#!/usr/bin/env python3
"""Add a UniProt protein sequence to a GraphBAN CSV input."""

import argparse
import csv
import re
import sys
from pathlib import Path
from urllib.error import URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


def fetch_protein_sequence(accession: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9_-]+", accession):
        raise ValueError(f"Invalid UniProt accession: {accession!r}")

    url = f"https://rest.uniprot.org/uniprotkb/{quote(accession, safe='')}.fasta"
    request = Request(url, headers={"User-Agent": "GraphBAN-preprocessing/1.0"})
    try:
        with urlopen(request, timeout=30) as response:
            fasta = response.read().decode("utf-8")
    except (URLError, TimeoutError) as exc:
        raise RuntimeError(f"Could not fetch UniProt FASTA for {accession}: {exc}") from exc

    header = None
    sequence_parts = []
    for line in fasta.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith(">"):
            if header is not None:
                raise ValueError(f"Expected one FASTA record for {accession}, got multiple")
            header = line[1:]
            if accession not in header.split()[0].split("|"):
                raise ValueError(f"UniProt FASTA header does not match {accession}: {header}")
        elif header is None:
            raise ValueError("Invalid FASTA response: sequence appears before header")
        else:
            sequence_parts.append("".join(line.split()))

    sequence = "".join(sequence_parts).upper()
    if header is None or not sequence or not re.fullmatch(r"[A-Z]+", sequence):
        raise ValueError(f"Invalid or empty protein sequence returned for {accession}")
    return sequence


def add_protein_column(input_path: Path, output_path: Path, sequence: str) -> int:
    if input_path.resolve() == output_path.resolve():
        raise ValueError("Input and output paths must be different")

    with input_path.open("r", encoding="utf-8-sig", newline="") as source:
        reader = csv.reader(source)
        header = next(reader, None)
        if not header:
            raise ValueError(f"Input CSV is empty: {input_path}")
        if "SMILES" not in header:
            raise ValueError(f"Input CSV must contain a 'SMILES' column; found: {header}")
        if "Protein" in header:
            raise ValueError("Input CSV already contains a 'Protein' column")

        rows = []
        for line_number, row in enumerate(reader, start=2):
            if len(row) != len(header):
                raise ValueError(
                    f"Malformed CSV row {line_number}: expected {len(header)} columns, "
                    f"found {len(row)}"
                )
            rows.append(row + [sequence])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="") as target:
        writer = csv.writer(target, lineterminator="\n")
        writer.writerow(header + ["Protein"])
        writer.writerows(rows)
    return len(rows)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fetch a UniProt protein sequence and add it to a GraphBAN CSV."
    )
    parser.add_argument("--input", required=True, type=Path, help="Source CSV")
    parser.add_argument("--output", required=True, type=Path, help="Output CSV")
    parser.add_argument("--accession", required=True, help="UniProt accession, e.g. Q16656")
    args = parser.parse_args()

    try:
        sequence = fetch_protein_sequence(args.accession)
        row_count = add_protein_column(args.input, args.output, sequence)
    except (OSError, RuntimeError, ValueError, csv.Error) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Protein sequence fetched: {args.accession} ({len(sequence)} amino acids)")
    print(f"Rows written: {row_count}")
    print(f"Output: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
