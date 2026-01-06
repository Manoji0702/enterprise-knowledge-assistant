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

# --------------------------------------------------
# Namespace
# --------------------------------------------------
resource "kubernetes_namespace" "eka" {
  metadata {
    name = "eka"
  }
}

# --------------------------------------------------
# Secret (namespaced)
# --------------------------------------------------
resource "kubernetes_secret" "openai" {
  metadata {
    name      = "eka-openai-secret"
    namespace = kubernetes_namespace.eka.metadata[0].name
  }

  data = {
    OPENAI_API_KEY = var.openai_api_key
  }

  type = "Opaque"
}

# --------------------------------------------------
# Persistent Volume (cluster-scoped, NO namespace)
# --------------------------------------------------
resource "kubernetes_persistent_volume" "eka_vector_pv" {
  metadata {
    name = "eka-vector-pv"
  }

  spec {
    capacity = {
      storage = "1Gi"
    }

    access_modes = ["ReadWriteOnce"]

    persistent_volume_reclaim_policy = "Retain"

    persistent_volume_source {
      host_path {
        path = "/mnt/eka-vector-store"
      }
    }
  }
}

# --------------------------------------------------
# Persistent Volume Claim (namespaced, bound to PV)
# --------------------------------------------------
resource "kubernetes_persistent_volume_claim" "vector_store" {
  metadata {
    name      = "eka-vector-pvc"
    namespace = kubernetes_namespace.eka.metadata[0].name
  }

  spec {
    access_modes = ["ReadWriteOnce"]

    resources {
      requests = {
        storage = "1Gi"
      }
    }

    volume_name = kubernetes_persistent_volume.eka_vector_pv.metadata[0].name
  }
}

# --------------------------------------------------
# Deployment (namespaced)
# --------------------------------------------------
resource "kubernetes_deployment" "eka" {
  depends_on = [
    kubernetes_namespace.eka,
    kubernetes_persistent_volume_claim.vector_store
  ]

  metadata {
    name      = "enterprise-knowledge-assistant"
    namespace = kubernetes_namespace.eka.metadata[0].name
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
          image_pull_policy = "Always"
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

# --------------------------------------------------
# Service (namespaced)
# --------------------------------------------------
resource "kubernetes_service" "eka" {
  depends_on = [
    kubernetes_deployment.eka
  ]

  metadata {
    name      = "eka-service"
    namespace = kubernetes_namespace.eka.metadata[0].name
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

