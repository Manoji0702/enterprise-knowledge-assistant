pipeline {
    agent any

    environment {
        IMAGE_NAME = "manoj0207/enterprise-knowledge-assistant"
        KUBECONFIG = "D:/Kube_Config/admin.conf"
    }

    stages {

        stage("Checkout") {
            steps {
                checkout scm
            }
        }

        stage("Docker Build & Push") {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    bat """
                    docker login -u %DOCKER_USER% -p %DOCKER_PASS%
                    docker build -t %IMAGE_NAME%:%BUILD_NUMBER% .
                    docker push %IMAGE_NAME%:%BUILD_NUMBER%
                    """
                }
            }
        }

        stage("Terraform Deploy") {
            steps {
                withCredentials([
                    string(credentialsId: 'openai-api-key', variable: 'OPENAI_KEY')
                ]) {
                    dir('terraform') {
                        bat """
                        terraform init -input=false
                        terraform plan ^
                          -var="image_name=%IMAGE_NAME%:%BUILD_NUMBER%" ^
                          -var="openai_api_key=%OPENAI_KEY%"
                        terraform apply -auto-approve ^
                          -var="image_name=%IMAGE_NAME%:%BUILD_NUMBER%" ^
                          -var="openai_api_key=%OPENAI_KEY%"
                        """
                    }
                }
            }
        }
    }

    post {
        success {
            echo "🚀 Deployment successful"
        }
        failure {
            echo "❌ Deployment failed"
        }
    }
}
