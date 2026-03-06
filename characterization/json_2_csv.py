import argparse
import csv
import json
from pathlib import Path

try:
    from characterization.config import config
except ModuleNotFoundError:  # pragma: no cover - direct script execution fallback
    from config import config


CSV_COLUMNS = [
    "wavelength",
    "gain",
    "photodiode_id",
    "v_slope",
    "v_intercept",
    "power_slope",
    "power_intercept",
]


def _sensor_sort_key(sensor_id: str):
    try:
        return float(sensor_id)
    except ValueError:
        return sensor_id


def _wavelength_sort_key(wavelength: str):
    try:
        return float(wavelength)
    except ValueError:
        return wavelength


def _build_rows(payload: dict) -> list[dict]:
    photodiodes = payload.get("photodiodes", {}) or {}
    rows: list[dict] = []

    for photodiode_id in sorted(photodiodes.keys(), key=_sensor_sort_key):
        gain = str(config.sensor_config.get(photodiode_id, {}).get("gain", "UNK"))
        per_wavelength = photodiodes.get(photodiode_id, {}) or {}
        for wavelength in sorted(per_wavelength.keys(), key=_wavelength_sort_key):
            node = per_wavelength.get(wavelength, {}) or {}
            adc_to_vref = node.get("adc_to_vrefV", {}) or {}
            adc_to_power = node.get("adc_to_power", {}) or {}

            rows.append(
                {
                    "wavelength": wavelength,
                    "gain": gain,
                    "photodiode_id": photodiode_id,
                    "v_slope": adc_to_vref.get("slope"),
                    "v_intercept": adc_to_vref.get("intercept"),
                    "power_slope": adc_to_power.get("slope"),
                    "power_intercept": adc_to_power.get("intercept"),
                }
            )

    return rows


def convert_json_to_csv(json_path: str | Path, output_path: str | Path | None = None) -> Path:
    input_path = Path(json_path)
    if not input_path.is_file():
        raise FileNotFoundError(f"Input JSON file does not exist: {input_path}")

    csv_path = Path(output_path) if output_path else input_path.with_suffix(".csv")

    with input_path.open("r", encoding="utf-8") as f:
        payload = json.load(f)

    rows = _build_rows(payload)

    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    return csv_path


def main():
    parser = argparse.ArgumentParser(
        description="Convert simplified characterization JSON to CSV."
    )
    parser.add_argument("json_path", help="Path to simplified characterization JSON file")
    parser.add_argument(
        "--output",
        "-o",
        help="Output CSV path (default: same path as input with .csv extension)",
    )
    args = parser.parse_args()

    try:
        out = convert_json_to_csv(args.json_path, args.output)
    except FileNotFoundError as exc:
        parser.error(str(exc))
    print(f"CSV written to: {out}")


if __name__ == "__main__":
    main()
