from dataclasses import dataclass

class CharLinReg:
    """Holds the result of a linear regression"""
    def __init__(self, x_var: str, y_var: str, linreg):
        self.x_var = x_var
        self.y_var = y_var
        self.linreg = linreg

    @property
    def slope(self):
        if self.linreg:
            return self.linreg.slope
        raise AttributeError("No linear regression result available")

    @property
    def intercept(self):
        if self.linreg:
            return self.linreg.intercept
        raise AttributeError("No linear regression result available")

    @property
    def r_value(self):
        if self.linreg:
            return self.linreg.rvalue
        raise AttributeError("No linear regression result available")

    @property
    def p_value(self):
        if self.linreg:
            return self.linreg.pvalue
        raise AttributeError("No linear regression result available")

    @property
    def stderr(self):
        if self.linreg:
            return self.linreg.stderr
        raise AttributeError("No linear regression result available")

    @property
    def intercept_stderr(self):
        if self.linreg:
            return self.linreg.intercept_stderr
        raise AttributeError("No linear regression result available")

    def to_dict(self):
        if self.linreg:
            return {
                'x_var': self.x_var,
                'y_var': self.y_var,
                'slope': float(self.slope),
                'intercept': float(self.intercept),
                'r_value': float(self.r_value),
                'p_value': float(self.p_value),
                'stderr': float(self.stderr),
                'intercept_stderr': float(self.intercept_stderr),
            }
        raise AttributeError("No linear regression result available")

@dataclass
class MeanStats:
    mean: float
    std: float
    samples: int

    def to_dict(self) -> dict:
        return {
            'mean': self.mean,
            'std': self.std,
            'samples': self.samples,
        }

@dataclass
class GainStats:
    mean_without_gain: float
    mean_with_gain: float
    gain: float
    gain_error: float
    std_without_gain: float
    std_with_gain: float
    samples_without_gain: int
    samples_with_gain: int

    def to_dict(self) -> dict:
        return {
            'mean_without_gain': self.mean_without_gain,
            'mean_with_gain': self.mean_with_gain,
            'gain': self.gain,
            'gain_error': self.gain_error,
            'std_without_gain': self.std_without_gain,
            'std_with_gain': self.std_with_gain,
            'samples_without_gain': self.samples_without_gain,
            'samples_with_gain': self.samples_with_gain,
        }

@dataclass
class SanityCheckResult:
    severity: str
    check_name: str
    check_args: dict | float | int | str | list | None
    passed: bool
    info: str = ""
    exec_error: bool = False
    internal: bool = False
    check_explanation: str = ""

    def to_dict(self) -> dict:
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
