terraform {
  required_version = ">= 1.5.0"

  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.25"
    }
  }
}

provider "kubernetes" {
  config_path = "D:/Kube_Config/admin.conf"
}

resource "kubernetes_secret" "openai" {
  metadata {
    name = "eka-openai-secret"
  }

  data = {
    OPENAI_API_KEY = var.openai_api_key
  }

  type = "Opaque"
}

resource "kubernetes_persistent_volume_claim" "vector_store" {
  metadata {
    name = "eka-vector-pvc"
  }

  spec {
    access_modes = ["ReadWriteOnce"]

    resources {
      requests = {
        storage = "1Gi"
      }
    }
  }
}

resource "kubernetes_deployment" "eka" {
  metadata {
    name = "enterprise-knowledge-assistant"
    labels = {
      app = "eka"
    }
  }

  spec {
    replicas = 1

    selector {
      match_labels = {
        app = "eka"
      }
    }

    template {
      metadata {
        labels = {
          app = "eka"
        }
      }

      spec {
        container {
          name  = "eka"
          image = var.image_name

          port {
            container_port = 8000
          }

          env {
            name = "OPENAI_API_KEY"
            value_from {
              secret_key_ref {
                name = kubernetes_secret.openai.metadata[0].name
                key  = "OPENAI_API_KEY"
              }
            }
          }

          volume_mount {
            name       = "vector-store"
            mount_path = "/app/app/knowledge"
          }
        }

        volume {
          name = "vector-store"

          persistent_volume_claim {
            claim_name = kubernetes_persistent_volume_claim.vector_store.metadata[0].name
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "eka" {
  metadata {
    name = "eka-service"
  }

  spec {
    selector = {
      app = "eka"
    }

    port {
      port        = 80
      target_port = 8000
      node_port   = 30080
    }

    type = "NodePort"
  }
}
