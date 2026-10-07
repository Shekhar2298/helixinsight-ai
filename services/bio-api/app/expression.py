from __future__ import annotations
import io
import numpy as np
import pandas as pd


def analyze_expression_csv(data: bytes, top_n: int = 20) -> dict:
    df = pd.read_csv(io.BytesIO(data), index_col=0)
    if df.empty or df.shape[1] < 2:
        raise ValueError("Expression CSV must contain genes as rows and at least two sample columns")
    numeric = df.apply(pd.to_numeric, errors="coerce").dropna(axis=0, how="all").fillna(0.0)
    log = np.log1p(numeric.clip(lower=0))
    variances = log.var(axis=1).sort_values(ascending=False)
    top = variances.head(top_n)
    return {
        "genes": int(numeric.shape[0]),
        "samples": int(numeric.shape[1]),
        "normalization": "log1p",
        "ranking_method": "variance_across_samples_demo",
        "candidate_biomarkers": [
            {"gene": str(gene), "score": round(float(score), 6)} for gene, score in top.items()
        ],
        "warning": "Variance ranking is exploratory and is not evidence of disease association.",
    }


def differential_expression(data: bytes, labels: dict[str, str], top_n: int = 20) -> dict:
    df = pd.read_csv(io.BytesIO(data), index_col=0).apply(pd.to_numeric, errors="coerce").fillna(0.0)
    groups = sorted(set(labels.values()))
    if len(groups) != 2:
        raise ValueError("Exactly two cohort labels are required")
    cols_a = [c for c in df.columns if labels.get(c) == groups[0]]
    cols_b = [c for c in df.columns if labels.get(c) == groups[1]]
    if not cols_a or not cols_b:
        raise ValueError("Both cohorts must map to expression columns")
    log = np.log1p(df.clip(lower=0))
    effect = log[cols_b].mean(axis=1) - log[cols_a].mean(axis=1)
    ranked = effect.abs().sort_values(ascending=False).head(top_n)
    return {
        "comparison": f"{groups[1]} vs {groups[0]}",
        "candidate_biomarkers": [
            {"gene": str(g), "log_effect": round(float(effect.loc[g]), 6), "abs_effect": round(float(v), 6)}
            for g, v in ranked.items()
        ],
        "warning": "Exploratory effect-size ranking; statistical validation and multiple-testing correction are required.",
    }
