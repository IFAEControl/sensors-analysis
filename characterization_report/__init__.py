def build_report(*args, **kwargs):
    from .main import build_report as _build_report
    return _build_report(*args, **kwargs)

__all__ = ["build_report"]
