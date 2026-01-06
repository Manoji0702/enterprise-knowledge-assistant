pipeline {
    agent any

    environment {
        DOCKER_USER = 'manoj0207'
        IMAGE_NAME  = 'enterprise-knowledge-assistant'
        IMAGE_TAG   = "${BUILD_NUMBER}"
        FULL_IMAGE  = "${DOCKER_USER}/${IMAGE_NAME}:${IMAGE_TAG}"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Sync Knowledge Docs') {
            steps {
                bat """
                f not exist C:\\eka-knowledge\\processed mkdir C:\\eka-knowledge\\processed
                xcopy /E /Y docs C:\\eka-knowledge\\processed\\
                """
            }
        }

        stage('Docker Build') {
            steps {
                bat """
                docker build -t %FULL_IMAGE% .
                """
            }
        }

        stage('Docker Push') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    bat """
                    docker login -u %DOCKER_USER% -p %DOCKER_PASS%
                    docker push %FULL_IMAGE%
                    """
                }
            }
        }

        stage('Terraform Deploy') {
            steps {
                withCredentials([string(
                    credentialsId: 'openai-api-key',
                    variable: 'OPENAI_API_KEY'
                )]) {
                    dir('terraform') {
                        bat """
                        terraform init -input=false
                        terraform apply -auto-approve ^
                          -var="image_name=%FULL_IMAGE%" ^
                          -var="openai_api_key=%OPENAI_API_KEY%"
                        """
                    }
                }
            }
        }
    }

    post {
        success {
            echo "✅ CI/CD completed successfully"
        }
        failure {
            echo "❌ CI/CD failed"
        }
    }
}
