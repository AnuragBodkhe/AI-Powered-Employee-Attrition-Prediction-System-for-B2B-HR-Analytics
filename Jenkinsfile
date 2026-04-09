pipeline {
    agent any

    environment {
        VENV_DIR = "venv"
    }

    stages {

        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/AnuragBodkhe/AI-Powered-Employee-Attrition-Prediction-System-for-B2B-HR-Analytics.git'
            }
        }

        stage('Setup Python') {
            steps {
                sh '''
                    python3 -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                    
                    if [ -f requirements.txt ]; then
                        pip install -r requirements.txt
                    else
                        pip install pandas numpy scikit-learn flask
                    fi
                '''
            }
        }

        stage('Run Model') {
            steps {
                sh '''
                    . ${VENV_DIR}/bin/activate
                    echo "Running ML Model..."
                    python main.py || echo "main.py not found"
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    if [ ! -f Dockerfile ]; then
                        cat <<EOF > Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt || true
CMD ["python", "main.py"]
EOF
                    fi

                    docker build -t employee-attrition-ml:latest .
                '''
            }
        }

        stage('Show Time') {
            steps {
                script {
                    def time = sh(script: 'date', returnStdout: true).trim()
                    echo "Build Time: ${time}"
                }
            }
        }
    }

    post {
        success {
            script {
                def time = sh(script: 'date', returnStdout: true).trim()
                echo "✅ Build Successful at ${time}"
            }
        }
        failure {
            echo "❌ Build Failed"
        }
    }
}
