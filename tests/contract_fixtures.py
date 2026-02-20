from __future__ import annotations


def make_valid_extended_payload(generate_plots: bool = True) -> dict:
    plots_node = {"photodiodes": {"0.0": {}}} if generate_plots else {}
    return {
        "meta": {
            "charact_id": "test_char",
            "config": {"generate_plots": generate_plots},
        },
        "analysis": {
            "photodiodes": {
                "0.0": {
                    "meta": {"sensor_id": "0.0"},
                    "time_info": {},
                    "analysis": {},
                    "filesets": {
                        "1064_FW5": {
                            "meta": {"wavelength": "1064", "filter_wheel": "FW5"},
                            "time_info": {},
                            "analysis": {},
                            "files": {
                                "0.0_1064nm_FW5_run1": {
                                    "file_info": {"filename": "dummy.txt"},
                                    "time_info": {},
                                    "analysis": {},
                                }
                            },
                            "plots": {},
                        }
                    },
                    "plots": {},
                }
            }
        },
        "time_info": {},
        "plots": plots_node,
        "sanity_checks": {
            "run_1": {
                "checks": {},
                "photodiodes": {
                    "0.0": {
                        "checks": {},
                        "filesets": {
                            "1064_FW5": {
                                "checks": {},
                                "sweepfiles": {"0.0_1064nm_FW5_run1": {}},
                            }
                        },
                    }
                },
            }
        },
    }


def make_valid_reduced_payload() -> dict:
    return {
        "characterization_id": "test_char",
        "acquisition_time": {},
        "calibration": {},
        "photodiodes": {"0.0": {}},
    }
