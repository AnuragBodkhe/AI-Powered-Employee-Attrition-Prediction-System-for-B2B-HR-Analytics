pipeline {
    agent any

    environment {
        IMAGE_NAME = 'eaps-flask-app'
        IMAGE_TAG  = "${env.BUILD_NUMBER}"
        PYTHON = "C:\\Users\\Anurag\\AppData\\Local\\Programs\\Python\\Python311\\python.exe"
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
                    "%PYTHON%" -m venv venv
                    call venv\\Scripts\\activate

                    "%PYTHON%" -m pip install --upgrade pip
                    "%PYTHON%" -m pip install -r requirements.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                bat '''
                    call venv\\Scripts\\activate
                    "%PYTHON%" -m pytest test_predict.py -v
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                bat '''
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
            bat 'docker system prune -f || echo Docker not running'
        }
    }
}
