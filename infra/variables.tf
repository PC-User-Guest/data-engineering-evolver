variable "postgres_image" {
  type    = string
  default = "postgres:15"
}

variable "minio_image" {
  type    = string
  default = "minio/minio:latest"
}

variable "redis_image" {
  type    = string
  default = "redis:7"
}

variable "network_name" {
  type    = string
  default = "de_network"
}
