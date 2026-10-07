from pydantic import BaseModel, Field


class BiomarkerTrainingRequest(BaseModel):
    X: list[list[float]]
    y: list[int]
    feature_names: list[str]
    epochs: int = Field(default=80, ge=10, le=1000)


class ReportRequest(BaseModel):
    title: str
    analysis: dict
    evidence: list[dict] = []
