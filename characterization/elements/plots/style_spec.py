"""Centralized plot style spec for characterization plots."""

from __future__ import annotations


BAND_ALPHA = 0.20
MEAN_LINESTYLE = "--"
DEFAULT_MARKER = "."
DEFAULT_LINESTYLE = "-"


# Same metric always uses the same color/marker/line style.
METRIC_STYLES: dict[str, dict[str, str]] = {
    "ref_pd_mean": {"color": "#036358", "marker": DEFAULT_MARKER, "linestyle": DEFAULT_LINESTYLE},
    "mean_adc": {"color": "#4B0082", "marker": DEFAULT_MARKER, "linestyle": DEFAULT_LINESTYLE},
    "temperature": {"color": "#256AB9", "marker": DEFAULT_MARKER, "linestyle": DEFAULT_LINESTYLE},
    "RH": {"color": "#8A6E00", "marker": DEFAULT_MARKER, "linestyle": DEFAULT_LINESTYLE},
    "laser_sp_1064": {"color": "#A03333", "marker": DEFAULT_MARKER, "linestyle": DEFAULT_LINESTYLE},
    "laser_sp_532": {"color": "#008B19", "marker": DEFAULT_MARKER, "linestyle": DEFAULT_LINESTYLE},
    "linreg_slope": {"color": "#6A4C93", "marker": DEFAULT_MARKER, "linestyle": DEFAULT_LINESTYLE},
    "linreg_intercept": {"color": "#F4A261", "marker": DEFAULT_MARKER, "linestyle": DEFAULT_LINESTYLE},
    "linreg_r_value": {"color": "#2A9D8F", "marker": 's', "linestyle": DEFAULT_LINESTYLE},
    "linreg_p_value": {"color": "#8E9AAF", "marker": 'o', "linestyle": DEFAULT_LINESTYLE},
    "power_slope": {"color": "#1D3557", "marker": DEFAULT_MARKER, "linestyle": DEFAULT_LINESTYLE},
    "power_intercept": {"color": "#3A86FF", "marker": DEFAULT_MARKER, "linestyle": DEFAULT_LINESTYLE},
    "power_slope_err": {"color": "#2A9D8F", "marker": DEFAULT_MARKER, "linestyle": DEFAULT_LINESTYLE},
    "power_intercept_err": {"color": "#7B2CBF", "marker": DEFAULT_MARKER, "linestyle": DEFAULT_LINESTYLE},
    "saturation_points": {"color": "#0E6157", "marker": DEFAULT_MARKER, "linestyle": DEFAULT_LINESTYLE},
    "fit_line": {"color": "#864B77", "marker": DEFAULT_MARKER, "linestyle": DEFAULT_LINESTYLE},
    "linreg_region": {"color": "#2F4858", "marker": DEFAULT_MARKER, "linestyle": DEFAULT_LINESTYLE},
    "saturation_region": {"color": "#5E548E", "marker": DEFAULT_MARKER, "linestyle": DEFAULT_LINESTYLE},
}


def metric_style(metric: str) -> dict[str, str]:
    if metric not in METRIC_STYLES:
        raise KeyError(f"Unknown plot metric style '{metric}'")
    return METRIC_STYLES[metric]
