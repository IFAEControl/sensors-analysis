
# Virgo Instrumented baffles optical setup sensors calibration and characterization analysis

## Calibration Module

To execute it without installing the package, use:
```bash
python -m calibration.main <path_to_calibration_zip_file> [--output_path <output_path>]
```

### Structure

 - Calibration
   - File Sets: groups of calibration files with same wavelength and filter wheel settings
     - Calibration Files: individual calibration data files

Each stage has its own analysis and plotting capabilities to facilitate detailed examination of calibration data at different levels of granularity. This modular approach allows for efficient organization and processing of calibration data, enabling users to derive meaningful insights from their measurements.

Output paths for plots and results are structured to reflect this hierarchy, ensuring clarity and ease of access to analysis outputs.

- **\<output_path> /**: Either set by user or calculated from the input file argument
    - **\<wavelength>\_<filter_wheel> /**: FileSet level
        - **\<wavelength>\_<filter_wheel>\_\<run> /** : CalibFile level
            - ***.png**: Plots and analysis results
            - **results.json**: Analysis results of the calibration file
        - ***.png**: Plots and analysis results of the file set (usually using means from run files)
        - **results.json**: Analysis results of the file set (contains aggregated results and all run files results in the hierarchy)
    - ***.png**: Plots and analysis results of the overall calibration (mostly environment of the whole data taking and some plot representing different filter wheels and/or wavelengths)
    - **results.json**: Analysis results of the overall calibration (contains aggregated results and all file sets results in the hierarchy)
