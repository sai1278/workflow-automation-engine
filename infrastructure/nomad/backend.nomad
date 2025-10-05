job "backend" {
  datacenters = ["dc1"]
  group "backend" {
    count = 1
    task "app" {
      driver = "docker"
      config {
        image = "myorg/backend:latest"
        port_map { http = 8000 }
      }
      env {
        ENVIRONMENT = "production"
      }
      resources {
        cpu    = 500
        memory = 512
      }
      service {
        name = "backend"
        port = "http"
        check {
          type     = "http"
          path     = "/health"
          interval = "10s"
          timeout  = "2s"
        }
      }
    }
  }
}
