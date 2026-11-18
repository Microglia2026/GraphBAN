import argparse

import pandas as pd


def combine_predictions(bindingbd_path, biosnap_path, kiba_path):
    sources = [
        ("BindingBD", bindingbd_path),
        ("BioSNAP", biosnap_path),
        ("KIBA", kiba_path),
    ]
    key_columns = ["SMILES", "Protein"]
    frames = []

    for source, path in sources:
        frame = pd.read_csv(path)
        missing = set(key_columns + ["pred"]) - set(frame.columns)
        if missing:
            raise ValueError(f"{path} is missing required columns: {sorted(missing)}")
        frames.append((source, frame[key_columns + ["pred"]].copy()))

    base = frames[0][1][key_columns].reset_index(drop=True)
    combined = base.copy()
    prediction_columns = []
    for source, frame in frames:
        keys = frame[key_columns].reset_index(drop=True)
        if not keys.equals(base):
            raise ValueError(
                f"{source} rows do not match BindingBD by order and SMILES/Protein"
            )
        column = f"pred_{source}"
        combined[column] = pd.to_numeric(frame["pred"], errors="raise").reset_index(drop=True)
        prediction_columns.append(column)

    combined["pred_mean"] = combined[prediction_columns].mean(axis=1)
    return combined, prediction_columns


def merge_predictions(bindingbd_path, biosnap_path, kiba_path, threshold=0.5):
    combined, _ = combine_predictions(bindingbd_path, biosnap_path, kiba_path)
    return combined.loc[combined["pred_mean"].gt(threshold)]


def main():
    parser = argparse.ArgumentParser(
        description="Merge three GraphBAN prediction files and filter by score."
    )
    parser.add_argument("--bindingbd", required=True, help="BindingDB prediction CSV.")
    parser.add_argument("--biosnap", required=True, help="BioSNAP prediction CSV.")
    parser.add_argument("--kiba", required=True, help="KIBA prediction CSV.")
    parser.add_argument("--output", required=True, help="Output combined CSV.")
    parser.add_argument(
        "--unfiltered-output", help="Optional output CSV containing all predictions."
    )
    parser.add_argument(
        "--threshold", type=float, default=0.5, help="Keep a row if any score exceeds this value."
    )
    args = parser.parse_args()

    combined, _ = combine_predictions(args.bindingbd, args.biosnap, args.kiba)
    if args.unfiltered_output:
        combined.to_csv(args.unfiltered_output, index=False)
        print(f"Saved {len(combined)} rows to {args.unfiltered_output}")

    filtered = combined.loc[combined["pred_mean"].gt(args.threshold)]
    filtered.to_csv(args.output, index=False)
    print(f"Saved {len(filtered)} rows to {args.output}")


if __name__ == "__main__":
    main()
