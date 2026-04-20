pipeline {
    agent any

    parameters {
        string(name: 'REPO_URL', defaultValue: 'https://github.com/amajps/gazpromtest.git')
        string(name: 'BRANCH_TAG', defaultValue: 'master')
        string(name: 'DOCKER_IMAGE_NAME', defaultValue: 'amajps/vuln-app')
        string(name: 'DOCKER_TAG', defaultValue: 'dev')
    }

    environment {
        REPORTS_DIR = "security-reports"
        SAST_DIR   = "${REPORTS_DIR}/semgrep"
        SCA_DIR    = "${REPORTS_DIR}/dependency-check"
        IMAGE_DIR  = "${REPORTS_DIR}/trivy"
        DAST_DIR   = "${REPORTS_DIR}/zap"

        CONTAINER_NAME = 'vuln-app'
        APP_URL = 'http://localhost:8080'
    }

    stages {

        stage('Checkout SCM') {
            steps {
                checkout([
                    $class: 'GitSCM',
                    branches: [[name: "${params.BRANCH_TAG}"]],
                    userRemoteConfigs: [[
                        url: "${params.REPO_URL}",
                        credentialsId: 'github-credentials'
                    ]]
                ])
            }
        }

        stage('Prepare Report Dirs') {
            steps {
                sh """
                    mkdir -p ${SAST_DIR}
                    mkdir -p ${SCA_DIR}
                    mkdir -p ${IMAGE_DIR}
                    mkdir -p ${DAST_DIR}
                    chmod -R 777 ${REPORTS_DIR}
                """
            }
        }

        stage('SAST Scan (Semgrep)') {
            steps {
                sh """
                    docker run --rm \
                    -v "${WORKSPACE}:/src" \
                    -w /src \
                    returntocorp/semgrep semgrep scan \
                    --config=auto \
                    --json \
                    --output /src/${SAST_DIR}/semgrep-report.json \
                    --no-error
                """
            }
            post {
                always {
                    archiveArtifacts artifacts: "${SAST_DIR}/semgrep-report.json", fingerprint: true
                }
            }
        }

        stage('SCA Scan (Dependency Check)') {
            steps {
                script {
                    echo "Запуск OWASP Dependency Check..."
                    sh """
                        docker run --rm \
                        -v "${WORKSPACE}:/src" \
                        -v "${WORKSPACE}/security-reports:/report" \
                        owasp/dependency-check \
                        --scan /src \
                        --format HTML \
                        --format JSON \
                        --out /report \
                        --project "Insecure Web App"
                    """
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: "${REPORTS_DIR}/dependency-check-report.*", fingerprint: true
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                sh "docker build -t ${params.DOCKER_IMAGE_NAME}:${params.DOCKER_TAG} ."
            }
        }

        stage('Container Scanning (Trivy)') {
            steps {
                script {
                    echo "Запуск Trivy для сканирования собранного образа..."
                    sh """
                        docker run --rm \
                        -v /var/run/docker.sock:/var/run/docker.sock \
                        -v "${WORKSPACE}/security-reports:/report" \
                        aquasec/trivy image \
                        --format json \
                        --output /report/trivy-report.json \
                        --severity HIGH,CRITICAL \
                        ${params.DOCKER_IMAGE_NAME}:${params.DOCKER_TAG}
                    """
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: "${REPORTS_DIR}/trivy-report.json", fingerprint: true
                }
            }
        }


        stage('Publishing to DockerHub') {
            steps {
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-creds',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh """
                        echo \$DOCKER_PASS | docker login -u \$DOCKER_USER --password-stdin
                        docker push ${params.DOCKER_IMAGE_NAME}:${params.DOCKER_TAG}
                    """
                }
            }
        }

        stage('Deployment') {
            steps {
                sh "docker stop ${CONTAINER_NAME} || true && docker rm ${CONTAINER_NAME} || true"

                sh """
                    docker run -d --name ${CONTAINER_NAME} \
                    -p 8081:8080 \
                    ${params.DOCKER_IMAGE_NAME}:${params.DOCKER_TAG}
                """

                sleep 10
            }
        }

        stage('DAST Scanning (OWASP ZAP)') {
            steps {
                sh """
                    docker run --rm --network="host" -u 0 \
                    -v "${WORKSPACE}/${DAST_DIR}:/zap/wrk/:rw" \
                    zaproxy/zap-stable \
                    zap-full-scan.py \
                    -t ${APP_URL} \
                    -J zap-report.json \
                    -r zap-report.html \
                    -m 5 \
                    -T 10 \
                    -d || true
                """

                sh "ls -la ${DAST_DIR} || true"
            }
            post {
                always {
                    archiveArtifacts artifacts: "${DAST_DIR}/zap-report.*", fingerprint: true
                }
            }
        }
    }

    post {
        always {
            sh "docker stop ${CONTAINER_NAME} || true"
            sh "docker rm ${CONTAINER_NAME} || true"
            cleanWs()
        }
    }
}