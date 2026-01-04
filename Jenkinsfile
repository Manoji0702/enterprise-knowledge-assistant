pipeline {
    agent any

    environment {
        IMAGE_NAME = "enterprise-knowledge-assistant"
    }

    stages {

        stage("Checkout") {
            steps {
                checkout scm
            }
        }

        stage("Docker Build") {
            steps {
                bat """
                docker build -t %IMAGE_NAME%:${env.BUILD_NUMBER} .
                """
            }
        }

        stage("Smoke Test (Container)") {
            steps {
                bat """
                docker run -d -p 8000:8000 --name eka-test %IMAGE_NAME%:${env.BUILD_NUMBER}
                timeout /t 5
                curl http://127.0.0.1:8000/health
                docker rm -f eka-test
                """
            }
        }
    }

    post {
        always {
            bat "docker ps -a"
        }
        success {
            echo "CI pipeline completed successfully"
        }
        failure {
            echo "CI pipeline failed"
        }
    }
}
