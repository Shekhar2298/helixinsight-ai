from app.ml import train_and_rank


def test_train_and_rank_is_reproducible():
    X = [[0, 0], [0, 1], [1, 0], [1, 1], [2, 1], [2, 2], [3, 2], [3, 3]]
    y = [0, 0, 0, 0, 1, 1, 1, 1]
    r1 = train_and_rank(X, y, ["GENE_A", "GENE_B"], epochs=10)
    r2 = train_and_rank(X, y, ["GENE_A", "GENE_B"], epochs=10)
    assert r1["model_fingerprint"] == r2["model_fingerprint"]
    assert r1["candidate_biomarkers"] == r2["candidate_biomarkers"]
