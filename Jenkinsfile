pipeline {
    agent any

    environment {
        PYTHON = 'python'
    }

    stages {

        stage('Checkout Code') {
            steps {
                git 'https://github.com/AnuragBodkhe/AI-Powered-Employee-Attrition-Prediction-System-for-B2B-HR-Analytics.git'
            }
        }

        stage('Setup Python') {
            steps {
                sh '''
                    python --version
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Run Model') {
            steps {
                sh '''
                    echo "Running Model..."
                    python main.py
                '''
            }
        }

        stage('Show Time') {
            steps {
                script {
                    def time = sh(script: 'date', returnStdout: true).trim()
                    echo "Execution Time: ${time}"
                }
            }
        }
    }

    post {
        success {
            echo "Build Successful ✅"
        }
        failure {
            echo "Build Failed ❌"
        }
    }
}
