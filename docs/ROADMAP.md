# Implementation roadmap

## Phase 1 — implemented
- FASTA/FASTQ QC with Biopython.
- CSV gene-expression exploratory ranking.
- VCF parser + optional Ensembl VEP annotation.
- Reproducible PyTorch candidate-biomarker ranking endpoint.
- Evidence-grounded deterministic/LLM reporting.
- PostgreSQL run persistence and S3/MinIO upload path.
- Java Spring Boot orchestration API.
- Docker Compose, Kubernetes manifests, Terraform S3 foundation, CI.

## Phase 2
- Background analysis jobs with Kafka and idempotency keys.
- Scanpy `.h5ad` single-cell workflow: QC, normalization, PCA/UMAP, clustering, marker genes.
- Cohort metadata schema, differential expression statistics, FDR correction.
- Rich VEP normalization and annotation caching.
- Model registry, train/validation/test splits, calibration, AUROC/AUPRC and MLflow.

## Phase 3
- OAuth2/OIDC, RBAC, audit logging, rate limiting.
- OpenTelemetry + Prometheus/Grafana; centralized logs.
- EKS/RDS/VPC modules, IRSA, KMS, Secrets Manager, WAF/ALB.
- Signed multipart S3 uploads, lifecycle rules, retention policies.
- SBOM, image scanning, SAST/dependency scanning and release provenance.
