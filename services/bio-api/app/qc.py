from __future__ import annotations
import io
from statistics import mean
from Bio import SeqIO


def _gc_fraction(seq: str) -> float:
    seq = seq.upper()
    valid = [b for b in seq if b in "ACGT"]
    if not valid:
        return 0.0
    return (valid.count("G") + valid.count("C")) / len(valid)


def sequence_qc(data: bytes, filename: str) -> dict:
    name = filename.lower()
    fmt = "fastq" if name.endswith((".fastq", ".fq")) else "fasta"
    text = data.decode("utf-8", errors="strict")
    records = list(SeqIO.parse(io.StringIO(text), fmt))
    if not records:
        raise ValueError("No sequence records found")

    lengths = [len(r.seq) for r in records]
    gc_values = [_gc_fraction(str(r.seq)) for r in records]
    n_count = sum(str(r.seq).upper().count("N") for r in records)
    total_bases = sum(lengths)

    result = {
        "format": fmt,
        "records": len(records),
        "total_bases": total_bases,
        "mean_length": round(mean(lengths), 2),
        "min_length": min(lengths),
        "max_length": max(lengths),
        "mean_gc_fraction": round(mean(gc_values), 4),
        "ambiguous_n_fraction": round(n_count / total_bases, 6) if total_bases else 0.0,
    }

    if fmt == "fastq":
        qualities = [q for r in records for q in r.letter_annotations.get("phred_quality", [])]
        result["mean_phred_quality"] = round(mean(qualities), 2) if qualities else None
        result["q30_fraction"] = round(sum(q >= 30 for q in qualities) / len(qualities), 4) if qualities else None
    return result
