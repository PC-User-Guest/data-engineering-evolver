output "postgres_container_id" {
  value = docker_container.postgres.id
}

output "minio_container_id" {
  value = docker_container.minio.id
}

output "redis_container_id" {
  value = docker_container.redis.id
}
}
