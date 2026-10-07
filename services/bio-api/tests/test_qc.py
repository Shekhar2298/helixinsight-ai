from app.qc import sequence_qc


def test_fastq_qc():
    data = b"@r1\nACGTACGT\n+\nIIIIIIII\n@r2\nGGGGNNNN\n+\nIIIIIIII\n"
    result = sequence_qc(data, "sample.fastq")
    assert result["records"] == 2
    assert result["total_bases"] == 16
    assert result["mean_phred_quality"] == 40.0
