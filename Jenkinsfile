pipeline {
    agent any

    environment {
        IMAGE_NAME = 'eaps-flask-app'
        IMAGE_TAG  = "${env.BUILD_NUMBER}"
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
                    where python || exit 1

                    python -m venv venv
                    call venv\\Scripts\\activate

                    python -m pip install --upgrade pip
                    python -m pip install -r requirements.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                bat '''
                    call venv\\Scripts\\activate
                    python -m pytest test_predict.py -v
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                bat '''
                    docker --version || exit 1
                    docker build -t %IMAGE_NAME%:%IMAGE_TAG% .
                '''
            }
        }

        stage('Deploy') {
            steps {
                bat '''
                    docker compose down
                    docker compose up -d --build
                '''
            }
        }

        stage('Health Check') {
            steps {
                bat '''
                    timeout /t 15
                    curl http://localhost:5000/ || exit 1
                '''
            }
        }
    }

    post {
        always {
            bat 'docker system prune -f'
        }
    }
}
