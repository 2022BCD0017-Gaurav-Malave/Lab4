pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = "2022bcd0017/2022bcd0017-jenkins:latest"
        SHOULD_DEPLOY = "false"
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo 'Cloning GitHub repository...'
                checkout scm
            }
        }
        
        stage('Setup Python Virtual Environment') {
            steps {
                echo 'Setting up Python virtual environment...'
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }
        
        stage('Train Model') {
            steps {
                echo 'Training model...'
                sh '''
                    . venv/bin/activate
                    python scripts/train.py
                '''
            }
        }
        
        stage('Read Accuracy') {
            steps {
                echo 'Reading accuracy from metrics.json...'
                script {
                    // Read the accuracy and store in environment variable
                    env.CURRENT_ACCURACY = sh(
                        script: '''
                            python3 -c "import json; print(json.load(open('app/artifacts/metrics.json'))['accuracy'])"
                        ''',
                        returnStdout: true
                    ).trim()
                    
                    echo "✓ Current Accuracy read: ${env.CURRENT_ACCURACY}"
                }
            }
        }
        
        stage('Compare Accuracy') {
            steps {
                echo 'Comparing accuracy...'
                withCredentials([string(credentialsId: 'best-accuracy', variable: 'BEST_ACCURACY')]) {
                    script {
                        // Use Python for comparison (more reliable)
                        def comparisonResult = sh(
                            script: """
                                python3 << 'PYTHON_EOF'
import sys

current = float('${env.CURRENT_ACCURACY}')
best = float('${BEST_ACCURACY}')

print(f"Current Accuracy: {current}")
print(f"Best Accuracy: {best}")

if current > best:
    print("DEPLOY")
    sys.exit(0)
else:
    print("SKIP")
    sys.exit(1)
PYTHON_EOF
                            """,
                            returnStatus: true
                        )
                        
                        if (comparisonResult == 0) {
                            env.SHOULD_DEPLOY = "true"
                            echo "✓ New model is better! Will build and push Docker image."
                        } else {
                            env.SHOULD_DEPLOY = "false"
                            echo "✗ New model is not better. Skipping Docker build."
                        }
                    }
                }
            }
        }
        
        stage('Build Docker Image') {
            steps {
                script {
                    if (env.SHOULD_DEPLOY == "true") {
                        echo 'Building Docker image...'
                        docker.withRegistry('https://index.docker.io/v1/', 'dockerhub-creds') {
                            def customImage = docker.build("${env.DOCKER_IMAGE}:${BUILD_NUMBER}")
                            // Store image name for next stage
                            env.DOCKER_IMAGE_FULL = "${env.DOCKER_IMAGE}:${BUILD_NUMBER}"
                        }
                    } else {
                        echo 'Skipping Docker build - model accuracy did not improve'
                    }
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                script {
                    if (env.SHOULD_DEPLOY == "true") {
                        echo 'Pushing Docker image to Docker Hub...'
                        docker.withRegistry('https://index.docker.io/v1/', 'dockerhub-creds') {
                            def customImage = docker.image(env.DOCKER_IMAGE_FULL)
                            customImage.push()
                            customImage.push('latest')
                        }
                    } else {
                        echo 'Skipping Docker push - model accuracy did not improve'
                    }
                }
            }
        }
    }
    
    post {
        always {
            echo 'Archiving artifacts...'
            archiveArtifacts artifacts: 'app/artifacts/**', allowEmptyArchive: true
        }
    }
}