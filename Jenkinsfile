pipeline {
    agent any

    environment {
        IMAGE_NAME = "enterprise-knowledge-assistant"
        IMAGE_TAG  = "${BUILD_NUMBER}"
    }

    stages {

        stage("Checkout") {
            steps {
                checkout scm
            }
        }

        stage("Validate Python App") {
            steps {
                sh 'python --version'
                sh 'pip install -r requirements.txt'
                sh 'python -c "import app.main"'
            }
        }

        stage("Docker Build") {
            steps {
                sh "docker build -t ${IMAGE_NAME}:${IMAGE_TAG} ."
            }
        }

        stage("Smoke Test (Container)") {
            steps {
                sh """
                docker run -d -p 8000:8000 --name eka-test ${IMAGE_NAME}:${IMAGE_TAG}
                sleep 5
                curl http://127.0.0.1:8000/health
                docker rm -f eka-test
                """
            }
        }
    }

    post {
        always {
            sh "docker ps -a"
        }
        success {
            echo "CI pipeline completed successfully"
        }
        failure {
            echo "CI pipeline failed"
        }
    }
}
