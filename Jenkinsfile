pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = "2022bcd0017/2022bcd0017-jenkins:latest"
        CURRENT_ACCURACY = ""
        BEST_ACCURACY = credentials('best-accuracy')
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
                    python train.py
                '''
            }
        }
        
        stage('Read Accuracy') {
            steps {
                echo 'Reading accuracy from metrics.json...'
                script {
                    def metrics = readJSON file: 'app/artifacts/metrics.json'
                    CURRENT_ACCURACY = metrics.accuracy
                    echo "Current Accuracy: ${CURRENT_ACCURACY}"
                }
            }
        }
        
        stage('Compare Accuracy') {
            steps {
                echo 'Comparing accuracy...'
                script {
                    def currentAcc = CURRENT_ACCURACY.toFloat()
                    def bestAcc = BEST_ACCURACY.toFloat()
                    
                    echo "Current Accuracy: ${currentAcc}"
                    echo "Best Accuracy: ${bestAcc}"
                    
                    if (currentAcc > bestAcc) {
                        SHOULD_DEPLOY = "true"
                        echo "✓ New model is better! Will build and push Docker image."
                    } else {
                        SHOULD_DEPLOY = "false"
                        echo "✗ New model is not better. Skipping Docker build."
                    }
                }
            }
        }
        
        stage('Build Docker Image') {
            when {
                expression { SHOULD_DEPLOY == "true" }
            }
            steps {
                echo 'Building Docker image...'
                script {
                    docker.withRegistry('https://index.docker.io/v1/', 'dockerhub-creds') {
                        def customImage = docker.build("${DOCKER_IMAGE}:${BUILD_NUMBER}")
                    }
                }
            }
        }
        
        stage('Push Docker Image') {
            when {
                expression { SHOULD_DEPLOY == "true" }
            }
            steps {
                echo 'Pushing Docker image to Docker Hub...'
                script {
                    docker.withRegistry('https://index.docker.io/v1/', 'dockerhub-creds') {
                        def customImage = docker.image("${DOCKER_IMAGE}:${BUILD_NUMBER}")
                        customImage.push()
                        customImage.push('latest')
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