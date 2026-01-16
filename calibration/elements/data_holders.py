
class CalibLinReg:
    def __init__(self, x_var:str, y_var:str, linreg):
        self.x_var = x_var
        self.y_var = y_var
        self.linreg = linreg
    
    @property
    def slope(self):
        if self.linreg:
            return self.linreg.slope
    @property
    def intercept(self):
        if self.linreg:
            return self.linreg.intercept
    @property
    def r_value(self):
        if self.linreg:
            return self.linreg.rvalue
    @property
    def p_value(self):
        if self.linreg:
            return self.linreg.pvalue
    @property
    def stderr(self):
        if self.linreg:
            return self.linreg.stderr
    @property
    def intercept_stderr(self):
        if self.linreg:
            return self.linreg.intercept_stderr
    
    def to_dict(self):
        if self.linreg:
            return {
                'x_var': self.x_var,
                'y_var': self.y_var,
                'slope': self.slope,
                'intercept': self.intercept,
                'r_value': self.r_value,
                'p_value': self.p_value,
                'stderr': self.stderr,
                'intercept_stderr': self.intercept_stderr,
            }
        else:
            return {}
    