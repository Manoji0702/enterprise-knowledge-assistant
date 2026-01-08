pipeline {
    agent any

    environment {
        DOCKER_USERNAME = 'manoj0207'
        IMAGE_NAME      = 'enterprise-knowledge-assistant'
        IMAGE_TAG       = "${BUILD_NUMBER}"
        FULL_IMAGE      = "${DOCKER_USERNAME}/${IMAGE_NAME}:${IMAGE_TAG}"
        LATEST_IMAGE    = "${DOCKER_USERNAME}/${IMAGE_NAME}:latest"
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Docker Build') {
            steps {
                bat """
                docker build --no-cache -t %FULL_IMAGE% .
                docker tag %FULL_IMAGE% %LATEST_IMAGE%
                """
            }
        }

        stage('Docker Login & Push') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DOCKERHUB_USER',
                    passwordVariable: 'DOCKERHUB_PASS'
                )]) {
                    bat """
                    echo %DOCKERHUB_PASS% | docker login -u %DOCKERHUB_USER% --password-stdin
                    docker push %FULL_IMAGE%
                    docker push %LATEST_IMAGE%
                    docker logout
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
