# CI/CD Pipeline with Jenkins and Kubernetes

## Overview
This project demonstrates a **CI/CD pipeline** for a Python backend application. It leverages **Jenkins**, **Docker**, and **Kubernetes** to automate the process of testing, building, scanning, and deploying the application to **two Kubernetes clusters (HOT & STANDBY)** with high availability provided by HAProxy.  

Key features:
- Unit testing with **pytest**
- Code quality checks with **SonarQube**
- Container image scanning with **Trivy**
- CI/CD pipeline using **Jenkins Declarative Pipeline**
- Deployment to **HOT** and **STANDBY** clusters via `kubectl`
- Monitoring with **Prometheus & Grafana**
- Logging with **Kubetail**

---

## Setup Instructions

### 1. Clone the Repository
```bash
git clone git@github.com:mahyarvatani/python-backend.git
cd python-backend
```

### 2. Prepare the Infrastructure
- Inside the repo, you will find a file: **`infrastructure.zip`**.  
- Move it **out of the `python-backend` folder**:
  ```bash
  mv infrastructure.zip ..
  cd ..
  ```
- Unzip it:
  ```bash
  unzip infrastructure.zip -d infrastructure
  cd infrastructure
  ```
- Run the Ansible playbooks to set up clusters:
  ```bash
  ansible-playbook create-kind.yml
  ansible-playbook install-ingress.yml
  ```

At this point, your HOT and STANDBY Kubernetes clusters with ingress controllers should be ready. 
you can build HAproxy, Jenkins, SonarQube containers with docker-compose provided in the folder with the name of tools. you can deploy kube-prometheus-stack and kubetail with helm chart that provided in monitoring.txt and logging.txt
---

### 3. Modify the Application
Now you can make changes to the Python backend code inside the `python-backend/` folder.

### 4. Push Changes
Commit and push your changes to GitHub:
```bash
git add .
git commit -m "xxxxxxxxxx"
git push origin main
```

Jenkins will automatically trigger the **pipeline**, which will:
1. Run unit tests  
2. Analyze code with SonarQube  
3. Build the Docker image  
4. Scan vulnerabilities with Trivy  
5. Push the image to the registry  
6. Deploy to HOT and STANDBY clusters  

---

## Accessing the Services

### Application
- HOT cluster → [http://127.0.0.1:8080](http://127.0.0.1:8080)  
- STANDBY cluster → [http://127.0.0.1:9080](http://127.0.0.1:9080)  
- HAProxy (automatic failover) → [http://127.0.0.1](http://127.0.0.1)  

### SonarQube
```bash
http://127.0.0.1:9000
```

### Monitoring
- **Grafana**
  ```bash
  kubectl --context kind-hot -n monitoring port-forward svc/kube-prometheus-stack-grafana 8000:80
  ```
  → [http://127.0.0.1:8000](http://127.0.0.1:8000)

- **Prometheus**
  ```bash
  kubectl --context kind-hot -n monitoring port-forward svc/kube-prometheus-stack-prometheus 8001:9090
  ```
  → [http://127.0.0.1:8001](http://127.0.0.1:8001)

### Logging
```bash
kubectl port-forward -n kubetail-system svc/kubetail-dashboard 8003:8080
```
→ [http://127.0.0.1:8003](http://127.0.0.1:8003)

---

## Project Structure
```
.
├── python-backend/        # Application code & Jenkinsfile
│   ├── app/               # Python backend
│   ├── tests/             # Unit tests
│   ├── Jenkinsfile        # CI/CD pipeline
│   └── requirements*.txt
├── infrastructure.zip     # Infrastructure setup (move & unzip before use)
```

## Security
- Trivy ensures images are free of **High** and **Critical** vulnerabilities before pushing.  
- If vulnerabilities are found, the build is marked **UNSTABLE** (but not failed).  

---

## Monitoring & Logs
- **Prometheus** and **Grafana** provide real-time metrics and dashboards.  
- **Kubetail** aggregates logs for easier debugging.  



