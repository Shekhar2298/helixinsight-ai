from __future__ import annotations
import httpx
from .config import settings


def parse_vcf(data: bytes, limit: int = 1000) -> list[dict]:
    rows: list[dict] = []
    for raw in data.decode("utf-8", errors="strict").splitlines():
        if not raw or raw.startswith("#"):
            continue
        parts = raw.split("\t")
        if len(parts) < 8:
            continue
        chrom, pos, variant_id, ref, alt, qual, flt, info = parts[:8]
        rows.append({
            "chrom": chrom,
            "pos": int(pos),
            "id": variant_id,
            "ref": ref,
            "alt": alt,
            "qual": None if qual == "." else float(qual),
            "filter": flt,
            "info": info,
        })
        if len(rows) >= limit:
            break
    if not rows:
        raise ValueError("No VCF variants found")
    return rows


async def annotate_variant_id(variant_id: str, species: str = "human") -> dict:
    if not variant_id or variant_id == ".":
        return {"id": variant_id, "annotation": None, "source": None}
    url = f"{settings.ensembl_base_url}/vep/{species}/id/{variant_id}"
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(url, headers={"Accept": "application/json"})
        response.raise_for_status()
        payload = response.json()
    return {
        "id": variant_id,
        "annotation": payload,
        "source": url,
        "source_name": "Ensembl Variant Effect Predictor",
    }
