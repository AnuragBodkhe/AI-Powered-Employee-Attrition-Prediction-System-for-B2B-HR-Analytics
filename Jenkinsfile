pipeline {
    agent any

    environment {
        VENV_DIR = "venv"
        REPO_URL = "https://github.com/AnuragBodkhe/AI-Powered-Employee-Attrition-Prediction-System-for-B2B-HR-Analytics.git"
    }

    stages {

        stage('Checkout') {
            steps {
                git branch: 'main', url: "${REPO_URL}"
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
                        pip install pandas numpy scikit-learn
                    fi
                '''
            }
        }

        stage('Run Model') {
            steps {
                sh '''
                    . ${VENV_DIR}/bin/activate
                    python main.py || echo "No main.py found"
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
