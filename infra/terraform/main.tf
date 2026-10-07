data "aws_caller_identity" "current" {}

resource "aws_s3_bucket" "omics" {
  bucket = "${var.project}-omics-${data.aws_caller_identity.current.account_id}"
}
resource "aws_s3_bucket_versioning" "omics" {
  bucket = aws_s3_bucket.omics.id
  versioning_configuration { status = "Enabled" }
}
resource "aws_s3_bucket_server_side_encryption_configuration" "omics" {
  bucket = aws_s3_bucket.omics.id
  rule { apply_server_side_encryption_by_default { sse_algorithm = "AES256" } }
}
resource "aws_s3_bucket_public_access_block" "omics" {
  bucket = aws_s3_bucket.omics.id
  block_public_acls = true
  block_public_policy = true
  ignore_public_acls = true
  restrict_public_buckets = true
}

# Networking/EKS/RDS are intentionally split into a second deployment milestone.
# This first module creates the encrypted, versioned research-data landing bucket safely.
output "omics_bucket" { value = aws_s3_bucket.omics.bucket }
