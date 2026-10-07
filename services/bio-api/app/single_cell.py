from __future__ import annotations
import os
import tempfile
import numpy as np
import scanpy as sc


def analyze_h5ad(data: bytes, top_n: int = 25) -> dict:
    with tempfile.NamedTemporaryFile(suffix=".h5ad", delete=False) as tmp:
        tmp.write(data)
        path = tmp.name
    try:
        adata = sc.read_h5ad(path)
        if adata.n_obs < 2 or adata.n_vars < 2:
            raise ValueError("h5ad must contain at least 2 cells and 2 genes")

        sc.pp.calculate_qc_metrics(adata, inplace=True, percent_top=None, log1p=False)
        initial_cells, initial_genes = int(adata.n_obs), int(adata.n_vars)

        min_genes = min(200, max(1, int(adata.n_vars * 0.01)))
        min_cells = min(3, max(1, int(adata.n_obs * 0.01)))
        sc.pp.filter_cells(adata, min_genes=min_genes)
        sc.pp.filter_genes(adata, min_cells=min_cells)
        if adata.n_obs < 2 or adata.n_vars < 2:
            raise ValueError("QC filtering removed too much data; adjust thresholds for this dataset")

        sc.pp.normalize_total(adata, target_sum=1e4)
        sc.pp.log1p(adata)
        n_top = min(max(2, top_n), adata.n_vars)
        sc.pp.highly_variable_genes(adata, n_top_genes=n_top, flavor="seurat")
        hv = adata.var[adata.var["highly_variable"]].copy()

        pca_dims = min(20, adata.n_obs - 1, adata.n_vars - 1)
        variance_ratio = []
        if pca_dims >= 2:
            sc.tl.pca(adata, n_comps=pca_dims, use_highly_variable=True)
            variance_ratio = [round(float(v), 6) for v in adata.uns["pca"]["variance_ratio"][:10]]

        genes = [str(g) for g in hv.index[:top_n]]
        mean_counts = float(np.asarray(adata.obs["total_counts"]).mean()) if "total_counts" in adata.obs else None
        return {
            "initial_cells": initial_cells,
            "initial_genes": initial_genes,
            "post_qc_cells": int(adata.n_obs),
            "post_qc_genes": int(adata.n_vars),
            "mean_total_counts_pre_normalization": round(mean_counts, 3) if mean_counts is not None else None,
            "normalization": "total-count 1e4 + log1p",
            "highly_variable_genes": genes,
            "pca_variance_ratio_top10": variance_ratio,
            "warning": "Exploratory single-cell QC/feature selection only; biological interpretation requires study-specific QC and validation.",
        }
    finally:
        os.unlink(path)
