pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "2022bcd0017/2022bcd0017-jenkins"
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

        stage('Train Model in Python 3.11 Container') {
            steps {
                echo 'Running training inside Python 3.11 container...'
                script {
                    docker.image('python:3.11-slim').inside {
                        sh '''
                            pip install --upgrade pip
                            pip install -r requirements.txt
                            python scripts/train.py
                        '''
                    }
                }
            }
        }

        stage('Read Accuracy') {
            steps {
                echo 'Reading accuracy from metrics.json...'
                script {
                    def metrics = readJSON file: 'model/metrics.json'
                    CURRENT_ACCURACY = metrics.r2_score.toString()
                    echo "Current Accuracy (R2): ${CURRENT_ACCURACY}"
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
                    docker.build("${DOCKER_IMAGE}:${BUILD_NUMBER}", ".")
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
                        def image = docker.image("${DOCKER_IMAGE}:${BUILD_NUMBER}")
                        image.push()
                        image.push("latest")
                    }
                }
            }
        }
    }

    post {
        always {
            echo 'Archiving artifacts...'
            archiveArtifacts artifacts: 'model/**', allowEmptyArchive: true
        }
    }
}