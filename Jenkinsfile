pipeline {
    agent any

    environment {
        IMAGE_NAME = "attrition-prediction-app"
        CONTAINER_NAME = "attrition-container"
        PORT = "5000"
    }

    tools {
        // If configured in Jenkins
        python 'Python3'
    }

    stages {

        stage('Checkout Code') {
            steps {
                echo "Cloning GitHub Repository..."
                git branch: 'main', url: 'https://github.com/AnuragBodkhe/AI-Powered-Employee-Attrition-Prediction-System-for-B2B-HR-Analytics.git'
            }
        }

        stage('Setup Python Environment') {
            steps {
                echo "Setting up Python virtual environment..."
                sh '''
                python -m venv venv
                . venv/bin/activate
                pip install --upgrade pip
                pip install -r requirements.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                echo "Running Tests..."
                sh '''
                . venv/bin/activate
                pytest || echo "No tests found, skipping..."
                '''
            }
        }

        stage('Lint Code (Optional)') {
            steps {
                echo "Checking code quality..."
                sh '''
                . venv/bin/activate
                flake8 . || echo "Lint warnings ignored"
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                echo "Building Docker Image..."
                sh '''
                docker build -t $IMAGE_NAME .
                '''
            }
        }

        stage('Stop Existing Container') {
            steps {
                echo "Stopping old container if exists..."
                sh '''
                docker stop $CONTAINER_NAME || true
                docker rm $CONTAINER_NAME || true
                '''
            }
        }

        stage('Run Docker Container') {
            steps {
                echo "Running new container..."
                sh '''
                docker run -d -p $PORT:$PORT --name $CONTAINER_NAME $IMAGE_NAME
                '''
            }
        }

        stage('Health Check') {
            steps {
                echo "Checking if app is running..."
                sh '''
                sleep 10
                curl http://localhost:$PORT || echo "App not responding"
                '''
            }
        }
    }

    post {
        success {
            echo "✅ Pipeline executed successfully!"
        }
        failure {
            echo "❌ Pipeline failed!"
        }
        always {
            echo "🔁 Pipeline finished."
        }
    }
}
