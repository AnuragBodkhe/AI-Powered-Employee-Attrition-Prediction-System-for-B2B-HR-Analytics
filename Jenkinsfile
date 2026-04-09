pipeline {
    agent any

    stages {

        stage('Checkout Code') {
            steps {
                git branch: 'main', 
                    url: 'https://github.com/AnuragBodkhe/AI-Powered-Employee-Attrition-Prediction-System-for-B2B-HR-Analytics.git'
            }
        }

        stage('Setup Python') {
            steps {
                bat '''
                    python --version
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Run Model') {
            steps {
                bat '''
                    echo Running Model...
                    python main.py
                '''
            }
        }

        stage('Show Time') {
            steps {
                script {
                    def time = bat(script: 'echo %DATE% %TIME%', returnStdout: true).trim()
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
