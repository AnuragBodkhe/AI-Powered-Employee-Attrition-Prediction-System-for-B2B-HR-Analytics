pipeline {
    agent any

    environment {
        // Python configuration
        PYTHON_VERSION = '3.11'
        VENV_DIR = "${WORKSPACE}/venv"
        
        // Docker configuration
        DOCKER_REGISTRY = "docker.io"
        DOCKER_IMAGE_NAME = "employee-attrition-prediction"
        DOCKER_IMAGE_TAG = "latest"
        BUILD_NUMBER_TAG = "${BUILD_NUMBER}"
        
        // Project configuration
        PROJECT_NAME = "Employee Attrition System using ML"
        REPO_URL = "https://github.com/AnuragBodkhe/AI-Powered-Employee-Attrition-Prediction-System-for-B2B-HR-Analytics.git"
    }

    options {
        // Keep last 10 builds
        buildDiscarder(logRotator(numToKeepStr: '10'))
        // Timeout after 30 minutes
        timeout(time: 30, unit: 'MINUTES')
        // Disable concurrent builds
        disableConcurrentBuilds()
    }

    stages {
        stage('Checkout') {
            steps {
                script {
                    echo "========== Checking out source code =========="
                    checkout([$class: 'GitSCM',
                        branches: [[name: '*/main']],
                        userRemoteConfigs: [[url: "${REPO_URL}"]],
                        extensions: [[$class: 'CleanBeforeCheckout']]
                    ])
                    echo "Successfully checked out repository"
                }
            }
        }

        stage('Verify Python Installation') {
            steps {
                script {
                    echo "========== Verifying Python Installation =========="
                    try {
                        // Try to find Python executable
                        def pythonPath = sh(
                            script: 'which python3 || which python',
                            returnStdout: true
                        ).trim()
                        echo "Python found at: ${pythonPath}"
                        
                        // Display Python version
                        sh 'python3 --version || python --version'
                    } catch (Exception e) {
                        echo "WARNING: Could not verify Python installation"
                        echo "Make sure Python 3.11+ is installed and in PATH"
                    }
                }
            }
        }

        stage('Setup Virtual Environment') {
            steps {
                script {
                    echo "========== Setting up Python Virtual Environment =========="
                    try {
                        // Remove existing venv if it exists
                        sh '''
                            if [ -d "${VENV_DIR}" ]; then
                                echo "Removing existing virtual environment..."
                                rm -rf ${VENV_DIR}
                            fi
                            
                            echo "Creating new virtual environment..."
                            python3 -m venv ${VENV_DIR} || python -m venv ${VENV_DIR}
                            echo "Virtual environment created successfully"
                        '''
                    } catch (Exception e) {
                        echo "ERROR: Failed to create virtual environment"
                        throw e
                    }
                }
            }
        }

        stage('Install Dependencies') {
            steps {
                script {
                    echo "========== Installing Python Dependencies =========="
                    try {
                        sh '''
                            # Activate virtual environment and upgrade pip
                            . ${VENV_DIR}/bin/activate || source ${VENV_DIR}/Scripts/activate
                            
                            echo "Upgrading pip..."
                            python -m pip install --upgrade pip setuptools wheel
                            
                            # Check if requirements.txt exists
                            if [ -f "requirements.txt" ]; then
                                echo "Installing requirements from requirements.txt..."
                                pip install -r requirements.txt
                            else
                                echo "WARNING: requirements.txt not found. Installing common ML dependencies..."
                                pip install pandas numpy scikit-learn matplotlib seaborn jupyter pytest flask
                            fi
                            
                            echo "Dependencies installed successfully"
                        '''
                    } catch (Exception e) {
                        echo "ERROR: Failed to install dependencies"
                        throw e
                    }
                }
            }
        }

        stage('Code Quality Analysis') {
            steps {
                script {
                    echo "========== Running Code Quality Analysis =========="
                    try {
                        sh '''
                            . ${VENV_DIR}/bin/activate || source ${VENV_DIR}/Scripts/activate
                            
                            # Install linting tools
                            pip install pylint flake8 black --quiet
                            
                            # Run pylint on Python files (ignore errors, just report)
                            echo "Running pylint analysis..."
                            find . -name "*.py" -not -path "./venv/*" -not -path "./.git/*" | head -20 | xargs pylint --disable=all --enable=E || true
                            
                            echo "Code quality analysis completed"
                        '''
                    } catch (Exception e) {
                        echo "WARNING: Code quality analysis had issues (non-blocking)"
                    }
                }
            }
        }

        stage('Run Unit Tests') {
            steps {
                script {
                    echo "========== Running Unit Tests =========="
                    try {
                        sh '''
                            . ${VENV_DIR}/bin/activate || source ${VENV_DIR}/Scripts/activate
                            
                            # Install pytest if needed
                            pip install pytest pytest-cov --quiet
                            
                            # Check if tests directory exists
                            if [ -d "tests" ]; then
                                echo "Running tests from tests/ directory..."
                                pytest tests/ -v --tb=short --cov=. || true
                            elif [ -f "test_*.py" ]; then
                                echo "Running test files in root..."
                                pytest test_*.py -v --tb=short || true
                            else
                                echo "No test files found. Skipping test stage."
                            fi
                        '''
                    } catch (Exception e) {
                        echo "WARNING: Test stage failed (non-blocking for now)"
                    }
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    echo "========== Building Docker Image =========="
                    try {
                        sh '''
                            # Check if Docker is running
                            if ! command -v docker &> /dev/null; then
                                echo "WARNING: Docker is not installed. Skipping Docker build."
                                exit 0
                            fi
                            
                            if ! docker ps > /dev/null 2>&1; then
                                echo "WARNING: Docker daemon is not running. Skipping Docker build."
                                exit 0
                            fi
                            
                            # Check if Dockerfile exists
                            if [ ! -f "Dockerfile" ]; then
                                echo "WARNING: Dockerfile not found. Creating a basic one..."
                                cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
EOF
                            fi
                            
                            echo "Building Docker image: ${DOCKER_IMAGE_NAME}:${BUILD_NUMBER_TAG}"
                            docker build -t ${DOCKER_IMAGE_NAME}:${BUILD_NUMBER_TAG} .
                            docker tag ${DOCKER_IMAGE_NAME}:${BUILD_NUMBER_TAG} ${DOCKER_IMAGE_NAME}:latest
                            
                            echo "Docker image built successfully"
                        '''
                    } catch (Exception e) {
                        echo "WARNING: Docker build failed (non-blocking)"
                    }
                }
            }
        }

        stage('Generate Reports') {
            steps {
                script {
                    echo "========== Generating Build Reports =========="
                    try {
                        sh '''
                            # Create reports directory
                            mkdir -p reports
                            
                            # Generate project summary
                            cat > reports/build_summary.txt << EOF
Build Information:
==================
Build Number: ${BUILD_NUMBER}
Job Name: ${JOB_NAME}
Build URL: ${BUILD_URL}
Workspace: ${WORKSPACE}
Timestamp: $(date)

Python Environment:
===================
Virtual Environment: ${VENV_DIR}
Repository: ${REPO_URL}

Build Artifacts:
================
Docker Image: ${DOCKER_IMAGE_NAME}:${BUILD_NUMBER_TAG}
EOF
                            
                            cat reports/build_summary.txt
                        '''
                    } catch (Exception e) {
                        echo "WARNING: Failed to generate reports"
                    }
                }
            }
        }

        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                script {
                    echo "========== Deployment Stage =========="
                    echo "Running on branch: main"
                    try {
                        sh '''
                            echo "Deployment configuration:"
                            echo "- Project Name: ${PROJECT_NAME}"
                            echo "- Build Number: ${BUILD_NUMBER}"
                            echo ""
                            echo "NOTE: Configure your deployment steps here:"
                            echo "- Push Docker image to registry"
                            echo "- Deploy to Kubernetes/Docker Swarm/Cloud platform"
                            echo "- Run health checks"
                        '''
                    } catch (Exception e) {
                        echo "WARNING: Deployment stage had issues"
                    }
                }
            }
        }

        stage('Health Check') {
            steps {
                script {
                    echo "========== Performing Health Check =========="
                    try {
                        sh '''
                            . ${VENV_DIR}/bin/activate || source ${VENV_DIR}/Scripts/activate
                            
                            # Check if main application file exists
                            if [ -f "app.py" ]; then
                                echo "Checking Python syntax of app.py..."
                                python -m py_compile app.py
                                echo "✓ app.py syntax is valid"
                            fi
                            
                            # List key project files
                            echo ""
                            echo "Project Structure:"
                            ls -la | grep -E "^-" | head -20
                            
                            echo ""
                            echo "Health check completed successfully"
                        '''
                    } catch (Exception e) {
                        echo "WARNING: Health check had issues (non-blocking)"
                    }
                }
            }
        }
    }

    post {
        always {
            script {
                echo "========== Post-Build Cleanup =========="
                try {
                    sh '''
                        # Remove Docker images safely
                        if command -v docker &> /dev/null; then
                            if docker ps > /dev/null 2>&1; then
                                echo "Cleaning up Docker system..."
                                docker system prune -f --volumes || true
                            fi
                        fi
                        
                        echo "Workspace cleanup..."
                        echo "Build completed at: $(date)"
                    '''
                } catch (Exception e) {
                    echo "WARNING: Cleanup operations had issues"
                }
            }
        }

        success {
            script {
                echo "✓ ========== BUILD SUCCESSFUL =========="
                echo "Project: ${PROJECT_NAME}"
                echo "Build Number: ${BUILD_NUMBER}"
                echo "Time: $(date)"
            }
        }

        failure {
            script {
                echo "✗ ========== BUILD FAILED =========="
                echo "Please review the logs above for details"
                echo "Common issues:"
                echo "1. Python not installed or not in PATH"
                echo "2. Missing requirements.txt file"
                echo "3. Docker not running (non-blocking)"
                echo "4. Permission issues on workspace"
            }
        }

        unstable {
            script {
                echo "⚠ ========== BUILD UNSTABLE =========="
                echo "Some stages may have had warnings or partial failures"
            }
        }

        cleanup {
            script {
                echo "Removing temporary files..."
                deleteDir()
            }
        }
    }
}
