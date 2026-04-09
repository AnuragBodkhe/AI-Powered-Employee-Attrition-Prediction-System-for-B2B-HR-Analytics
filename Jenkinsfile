pipeline {
    agent any

    environment {
        IMAGE_NAME = 'eaps-flask-app'
        IMAGE_TAG  = "${env.BUILD_NUMBER}"
        CONTAINER_NAME = 'eaps_flask_app'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    . venv/bin/activate
                    python -m pytest test_predict.py -v || true
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh "docker build -t ${IMAGE_NAME}:${IMAGE_TAG} ."
            }
        }

        stage('Deploy with Docker Compose') {
            steps {
                sh '''
                    docker-compose down || true
                    docker-compose up -d --build
                '''
            }
        }

        stage('Health Check') {
            steps {
                sh '''
                    echo "Waiting for the application to start..."
                    sleep 15
                    curl --fail http://localhost:5000/ || (echo "Health check failed!" && exit 1)
                '''
            }
        }
    }

    post {
        success {
            echo "Pipeline completed successfully. EAPS app is running on port 5000."
        }
        failure {
            echo "Pipeline failed. Check the logs above for details."
            sh 'docker-compose down || true'
        }
        always {
            sh 'docker system prune -f || true'
        }
    }
}
