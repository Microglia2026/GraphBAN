import argparse
import csv
from pathlib import Path

from rdkit import Chem, RDLogger

RDLogger.DisableLog("rdApp.*")


def main():
    parser = argparse.ArgumentParser(description="预处理 GraphBAN 所需的 SMILES")
    parser.add_argument("-i", "--input", required=True, help="输入 CSV")
    parser.add_argument("-o", "--output", required=True, help="输出 CSV")
    parser.add_argument("--smiles-col", default="SMILES", help="输入中的 SMILES 列名")
    parser.add_argument("--report", required=True, help="无法使用的记录报告 CSV")
    parser.add_argument("--max-atoms", type=int, default=290, help="GraphBAN 原子数上限")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    report_path = Path(args.report)

    paths = [input_path.resolve(), output_path.resolve(), report_path.resolve()]
    if len(set(paths)) != 3:
        raise ValueError("输入、输出和报告文件必须使用不同路径")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    total = kept = excluded = 0

    with input_path.open("r", encoding="utf-8-sig", newline="") as src:
        reader = csv.reader(src)
        header = next(reader, None)

        if not header or args.smiles_col not in header:
            raise ValueError(f"找不到 SMILES 列 {args.smiles_col!r}；现有列：{header}")

        smiles_idx = header.index(args.smiles_col)
        output_header = header.copy()
        output_header[smiles_idx] = "SMILES"

        with (
            output_path.open("w", encoding="utf-8", newline="") as dst,
            report_path.open("w", encoding="utf-8", newline="") as report,
        ):
            writer = csv.writer(dst, lineterminator="\n")
            report_writer = csv.writer(report, lineterminator="\n")

            writer.writerow(output_header)
            report_writer.writerow(["source_row", "original_smiles", "reason"])

            for source_row, row in enumerate(reader, start=2):
                total += 1

                if smiles_idx >= len(row):
                    report_writer.writerow([source_row, "", "missing_smiles"])
                    excluded += 1
                    continue

                original = row[smiles_idx]
                smiles = original.strip().replace("\r", "").replace("\n", "")

                mol = Chem.MolFromSmiles(smiles) if smiles else None
                if mol is None:
                    report_writer.writerow([source_row, original, "invalid_smiles"])
                    excluded += 1
                    continue

                if mol.GetNumAtoms() > args.max_atoms:
                    report_writer.writerow([
                        source_row, original,
                        f"over_atom_limit:{mol.GetNumAtoms()}",
                    ])
                    excluded += 1
                    continue

                row[smiles_idx] = Chem.MolToSmiles(
                    mol, canonical=True, isomericSmiles=True
                )
                writer.writerow(row)
                kept += 1

    print(f"输入记录: {total}")
    print(f"保留记录: {kept}")
    print(f"排除记录: {excluded}")
    print(f"输出文件: {output_path}")
    print(f"排除报告: {report_path}")


if __name__ == "__main__":
    main()