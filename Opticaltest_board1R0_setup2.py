import pandas as pd
import matplotlib.pyplot as plt
import os
from scipy.stats import linregress 
import numpy as np
import math
import matplotlib.ticker as ticker

# General variables: 
lowLevel_plot = True 
highLevel_plot = True
verbose = False

# First method for finding the saturation value. Compares i with i+1 at a certain level in %
def find_saturation_value(column_data):
    for i in range(len(column_data) - 1):
        if abs(column_data.iloc[i] - column_data.iloc[i + 1]) <= 0.01 * abs(column_data.iloc[i]):
            saturation = column_data.iloc[i]
            break
        else:
            saturation = None
    return saturation
def find_saturation_from_derivate(T):
        # Extract x and y values
        x = T['meanRefPD'].values
        y = T['meanADC'].values

        # Compute the first derivative using central differences
        dy_dx = np.gradient(y, x)

        # Add the derivative to the DataFrame
        T['dy_dx'] = dy_dx

        # Define a threshold for identifying the plateau
        threshold = 10  # Example threshold, adjust based on your data

        # Identify indices where dy_dx is not flat
        non_flat_indices = np.where(np.abs(dy_dx) >= threshold)[0]
        flat_indices = np.where(np.abs(dy_dx) < threshold)[0]
        if flat_indices.size > 0:
                first_flat_index = flat_indices[0]
                satADC=y[first_flat_index]
                #print(first_flat_index)
        else:
                #print("No flat indices found.")
                satADC=-1
        # Extract the corresponding rows
        T_non_flat = T.iloc[non_flat_indices]
        return T_non_flat, satADC
def ADC_analysis(folder_path,dataset_number,output_path,output_path_lowlevel,datetest,boardname):

    outputpath=f"{output_path}{dataset_number}"
    outputpath_lowlevel=f"{output_path_lowlevel}{dataset_number}"

    sensorsID=['0.0','0.1','0.2','0.3','1.0','1.1','1.2','1.3','2.0','2.1','2.2','2.3','3.0','3.1','3.2','3.3','4.0','4.1','4.2','4.3']
    wavelength= ['1064','532']
    
    if not os.path.exists(outputpath_lowlevel):
        os.makedirs(outputpath_lowlevel)
        os.makedirs(outputpath)
        print(f"Directory '{outputpath_lowlevel}' created.")

    if not os.path.exists(outputpath):
        os.makedirs(outputpath)
        print(f"Directory '{outputpath}' created.")

    for wl in wavelength:
        slopes = []
        intercepts= []
        rCoes = []
        stderr = []
        intercepts_stderr = []
        saturationADCs = []

        if wl== '532':
        # Rename DataFrame columns
            strg_L = 'Laser Current (mA)'
            temp = '20'
        elif wl == '1064':
            strg_L = 'Laser Power (mW)'
            temp = '25'

        for l in sensorsID:
            sensorID=l
            filename = f'{folder_path}/{datetest}_{boardname}_{sensorID}_{wl}_{dataset_number}.txt'
            T = pd.read_csv(filename,delimiter ='\t',header=None)
            T.columns = ['Date-Hour', 'L', 'TotalSum', 'TotalSquareSum', 'meanRefPD', 'stdRefPD', 'Tem', 'RH', 'TotalCounts']

            meanADC=T['TotalSum']/T['TotalCounts']
            stdADC=np.sqrt((T['TotalSquareSum']-T['TotalCounts']*meanADC**2)/(T['TotalCounts']-1))
            
            meanPM=meanADC*0.61e-3 #0.61mV/ADCcount   #this conversion should be done in W not in V might check this one
            stdPM=stdADC*0.61e-3

            #meanPM=4.6e-6*meanADC/0.61e-3 #0.61mV/ADCcount   #this conversion might be incorrect
            #stdPM=stdADC*4.6e-6/0.61e-3

            T['meanADC']=meanADC
            T['stdADC']=stdADC

            T['meanPM']=meanPM
            T['stdPM']=stdPM
            
            # Identify pedestal and remove the row
            Tpedestal=T[(T['L']== 0)]
            T = T.drop(T[(T['L']== 0)].index)
            
            # Find the ADC count saturation value
            # First method (doesnt work always): 
            #ADCthreshold = find_saturation_value(T['meanADC'])

            T, saturationADC= find_saturation_from_derivate(T)

            res = linregress(T['meanRefPD'], T['meanADC'])
            slope = res.slope 
            intercept = res.intercept
            r=res.rvalue
            se = res.stderr
            intercept_stderr = res.intercept_stderr

            slopes.append(slope)
            intercepts.append(intercept)
            rCoes.append(r)
            stderr.append(se)
            intercepts_stderr.append(intercept_stderr)
            saturationADCs.append(saturationADC)
            if(verbose):
                print(f'Calibration coefficient found for sensorID {sensorID} for laser {wl} nm = {res.slope} +/- {res.stderr} in ADC/V')

            if(lowLevel_plot):
                fig = plt.figure(2)
                plt.errorbar(T['L'], T['meanADC'], yerr=T['stdADC'], fmt='.', markersize=10, linewidth=1)
                plt.ylabel('mean ADC counts')
                plt.xlabel(strg_L)
                plt.grid()
                plt.title(f'Plot dataset {dataset_number}, sensorID {sensorID}, wavelength {wl} nm')
                plt.tight_layout()
                plt.savefig(f'{outputpath_lowlevel}/{datetest}_{boardname}_{sensorID}_{wl}_meanADC_L_{dataset_number}.png',dpi=199)  # Display the current figure
                plt.close(fig)



                fig = plt.figure(4)
                plt.errorbar(T['L'], T['meanRefPD'], yerr=T['stdRefPD'], fmt='.', markersize=10, linewidth=1)
                plt.ylabel('Mean ref PD (V)')
                plt.xlabel(strg_L)
                plt.grid()
                plt.title(f'Plot dataset {dataset_number}, sensorID {sensorID}, wavelength {wl} nm')
                plt.tight_layout()
                plt.savefig(f'{outputpath_lowlevel}/{datetest}_{boardname}_{sensorID}_{wl}_meanRefPD_L_{dataset_number}.png',dpi=199)  # Display the current figure
                #plt.show()
                plt.close(fig)

                #the label here are incorrect since meanPM=meanADC*0.61e-3 #0.61mV/ADCcoun. Monica proposed from the baffle paper: 
                #Voltage/ADCcount =3.3V/2**10=0.00322 V/ADCcount
                #4.6 uW/ADCcount*1ADCcount/0.00322V = 1428 uW/V


                fig = plt.figure(6)
                plt.errorbar(T['meanRefPD'], T['meanADC'], yerr=T['stdADC'], fmt='.', markersize=10, linewidth=1)
                plt.plot(T['meanRefPD'], intercept + slope*T['meanRefPD'], 'r', label='fitted line')
                plt.ylabel('Mean ADC counts')
                plt.xlabel('Mean ref PD (V)')
                plt.grid()
                plt.title(f'Plot dataset {dataset_number}, sensorID {sensorID}, wavelength {wl} nm')
                plt.tight_layout()
                plt.savefig(f'{outputpath_lowlevel}/{datetest}_{boardname}_{sensorID}_{wl}_meanADC_meanRefPD_{dataset_number}.png',dpi=199)  # Display the current figure
                #plt.show()
                plt.close(fig)
            
        if(highLevel_plot):
                tabdata = pd.DataFrame()
                tabdata["sensorID"]=sensorsID
                tabdata["slope"]=slopes
                tabdata["intercept"]=intercepts
                tabdata["rCoe"]=rCoes
                tabdata["stderr"]=stderr
                tabdata["intercept_stderr"]=intercepts_stderr
                tabdata["saturationADC"] = saturationADCs
                
                # Customize the plot
                fig = plt.figure(100)
                plt.errorbar(range(len(slopes)), slopes,stderr, fmt='.', markersize=10, linewidth=1)
                plt.title(f'Sensors at {wl} nm')
                plt.xlabel('SensorID')
                plt.ylabel('ADC counts/V')
                #plt.xticks(range(len(slopes)), [f'{i+1}' for i in range(len(sensorsID))])  # Label the x-axis with dataset identifiers
                plt.xticks(np.arange(len(slopes)), sensorsID, rotation=20)
                #plt.legend()
                #plt.axhline(y=res.slope, color='red', linestyle='--', label='Horizontal Line at y=m_all')
                plt.axhline(y=np.mean(slopes), color='purple', linestyle='--', label='Horizontal Line at y=m_av')
                #plt.fill_between(range(-1,len(slopes)+1), (res.slope-res.stderr), (res.slope+res.stderr), color='red', alpha=0.3, label='Shaded Region')
                plt.fill_between(range(-1,len(slopes)+1), (np.mean(slopes)-np.std(slopes)), (np.mean(slopes)+np.std(slopes)), color='purple', alpha=0.2, label='Shaded Region')
                plt.text(min(range(len(slopes))), max(slopes), f'Mean value = {np.mean(slopes)}', fontsize=12, color='red')
                #plt.ylim([0.00064, 0.000665])
                plt.xlim([-1,len(sensorsID)])
                plt.grid()
                # Show the plot
                plt.savefig(f'{outputpath}/{datetest}_{boardname}_{wl}_calibration_{dataset_number}.png',dpi=199)  # Display the current figure
                plt.close()

                # Customize the plot
                fig = plt.figure(101)
                plt.errorbar(range(len(slopes)), slopes,stderr, fmt='.', markersize=10, linewidth=1)
                plt.title(f'Sensors at {wl} nm')
                plt.xlabel('SensorID')
                plt.ylabel('ADC counts/V')
                #plt.xticks(range(len(slopes)), [f'{i+1}' for i in range(len(sensorsID))])  # Label the x-axis with dataset identifiers
                plt.xticks(np.arange(len(slopes)), sensorsID, rotation=20)
                #plt.legend()
                #plt.axhline(y=res.slope, color='red', linestyle='--', label='Horizontal Line at y=m_all')
                #plt.axhline(y=np.mean(slopes[9:]), color='purple', linestyle='--', label='Horizontal Line at y=m_av')
                #plt.fill_between(range(-1,len(slopes)+1), (res.slope-res.stderr), (res.slope+res.stderr), color='red', alpha=0.3, label='Shaded Region')
                #plt.fill_between(range(-1,len(slopes)+1), (np.mean(slopes)-np.std(slopes)), (np.mean(slopes)+np.std(slopes)), color='purple', alpha=0.2, label='Shaded Region')
                #plt.ylim([0.00064, 0.000665])
                plt.xlim([-1,len(sensorsID)])
                plt.grid()
                # Show the plot
                plt.savefig(f'{outputpath}/{datetest}_{boardname}_{wl}_noshades_calibration_{dataset_number}.png',dpi=199)  # Display the current figure
                plt.close()

                # Customize the plot
                fig = plt.figure(200)
                plt.errorbar(range(len(stderr)), stderr, fmt='.', markersize=10, linewidth=1)
                plt.title(f'stderr fit for different sensors at {wl} nm')
                plt.xlabel('SensorID')
                plt.ylabel('ADC counts/V')
                #plt.xticks(range(len(slopes)), [f'{i+1}' for i in range(len(sensorsID))])  # Label the x-axis with dataset identifiers
                plt.xticks(np.arange(len(stderr)), sensorsID, rotation=20)
                #plt.legend()
                #plt.axhline(y=res.slope, color='red', linestyle='--', label='Horizontal Line at y=m_all')
                #plt.axhline(y=np.mean(slopes), color='purple', linestyle='--', label='Horizontal Line at y=m_av')
                #plt.fill_between(range(-1,len(slopes)+1), (res.slope-res.stderr), (res.slope+res.stderr), color='red', alpha=0.3, label='Shaded Region')
                #plt.fill_between(range(-1,len(slopes)+1), (np.mean(slopes)-np.std(slopes)), (np.mean(slopes)+np.std(slopes)), color='purple', alpha=0.2, label='Shaded Region')
                #plt.ylim([0.00064, 0.000665])
                plt.xlim([-1,len(sensorsID)])
                plt.grid()
                # Show the plot
                plt.savefig(f'{outputpath}/{datetest}_{boardname}_{wl}_noshades_stderrs_{dataset_number}.png',dpi=199)  # Display the current figure
                plt.close()
                
                fig = plt.figure(300)
                plt.errorbar(range(len(intercepts)), intercepts,intercepts_stderr, fmt='.', markersize=10, linewidth=1)
                plt.title(f'Intercepts for differet sensors at {wl} nm')
                plt.xlabel('SensorID')
                plt.ylabel('ADC counts')
                #plt.xticks(range(len(slopes)), [f'{i+1}' for i in range(len(sensorsID))])  # Label the x-axis with dataset identifiers
                plt.xticks(np.arange(len(intercepts)), sensorsID, rotation=20)
                #plt.legend()
                #plt.axhline(y=res.slope, color='red', linestyle='--', label='Horizontal Line at y=m_all')
                #plt.axhline(y=np.mean(slopes), color='purple', linestyle='--', label='Horizontal Line at y=m_av')
                #plt.fill_between(range(-1,len(slopes)+1), (res.slope-res.stderr), (res.slope+res.stderr), color='red', alpha=0.3, label='Shaded Region')
                #plt.fill_between(range(-1,len(slopes)+1), (np.mean(slopes)-np.std(slopes)), (np.mean(slopes)+np.std(slopes)), color='purple', alpha=0.2, label='Shaded Region')
                #plt.ylim([0.00064, 0.000665])
                plt.xlim([-1,len(sensorsID)])
                plt.grid()
                # Show the plot
                plt.savefig(f'{outputpath}/{datetest}_{boardname}_{wl}_noshade_intercepts_{dataset_number}.png',dpi=199)  # Display the current figure
                plt.close()
                
                fig = plt.figure(400)
                plt.errorbar(range(len(rCoes)), rCoes, fmt='.', markersize=10, linewidth=1)
                plt.title(f'rCoes for differet sensors at {wl} nm')
                plt.xlabel('SensorID')
                plt.ylabel('')
                #plt.xticks(range(len(slopes)), [f'{i+1}' for i in range(len(sensorsID))])  # Label the x-axis with dataset identifiers
                plt.xticks(np.arange(len(rCoes)), sensorsID, rotation=20)
                #plt.legend()
                #plt.axhline(y=res.slope, color='red', linestyle='--', label='Horizontal Line at y=m_all')
                #plt.axhline(y=np.mean(slopes), color='purple', linestyle='--', label='Horizontal Line at y=m_av')
                #plt.fill_between(range(-1,len(slopes)+1), (res.slope-res.stderr), (res.slope+res.stderr), color='red', alpha=0.3, label='Shaded Region')
                #plt.fill_between(range(-1,len(slopes)+1), (np.mean(slopes)-np.std(slopes)), (np.mean(slopes)+np.std(slopes)), color='purple', alpha=0.2, label='Shaded Region')
                #plt.ylim([0.9997, 1.00001])
                #plt.xaxis.set_major_formatter(ticker.FormatStrFormatter('%0.1f'))
                plt.xlim([-1,len(sensorsID)])
                plt.grid()
                # Show the plot
                plt.savefig(f'{outputpath}/{datetest}_{boardname}_{wl}_noshade_rcoes_{dataset_number}.png',dpi=199)  # Display the current figure
                plt.close()
                
                fig = plt.figure(500)
                plt.title(f'Saturation ADC for differet sensors at {wl} nm')
                plt.plot(range(len(saturationADCs)), saturationADCs,'.')
                plt.xlabel('SensorID')
                plt.ylabel('')
                plt.xticks(np.arange(len(saturationADCs)), sensorsID, rotation=20)
                #plt.legend()
                #plt.axhline(y=res.slope, color='red', linestyle='--', label='Horizontal Line at y=m_all')
                #plt.axhline(y=np.mean(slopes), color='purple', linestyle='--', label='Horizontal Line at y=m_av')
                #plt.fill_between(range(-1,len(slopes)+1), (res.slope-res.stderr), (res.slope+res.stderr), color='red', alpha=0.3, label='Shaded Region')
                #plt.fill_between(range(-1,len(slopes)+1), (np.mean(slopes)-np.std(slopes)), (np.mean(slopes)+np.std(slopes)), color='purple', alpha=0.2, label='Shaded Region')
                #plt.ylim([0.9997, 1.00001])
                #plt.xaxis.set_major_formatter(ticker.FormatStrFormatter('%0.1f'))
                plt.xlim([-1,len(sensorsID)])
                plt.grid()
                # Show the plot
                plt.savefig(f'{outputpath}/{datetest}_{boardname}_{wl}_noshade_saturationADC_{dataset_number}.png',dpi=199)  # Display the current figure
                plt.close()

            #We separate the sensors according to whether they have gain or not 
                sensorsID1=sensorsID[:16]
                sensorsID2=sensorsID[-4:]
                slopes1=slopes[:16]
                slopes2=slopes[-4:]
                intercepts1=intercepts[:16]
                intercepts2=intercepts[-4:]
                rCoes1=rCoes[:16]
                rCoes2=rCoes[-4:]
                stderr1=stderr[:16]
                stderr2=stderr[-4:]
                intercepts_stderr1=intercepts_stderr[:16]
                intercepts_stderr2=intercepts_stderr[-4:]
                saturationADCs1=saturationADCs[:16]
                saturationADCs2=saturationADCs[-4:]

                #We calculate the gain and its error
                ringwog=[slopes[0],slopes[1],slopes[2],slopes[3],slopes[4],slopes[5],slopes[6],slopes[7],slopes[8],slopes[9],slopes[10],slopes[11],slopes[12],slopes[13],slopes[14],slopes[15]]
                ringwg=[slopes[16],slopes[17],slopes[18],slopes[19]]
                meanwog=sum(ringwog)/len(ringwog)
                meanwg=sum(ringwg)/len(ringwg)
                gain=meanwg/meanwog #fem la mitja dels sensors amb gain i ho dividim per la mitja dels sensors sense gain.
                deviationwog=((slopes[0]-meanwog)**2+(slopes[1]-meanwog)**2+(slopes[2]-meanwog)**2+(slopes[3]-meanwog)**2+(slopes[4]-meanwog)**2+(slopes[5]-meanwog)**2+(slopes[6]-meanwog)**2+(slopes[7]-meanwog)**2+(slopes[8]-meanwog)**2+(slopes[9]-meanwog)**2+(slopes[10]-meanwog)**2+(slopes[11]-meanwog)**2+(slopes[12]-meanwog)**2+(slopes[13]-meanwog)**2+(slopes[14]-meanwog)**2+(slopes[15]-meanwog)**2)/16
                deviationwg=((slopes[16]-meanwg)**2+(slopes[17]-meanwg)**2+(slopes[18]-meanwg)**2+(slopes[19]-meanwg)**2)/4
                gainerror=gain*math.sqrt(deviationwog/(meanwog**2)+deviationwg/(meanwg**2))

                print("gain",{wl},"=",gain)
                print("error",{wl},"=",gainerror)
                print(f'mean wog {wl}_{dataset_number}:',meanwog)
                print(f'error wog{wl}_{dataset_number}', math.sqrt(deviationwog))
                print(f'mean wg {wl}_{dataset_number}:',meanwg)
                print(f'error wg{wl}_{dataset_number}', math.sqrt(deviationwg))


                # Customize the plot
                fig = plt.figure(101)
                plt.errorbar(range(len(slopes1)),slopes1,stderr1,fmt='.',markersize=10,linewidth=1)
                plt.axhline(y=meanwog, color='r', linestyle='-', label='mean ADC/V')
                plt.title(f'Sensors at {wl} nm for dataset {dataset_number}')
                plt.xlabel('SensorID')
                plt.ylabel('ADC counts/V')
                plt.text(min(range(len(slopes1))), max(slopes1), f'Mean value = {np.mean(slopes1)}', fontsize=12, color='red')
                plt.xticks(np.arange(len(slopes1)), sensorsID1, rotation=20)
                plt.xlim([-1,len(sensorsID1)]) 
                plt.grid()
                # Show the plot
                plt.savefig(f'{outputpath}/{datetest}_{boardname}_{wl}_calibration_wogain_{dataset_number}.png',dpi=199)  # Display the current figure
                plt.close()
                
                # Customize the plot
                fig = plt.figure(200)
                plt.errorbar(range(len(stderr1)), stderr1, fmt='.', markersize=10, linewidth=1)
                plt.title(f'stderr fit for different sensors at {wl} nm for dataset {dataset_number}')
                plt.xlabel('SensorID')
                plt.ylabel('ADC counts/V')
                plt.xticks(np.arange(len(stderr1)), sensorsID1, rotation=20)
                plt.xlim([-1,len(sensorsID)])
                plt.grid()
                # Show the plot
                plt.savefig(f'{outputpath}/{datetest}_{boardname}_{wl}_noshades_stderrs_wogain_{dataset_number}.png',dpi=199)  # Display the current figure
                plt.close()

                # Customize the plot
                fig = plt.figure(102)
                plt.errorbar(range(len(slopes2)), slopes2,stderr2, fmt='.', markersize=10, linewidth=1)
                plt.axhline(y=meanwg, color='r', linestyle='-', label='mean ADC/V')
                plt.title(f'Sensors with gain at {wl} nm for dataset {dataset_number}')
                plt.xlabel('SensorID')
                plt.ylabel('ADC counts/V')
                plt.text(min(range(len(slopes2))), max(slopes2), f'Mean value = {np.mean(slopes2)}', fontsize=12, color='red')
                #plt.xticks(range(len(slopes)), [f'{i+1}' for i in range(len(sensorsID))])  # Label the x-axis with dataset identifiers
                plt.xticks(np.arange(len(slopes2)), sensorsID2, rotation=20)
                plt.xlim([-1,len(sensorsID2)]) 
                plt.grid()
                # Show the plot
                plt.savefig(f'{outputpath}/{datetest}_{boardname}_{wl}_calibration_wgain_{dataset_number}.png',dpi=199)  # Display the current figure
                plt.close()
                
                # Customize the plot
                fig = plt.figure(200)
                plt.errorbar(range(len(stderr2)), stderr2, fmt='.', markersize=10, linewidth=1)
                plt.title(f'stderr fit for different sensors with gain at {wl} nm for dataset {dataset_number}')
                plt.xlabel('SensorID')
                plt.ylabel('ADC counts/V')
                plt.xticks(np.arange(len(stderr2)), sensorsID2, rotation=20)
                plt.xlim([-1,len(sensorsID2)])
                plt.grid()
                # Show the plot
                plt.savefig(f'{outputpath}/{datetest}_{boardname}_{wl}_noshades_stderrs_wgain_{dataset_number}.png',dpi=199)  # Display the current figure
                plt.close()


    print('coeficients', f"{wl}",slopes)
    print('errors',f"{wl}",stderr)

ADC_analysis('./Useful_data/setup2/17092024_1R0/data',3,"./Plots/setup2/17092024/dataset","./Plots/setup2/17092024LowLevel/dataset",'17092024','1R0')