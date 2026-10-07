from app.variants import parse_vcf


def test_parse_vcf():
    data = b"##fileformat=VCFv4.2\n#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\n1\t12345\trs1\tA\tG\t99\tPASS\tDP=50\n"
    rows = parse_vcf(data)
    assert rows[0]["id"] == "rs1"
    assert rows[0]["pos"] == 12345
