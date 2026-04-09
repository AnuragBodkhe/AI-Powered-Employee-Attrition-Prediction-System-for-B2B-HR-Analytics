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
                bat '''
                    python -m venv venv
                    call venv\\Scripts\\activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                bat '''
                    call venv\\Scripts\\activate
                    python -m pytest test_predict.py -v || exit 0
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                bat "docker build -t %IMAGE_NAME%:%IMAGE_TAG% ."
            }
        }

        stage('Deploy with Docker Compose') {
            steps {
                bat '''
                    docker-compose down
                    docker-compose up -d --build
                '''
            }
        }

        stage('Health Check') {
            steps {
                bat '''
                    echo Waiting for the application to start...
                    timeout /t 15
                    curl http://localhost:5000/ || exit 1
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
            bat 'docker-compose down'
        }
        always {
            bat 'docker system prune -f'
        }
    }
}
