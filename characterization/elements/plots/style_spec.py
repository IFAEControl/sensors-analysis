"""Centralized plot style spec for characterization plots."""

from __future__ import annotations


BAND_ALPHA = 0.20
MEAN_LINESTYLE = "--"
DEFAULT_MARKER = "."
DEFAULT_LINESTYLE = "-"


# Same metric always uses the same color/marker/line style.
METRIC_STYLES: dict[str, dict[str, str]] = {
    "ref_pd_mean": {"color": "#009684", "marker": DEFAULT_MARKER, "linestyle": DEFAULT_LINESTYLE},
    "mean_adc": {"color": "#912FD7", "marker": DEFAULT_MARKER, "linestyle": DEFAULT_LINESTYLE},
    "temperature": {"color": "#4187D6", "marker": DEFAULT_MARKER, "linestyle": DEFAULT_LINESTYLE},
    "RH": {"color": "#D5B226", "marker": DEFAULT_MARKER, "linestyle": DEFAULT_LINESTYLE},
    "laser_sp_1064": {"color": "#BD1212", "marker": DEFAULT_MARKER, "linestyle": DEFAULT_LINESTYLE},
    "laser_sp_532": {"color": "#37B04D", "marker": DEFAULT_MARKER, "linestyle": DEFAULT_LINESTYLE},
    "linreg_slope": {"color": "#8760BE", "marker": DEFAULT_MARKER, "linestyle": DEFAULT_LINESTYLE},
    "linreg_intercept": {"color": "#F4A261", "marker": DEFAULT_MARKER, "linestyle": DEFAULT_LINESTYLE},
    "linreg_r_value": {"color": "#2A9D8F", "marker": DEFAULT_MARKER, "linestyle": DEFAULT_LINESTYLE},
    "linreg_p_value": {"color": "#5087E7", "marker": DEFAULT_MARKER, "linestyle": DEFAULT_LINESTYLE},
    "power_slope": {"color": "#0B65E3", "marker": DEFAULT_MARKER, "linestyle": DEFAULT_LINESTYLE},
    "power_intercept": {"color": "#697D9E", "marker": DEFAULT_MARKER, "linestyle": DEFAULT_LINESTYLE},
    "power_slope_err": {"color": "#2A9D8F", "marker": DEFAULT_MARKER, "linestyle": DEFAULT_LINESTYLE},
    "power_intercept_err": {"color": "#7B2CBF", "marker": DEFAULT_MARKER, "linestyle": DEFAULT_LINESTYLE},
    "saturation_points": {"color": "#1B8276", "marker": DEFAULT_MARKER, "linestyle": DEFAULT_LINESTYLE},
    "fit_line": {"color": "#CE47AC", "marker": DEFAULT_MARKER, "linestyle": DEFAULT_LINESTYLE},
    "linreg_region": {"color": "#CFF5DEFF", "marker": DEFAULT_MARKER, "linestyle": DEFAULT_LINESTYLE},
    "saturation_region": {"color": "#F1C1C1FF", "marker": DEFAULT_MARKER, "linestyle": DEFAULT_LINESTYLE},
    "filter_fw4": {"color": "#289FB7", "marker": DEFAULT_MARKER, "linestyle": DEFAULT_LINESTYLE},
    "filter_fw5": {"color": "#3A86FF", "marker": DEFAULT_MARKER, "linestyle": DEFAULT_LINESTYLE},
}


def metric_style(metric: str) -> dict[str, str]:
    if metric not in METRIC_STYLES:
        raise KeyError(f"Unknown plot metric style '{metric}'")
    return METRIC_STYLES[metric]
