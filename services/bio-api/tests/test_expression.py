from app.expression import analyze_expression_csv


def test_expression_rank():
    csv = b"gene,s1,s2,s3\nTP53,1,2,5\nEGFR,3,3,3\nBRCA1,1,8,2\n"
    result = analyze_expression_csv(csv, top_n=2)
    assert result["genes"] == 3
    assert len(result["candidate_biomarkers"]) == 2
