pipeline {
    agent {label '!master'}
    stages {
        stage ('Checkout') {
            steps {
                cleanWs()
                dir('sources'){
                    git url: 'https://github.com/oscarvx00/sitas-downloaders-youtube', branch: 'main'
                }
            }
        }
        stage('Test'){
            environment {
                scannerHome = tool 'SonarQubeScanner'
                RABBITMQ_ENDPOINT = "goose-01.rmq2.cloudamqp.com"
                RABBITMQ_VHOST = credentials("RABBITMQ_USER")
                RABBITMQ_USER = credentials("RABBITMQ_USER")
                RABBITMQ_PASS = credentials("RABBITMQ_PASS")
                DOWNLOAD_REQUEST_EXCHANGE = "sitas-test-exchange-downloadrequest"
                DOWNLOAD_REQUEST_YOUTUBE_QUEUE = "sitas-test-queue-downloadrequest-youtube"
                DOWNLOAD_COMPLETED_EXCHANGE = "sitas-test-exchange-downloadcompleted"
                MINIO_INTERNAL_ENDPOINT = "oscarvx00.ddns.net"
                MINIO_INTERNAL_PORT = 10000
                MINIO_INTERNAL_USER = credentials("MINIO_INTERNAL_USER")
                MINIO_INTERNAL_PASS = credentials("MINIO_INTERNAL_PASS")
                MINIO_INTERNAL_BUCKET = "internal-storage-test"
                YOUTUBE_API_KEY = credentials("YOUTUBE_API_KEY")
                AZURE_SERVICE_BUS_CONNECTION_STRING = credentials("AZURE_SERVICE_BUS_CONNECTION_STRING_YOUTUBE")
                AZURE_SERVICE_BUS_DOWNLOAD_REQUEST_YOUTUBE_QUEUE = "download-request-youtube-test"
                AZURE_SERVICE_BUS_DOWNLOAD_REQUEST_QUEUE = "download-request-test"
                AZURE_SERVICE_BUS_DOWNLOAD_COMPLETED_QUEUE = "download-completed-test"
            }
            steps {
                dir('Test') {
                    sh 'cp -r -a ../sources/. ./'
                    sh 'cp -r -a containers/test/. ./'
                    sh """
                    docker build \
                        --build-arg AZURE_SERVICE_BUS_CONNECTION_STRING=${AZURE_SERVICE_BUS_CONNECTION_STRING}\
                        --build-arg AZURE_SERVICE_BUS_DOWNLOAD_REQUEST_YOUTUBE_QUEUE=${AZURE_SERVICE_BUS_DOWNLOAD_REQUEST_YOUTUBE_QUEUE} \
                        --build-arg AZURE_SERVICE_BUS_DOWNLOAD_REQUEST_QUEUE=${AZURE_SERVICE_BUS_DOWNLOAD_REQUEST_QUEUE} \
                        --build-arg AZURE_SERVICE_BUS_DOWNLOAD_COMPLETED_QUEUE=${AZURE_SERVICE_BUS_DOWNLOAD_COMPLETED_QUEUE} \
                        --build-arg DOWNLOAD_REQUEST_EXCHANGE=${DOWNLOAD_REQUEST_EXCHANGE} \
                        --build-arg DOWNLOAD_REQUEST_YOUTUBE_QUEUE=${DOWNLOAD_REQUEST_YOUTUBE_QUEUE} \
                        --build-arg DOWNLOAD_COMPLETED_EXCHANGE=${DOWNLOAD_COMPLETED_EXCHANGE} \
                        --build-arg MINIO_INTERNAL_ENDPOINT=${MINIO_INTERNAL_ENDPOINT} \
                        --build-arg MINIO_INTERNAL_PORT=${MINIO_INTERNAL_PORT} \
                        --build-arg MINIO_INTERNAL_USER=${MINIO_INTERNAL_USER} \
                        --build-arg MINIO_INTERNAL_PASS=${MINIO_INTERNAL_PASS} \
                        --build-arg MINIO_INTERNAL_BUCKET=${MINIO_INTERNAL_BUCKET} \
                        --build-arg YOUTUBE_API_KEY=${YOUTUBE_API_KEY} \
                        -t sitas-downloader-youtube-test .
                    """
                    sh 'docker container rm sitas-downloader-youtube-test-container || true'
                    sh 'docker run --name sitas-downloader-youtube-test-container sitas-downloader-youtube-test'
                    dir('src'){
                        sh 'docker cp sitas-downloader-youtube-test-container:/sitas-dl-yt-test/coverage.xml ./'
                        sh 'docker container rm sitas-downloader-youtube-test-container'
                        withSonarQubeEnv('sonarqube'){
                            sh "${scannerHome}/bin/sonar-scanner"
                        }
                        script {
                            def qualitygate = waitForQualityGate()
                            if(qualitygate.status != 'OK'){
                                //error "Pipeline aborted due to quality gate coverage failure."
                            }
                        }
                    }
                }
            }
        }
        stage('Deploy') {
            steps {
                dir('deploy'){
                    sh 'cp -r -a ../sources/. ./'
                    sh 'cp -r -a containers/prod/. ./'
                    sh 'cp src/requirements.txt ./'
                    
                    sh """
                    docker build -t oscarvicente/sitas-downloaders-youtube-prod .
                    """
                    withCredentials([string(credentialsId: 'dockerhub-pass', variable: 'pass')]) {
                        sh "docker login --username oscarvicente --password $pass; docker push oscarvicente/sitas-downloaders-youtube-prod"
                    }
    
                    //Deploy in k8s, server configured
                    dir('kube'){
                        sh 'kubectl delete deploy -n sitas sitas-downloaders-youtube || true'
                        sh 'kubectl apply -f sitas-downloaders-youtube-deploy.yaml'
                    }
                }
            }
        }
    }
}