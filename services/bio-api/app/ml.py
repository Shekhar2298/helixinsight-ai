from __future__ import annotations
import hashlib
import numpy as np
import torch
from torch import nn


class BiomarkerNet(nn.Module):
    def __init__(self, n_features: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_features, max(8, min(64, n_features * 2))),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(max(8, min(64, n_features * 2)), 1),
        )

    def forward(self, x):
        return self.net(x).squeeze(-1)


def train_and_rank(X: list[list[float]], y: list[int], feature_names: list[str], epochs: int = 80) -> dict:
    if len(X) != len(y) or len(X) < 6:
        raise ValueError("Need at least 6 labeled samples and matching labels")
    if not feature_names or any(len(row) != len(feature_names) for row in X):
        raise ValueError("Feature dimensions do not match feature_names")

    torch.manual_seed(42)
    np.random.seed(42)
    x = torch.tensor(np.asarray(X), dtype=torch.float32)
    labels = torch.tensor(np.asarray(y), dtype=torch.float32)
    mean = x.mean(dim=0)
    std = x.std(dim=0).clamp_min(1e-6)
    xz = (x - mean) / std

    model = BiomarkerNet(x.shape[1])
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01, weight_decay=1e-4)
    loss_fn = nn.BCEWithLogitsLoss()
    model.train()
    for _ in range(epochs):
        optimizer.zero_grad()
        logits = model(xz)
        loss = loss_fn(logits, labels)
        loss.backward()
        optimizer.step()

    # Permutation importance on training loss: reproducible demo ranking, not clinical validation.
    model.eval()
    with torch.no_grad():
        baseline = float(loss_fn(model(xz), labels))
        importances = []
        for idx, name in enumerate(feature_names):
            permuted = xz.clone()
            order = torch.arange(xz.shape[0] - 1, -1, -1)
            permuted[:, idx] = permuted[order, idx]
            changed = float(loss_fn(model(permuted), labels))
            importances.append((name, max(0.0, changed - baseline)))

    ranked = sorted(importances, key=lambda p: p[1], reverse=True)
    fingerprint = hashlib.sha256((str(feature_names) + str(len(X)) + "seed=42").encode()).hexdigest()[:16]
    return {
        "model": "BiomarkerNet-demo",
        "seed": 42,
        "training_samples": len(X),
        "baseline_training_loss": round(baseline, 6),
        "model_fingerprint": fingerprint,
        "candidate_biomarkers": [{"feature": n, "permutation_importance": round(v, 6)} for n, v in ranked],
        "warning": "Demo candidate ranking only; requires held-out validation, external cohorts, and domain review.",
    }
