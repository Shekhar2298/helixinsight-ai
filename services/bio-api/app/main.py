from __future__ import annotations
from datetime import datetime
from fastapi import FastAPI, File, HTTPException, UploadFile
from sqlalchemy.exc import SQLAlchemyError
from .db import SessionLocal, init_db
from .expression import analyze_expression_csv
from .ml import train_and_rank
from .models import AnalysisRun
from .qc import sequence_qc
from .reporting import grounded_report
from .schemas import BiomarkerTrainingRequest, ReportRequest
from .single_cell import analyze_h5ad
from .storage import put_bytes
from .variants import annotate_variant_id, parse_vcf

app = FastAPI(
    title="HelixInsight Bioinformatics API",
    version="0.1.0",
    description="Research-only genomics/multi-omics analysis API; not for clinical decision-making.",
)


@app.on_event("startup")
def startup() -> None:
    init_db()


def save_run(kind: str, filename: str, result: dict, evidence: str | None = None) -> None:
    try:
        with SessionLocal() as db:
            db.add(AnalysisRun(kind=kind, filename=filename, result=result, evidence=evidence))
            db.commit()
    except SQLAlchemyError:
        # API result remains usable even when persistence is temporarily unavailable.
        return


@app.get("/health")
def health():
    return {"status": "ok", "service": "bio-api", "time": datetime.utcnow().isoformat() + "Z"}


@app.post("/v1/qc/sequence")
async def qc_sequence(file: UploadFile = File(...)):
    try:
        data = await file.read()
        result = sequence_qc(data, file.filename or "sequence.fasta")
        storage_uri = put_bytes(f"uploads/{file.filename}", data, file.content_type or "application/octet-stream")
        result["storage_uri"] = storage_uri
        save_run("sequence_qc", file.filename or "unknown", result)
        return result
    except (UnicodeDecodeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/v1/expression/analyze")
async def expression_analyze(file: UploadFile = File(...)):
    try:
        data = await file.read()
        result = analyze_expression_csv(data)
        save_run("expression", file.filename or "expression.csv", result)
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/v1/single-cell/analyze")
async def single_cell_analyze(file: UploadFile = File(...)):
    try:
        data = await file.read()
        result = analyze_h5ad(data)
        save_run("single_cell", file.filename or "dataset.h5ad", result)
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/v1/variants/analyze")
async def variants_analyze(file: UploadFile = File(...), annotate_first_ids: int = 3):
    try:
        data = await file.read()
        variants = parse_vcf(data)
        annotations = []
        evidence = []
        for variant in variants[:max(0, min(annotate_first_ids, 10))]:
            if variant["id"] != ".":
                try:
                    ann = await annotate_variant_id(variant["id"])
                    annotations.append(ann)
                    if ann.get("source"):
                        evidence.append({"name": f"Ensembl VEP {variant['id']}", "url": ann["source"]})
                except Exception as exc:
                    annotations.append({"id": variant["id"], "annotation": None, "error": type(exc).__name__})
        result = {"variant_count": len(variants), "variants": variants, "annotations": annotations, "evidence": evidence}
        save_run("variants", file.filename or "variants.vcf", result)
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/v1/biomarkers/train")
def biomarkers_train(request: BiomarkerTrainingRequest):
    try:
        result = train_and_rank(request.X, request.y, request.feature_names, request.epochs)
        save_run("biomarker_model", "inline_training_data", result)
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/v1/reports/generate")
async def reports_generate(request: ReportRequest):
    return await grounded_report(request.title, request.analysis, request.evidence)
