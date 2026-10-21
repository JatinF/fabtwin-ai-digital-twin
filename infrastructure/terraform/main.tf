# Unapplied sketch. Account 000000000000 is a placeholder. Do not apply this stack.
# Kafka, PostgreSQL, and Grafana are not declared here.

variable "account_id" {
  type    = string
  default = "000000000000"
}

variable "region" {
  type    = string
  default = "us-east-1"
}

output "account_id" {
  value = var.account_id
}
