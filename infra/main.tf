terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = ">= 2.20.0"
    }
  }
}

provider "docker" {
  host = "unix:///var/run/docker.sock"
}

resource "docker_network" "de" {
  name = var.network_name
}

resource "docker_container" "postgres" {
  image = var.postgres_image
  name  = "de_postgres"
  env = [
    "POSTGRES_USER=deuser",
    "POSTGRES_PASSWORD=depass",
    "POSTGRES_DB=dedb"
  ]
  networks_advanced = [{ name = docker_network.de.name }]
}

resource "docker_container" "minio" {
  image = var.minio_image
  name  = "de_minio"
  command = ["server", "/data"]
  env = [
    "MINIO_ROOT_USER=minio",
    "MINIO_ROOT_PASSWORD=minio123"
  ]
  networks_advanced = [{ name = docker_network.de.name }]
  ports {
    internal = 9000
    external = 9000
  }
}

resource "docker_container" "redis" {
  image = var.redis_image
  name  = "de_redis"
  networks_advanced = [{ name = docker_network.de.name }]
}

# added redis resource placeholder

# added redis resource placeholder

# added redis resource placeholder

# added redis resource placeholder 650

# added redis resource placeholder 132
