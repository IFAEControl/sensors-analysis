from dataclasses import dataclass


class CalibLinReg:
    """Holds the result of a calibration linear regression"""
    def __init__(self, x_var:str, y_var:str, linreg):
        self.x_var = x_var
        self.y_var = y_var
        self.linreg = linreg
    
    @property
    def slope(self):
        """Return the slope of the linear regression"""
        if self.linreg:
            return self.linreg.slope
        raise AttributeError("No linear regression result available")
    @property
    def intercept(self):
        """Return the intercept of the linear regression"""
        if self.linreg:
            return self.linreg.intercept
        raise AttributeError("No linear regression result available")
    @property
    def r_value(self):
        """Return the r_value of the linear regression"""
        if self.linreg:
            return self.linreg.rvalue
        raise AttributeError("No linear regression result available")
    @property
    def p_value(self):
        """Return the p_value of the linear regression"""
        if self.linreg:
            return self.linreg.pvalue
        raise AttributeError("No linear regression result available")
    @property
    def stderr(self):
        """Return the standard error of the linear regression"""
        if self.linreg:
            return self.linreg.stderr
        raise AttributeError("No linear regression result available")
    @property
    def intercept_stderr(self):
        """Return the intercept standard error of the linear regression"""
        if self.linreg:
            return self.linreg.intercept_stderr
        raise AttributeError("No linear regression result available")
    
    def to_dict(self):
        """Convert the linear regression result to a dictionary"""
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
        raise AttributeError("No linear regression result available")

@dataclass
class CalibFitResult:
    x_var: str
    y_var: str
    slope: float
    intercept: float
    r_value: float
    p_value: float
    stderr: float
    intercept_stderr: float
    weighted: bool = False
    slope_chi2: float = 0.0
    intercept_chi2: float = 0.0
    slope_chi2_reduced: float = 0.0
    intercept_chi2_reduced: float = 0.0
    ndof: int = 0

    def to_dict(self) -> dict:
        """Convert the calibration fit result to a dictionary"""
        result = {
            'x_var': self.x_var,
            'y_var': self.y_var,
            'slope': self.slope,
            'intercept': self.intercept,
            'r_value': self.r_value,
            'p_value': self.p_value,
            'stderr': self.stderr,
            'intercept_stderr': self.intercept_stderr,
        }
        if self.weighted:
            result.update({
                'weighted': self.weighted,
                'slope_chi2': self.slope_chi2,
                'intercept_chi2': self.intercept_chi2,
                'slope_chi2_reduced': self.slope_chi2_reduced,
                'intercept_chi2_reduced': self.intercept_chi2_reduced,
                'ndof': self.ndof,
            })
        return result


@dataclass
class MeanStats:
    """Holds mean statistics"""
    mean: float
    std: float
    samples: int
    weighted: bool = False
    w_mean: float = 0.0 # Weighted mean
    w_stderr: float = 0.0 # Weighted standard error
    ndof: int = 0
    chi2: float = 0.0
    chi2_reduced: float = 0.0
    exec_error: bool = False # whether the weight could be calculated or not (ie std >0)

    def to_dict(self) -> dict:
        """Convert the mean statistics to a dictionary"""
        if self.weighted:
            return {
                'mean': self.mean,
                'std': self.std,
                'weighted': self.weighted,
                'ndof': self.ndof,
                'chi2': self.chi2,
                'chi2_reduced': self.chi2_reduced,
                'exec_error': self.exec_error,
            }
        return {
                'mean': self.mean,
                'std': self.std,
            }

@dataclass
class PedestalStats:
    """Holds pedestal statistics"""
    pm:MeanStats
    refpd:MeanStats

    def to_dict(self) -> dict:
        """Convert the pedestal statistics to a dictionary"""
        return {
            'pm': self.pm.to_dict(),
            'refpd': self.refpd.to_dict(),
        }

@dataclass
class SanityCheckResult:
    """Result of a sanity check operation."""
    severity: str
    check_name: str
    check_args: dict|float|int|str|list|None
    passed: bool
    info: str = "" # optional additional information about the result for report generation
    exec_error: bool = False # If true, there was an error during the execution of the check
    internal: bool = False # whether the check was generated internally by the code or it comes from the configuration
    check_explanation: str = "" # optional explanation of the check purpose

    def to_dict(self) -> dict:
        """Convert the sanity check result to a dictionary."""
        return {
            'check_name': str(self.check_name),
            'check_args': str(self.check_args),
            'passed': bool(self.passed),
            'info': self.info,
            'severity': str(self.severity),
            'exec_error': bool(self.exec_error),
            'internal': bool(self.internal),
            'check_explanation': str(self.check_explanation),
        }