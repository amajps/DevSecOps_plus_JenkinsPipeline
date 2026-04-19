# Insecure Web Project

This project demonstrates an intentionally insecure web application for testing and educational purposes. The application is designed to be run in a Docker container and is built with poor security practices, making it an ideal target for penetration testing and security analysis tools like **Nikto**.

> **Disclaimer:** This project is for educational and testing purposes only. Do not deploy this application in a production environment.

---

## Features
- **Insecure Web Application**:
  - Written in Python (Flask) with common web vulnerabilities.
  - Bad security practices included (e.g., no input validation, weak passwords, exposed sensitive data).
- **Dockerized Application**:
  - Easy to deploy with Docker.
  - Contains all dependencies and configurations.
- **Testing Environment**:
  - Ready for tools like Nikto to analyze the application for vulnerabilities.

---

## Prerequisites

1. **Docker**: Ensure Docker is installed on your system.  
   [Download Docker](https://www.docker.com/get-started)

2. **Docker Compose**: To simplify multi-container orchestration.  
   [Install Docker Compose](https://docs.docker.com/compose/install/)

---

## Project Structure

insecure-web/ ├── app/ │ ├── static/ │ │ ├── style.css # CSS file for the web app │ │ └── images/ │ │ └── background.jpg # Background image for styling │ ├── templates/ │ │ └── index.html # Main HTML file for the app │ └── app.py # Flask application ├── Dockerfile # Docker configuration for the web app ├── docker-compose.yml # Compose file for multi-container setup └── README.md # Project documentation


---

## Usage

### 1. Clone the Repository
```bash
git clone https://github.com/brenesrm/insecure-web.git
cd insecure-web

docker-compose up --build

http://127.0.0.1:80

Use tools like Nikto or OWASP ZAP to analyze the application:

bash

Copy code

nikto -h http://127.0.0.1:80


Example Vulnerabilities
No Input Validation: User input is not sanitized or validated.
Hardcoded Credentials: Admin credentials are hardcoded in the application.
Exposed Sensitive Data: Logs and database files may leak sensitive information.
Insecure Deployment: Application runs in debug mode.
Improper Security Headers: Missing or incorrect HTTP security headers.


mkdir -p /var/lib/jenkins/.kube
cp ~/.kube/config /var/lib/jenkins/.kube/config
chown -R jenkins:jenkins /var/lib/jenkins/.kube


sudo mkdir -p /var/lib/jenkins/.kube
sudo cp /home/kali/.kube/config /var/lib/jenkins/.kube/config

🔥 Шаг 1 — копируем kubeconfig Jenkins-у
sudo mkdir -p /var/lib/jenkins/.kube
sudo cp /home/kali/.kube/config /var/lib/jenkins/.kube/config
🔥 Шаг 2 — исправляем пути внутри config

Открой:

sudo nano /var/lib/jenkins/.kube/config

Найди:

client-certificate: /home/kali/.minikube/...
client-key: /home/kali/.minikube/...
certificate-authority: /home/kali/.minikube/...
👉 ЗАМЕНИ на:
client-certificate: /var/lib/jenkins/.minikube/profiles/minikube/client.crt
client-key: /var/lib/jenkins/.minikube/profiles/minikube/client.key
certificate-authority: /var/lib/jenkins/.minikube/ca.crt
🔥 Шаг 3 — копируем сами сертификаты
sudo cp -r /home/kali/.minikube /var/lib/jenkins/
sudo chown -R jenkins:jenkins /var/lib/jenkins/.minikube
🔥 Шаг 4 — права
sudo chown -R jenkins:jenkins /var/lib/jenkins/.kube
