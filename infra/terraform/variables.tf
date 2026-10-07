variable "aws_region" { type = string default = "us-east-1" }
variable "project" { type = string default = "helixinsight" }
variable "db_username" { type = string default = "helixadmin" }
variable "db_password" { type = string sensitive = true }
