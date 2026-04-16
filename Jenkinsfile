pipeline {
    agent any

    // Параметризация сборки согласно п.4 задания
    parameters {
        string(name: 'REPO_URL', defaultValue: 'https://github.com/BrenesRM/insecure-web.git', description: 'URL репозитория')
        string(name: 'BRANCH_TAG', defaultValue: 'main', description: 'Ветка или тег для сборки')
        string(name: 'DOCKER_IMAGE_NAME', defaultValue: 'myuser/insecure-web', description: 'Имя образа в DockerHub')
        string(name: 'DOCKER_TAG', defaultValue: 'latest', description: 'Тег образа')
    }

    environment {
        // Путь для сохранения отчетов сканеров
        REPORTS_DIR = "${WORKSPACE}/security-reports"
        // Имя контейнера для деплоя и DAST
        CONTAINER_NAME = 'insecure-web-app'
        // URL для DAST сканирования
        APP_URL = 'http://localhost:80'
    }

    stages {
        
        stage('Checkout SCM') {
            steps {
                echo "Клонирование репозитория: ${params.REPO_URL} (${params.BRANCH_TAG})"
                git url: "${params.REPO_URL}", branch: "${params.BRANCH_TAG}"
            }
        }

        stage('SAST Scan (Semgrep)') {
            steps {
                script {
                    echo "Запуск Semgrep..."
                    // Создаем директорию для отчетов
                    sh "mkdir -p ${REPORTS_DIR}"
                    // Запуск Semgrep с сохранением отчета в JSON
                    sh """
                        docker run --rm -v "${WORKSPACE}:/src" -w /src returntocorp/semgrep semgrep scan \
                        --config=auto \
                        --json --output ${REPORTS_DIR}/semgrep-report.json \
                        --no-error
                    """
                }
            }
            post {
                always {
                    // Архивируем отчет для ручной выгрузки в GitHub (п.3)
                    archiveArtifacts artifacts: "${REPORTS_DIR}/semgrep-report.json", fingerprint: true
                }
            }
        }

        stage('SCA Scan (Dependency Check)') {
            steps {
                script {
                    echo "Запуск OWASP Dependency Check..."
                    sh """
                        docker run --rm -v "${WORKSPACE}:/src" -v "${REPORTS_DIR}:/report" owasp/dependency-check \
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
                script {
                    echo "Сборка Docker образа: ${params.DOCKER_IMAGE_NAME}:${params.DOCKER_TAG}"
                    // Используем переменные окружения Docker для тегирования
                    docker.build("${params.DOCKER_IMAGE_NAME}:${params.DOCKER_TAG}")
                }
            }
        }

        stage('Container Scanning (Trivy)') {
            steps {
                script {
                    echo "Запуск Trivy для сканирования собранного образа..."
                    sh """
                        docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
                        -v ${REPORTS_DIR}:/root/.cache/ aquasec/trivy image \
                        --format json --output /root/.cache/trivy-report.json \
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
            when {
                expression { params.DOCKER_IMAGE_NAME != 'myuser/insecure-web' } // Простая проверка, что имя не дефолтное
            }
            steps {
                script {
                    echo "Публикация образа в DockerHub..."
                    // Предполагается, что Credentials ID 'dockerhub-creds' настроен в Jenkins
                    docker.withRegistry('', 'dockerhub-creds') {
                        def img = docker.image("${params.DOCKER_IMAGE_NAME}:${params.DOCKER_TAG}")
                        img.push()
                    }
                }
            }
        }

        stage('Deployment') {
            steps {
                script {
                    echo "Остановка старого контейнера (если есть)..."
                    sh "docker stop ${CONTAINER_NAME} || true && docker rm ${CONTAINER_NAME} || true"
                    
                    echo "Запуск контейнера на хостовой машине..."
                    // Маппим порт 80 контейнера на порт 80 хоста
                    sh """
                        docker run -d --name ${CONTAINER_NAME} \
                        -p 80:80 \
                        ${params.DOCKER_IMAGE_NAME}:${params.DOCKER_TAG}
                    """
                    
                    // Небольшая пауза, чтобы приложение успело подняться перед DAST
                    sleep time: 10, unit: 'SECONDS'
                }
            }
        }

        stage('DAST Scanning (OWASP ZAP)') {
            steps {
                script {
                    echo "Запуск OWASP ZAP Baseline Scan против ${APP_URL}"
                    sh """
                        docker run --rm --network="host" \
                        -v ${REPORTS_DIR}:/zap/wrk/:rw \
                        -t owasp/zap2docker-stable zap-baseline.py \
                        -t ${APP_URL} \
                        -J zap-report.json \
                        -r zap-report.html || true
                    """
                    // Команда возвращает exit code 1 если найдены уязвимости (что для нас ОК), поэтому используем || true
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: "${REPORTS_DIR}/zap-report.*", fingerprint: true
                }
            }
        }
    }

    post {
        always {
            echo "Pipeline завершен. Отчеты сохранены в артефактах Jenkins."
            echo "Для выгрузки в GitHub: скачайте артефакты через интерфейс Jenkins и закоммитьте их в репозиторий вручную."
            
            // Очистка: Останавливаем контейнер, но оставляем образ для возможного переиспользования
            sh "docker stop ${CONTAINER_NAME} || true"
            sh "docker rm ${CONTAINER_NAME} || true"
            
            // Удаляем workspace в конце, если нужно (опционально)
            cleanWs()
        }
    }
}