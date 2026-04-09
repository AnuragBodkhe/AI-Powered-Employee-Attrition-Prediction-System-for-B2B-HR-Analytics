pipeline {
    agent any

    environment {
        VENV_DIR = "venv"
        REPO_URL = "https://github.com/AnuragBodkhe/AI-Powered-Employee-Attrition-Prediction-System-for-B2B-HR-Analytics.git"
        DOCKER_IMAGE = "employee-attrition-ml"
    }

    stages {

        stage('Checkout Code') {
            steps {
                git branch: 'main', url: "${REPO_URL}"
            }
        }

        stage('Setup Python') {
            steps {
                sh '''
                    python3 --version
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
                    
                    if [ -f main.py ]; then
                        python main.py
                    else
                        echo "main.py not found, skipping..."
                    fi
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    if [ ! -f Dockerfile ]; then
                        echo "Creating Dockerfile..."
                        cat <<EOF > Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt || true
CMD ["python", "main.py"]
EOF
                    fi

                    docker build -t ${DOCKER_IMAGE}:latest .
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

        always {
            sh 'echo "Cleaning workspace..."'
        }
    }
}
