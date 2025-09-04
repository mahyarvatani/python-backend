pipeline {
  agent any

  environment {
    REGISTRY_HOST = 'localhost:5001'
    IMAGE_NAME    = "${env.IMAGE_NAME ?: 'python-backend'}"
    IMAGE_TAG     = "${env.IMAGE_TAG ?: env.BUILD_NUMBER}"
    FULL_IMAGE    = "${REGISTRY_HOST}/${IMAGE_NAME}:${IMAGE_TAG}"
    HOT_CONTEXT   = "kind-hot"
    STBY_CONTEXT  = "kind-standby"
  }

  stages {

    stage('Unit Tests') {
      agent { docker { image 'python:3.12-slim'; reuseNode true } }
      steps {
        sh '''
          set -e
          python -m venv .venv
          . .venv/bin/activate
          python -m pip install --upgrade pip
          pip install -r requirements-dev.txt
          # export PYTHONPATH="$PWD"   # uncomment if tests can't import app/
          pytest -q
        '''
      }
    }
    
    stage('SonarQube Analysis') {
  steps {
    withSonarQubeEnv('sonar_server') {
      sh '''
        sonar-scanner \
          -Dsonar.projectKey=python-backend \
          -Dsonar.sources=app \
          -Dsonar.tests=tests \
          -Dsonar.python.version=3.12 \
          -Dsonar.coverageReportPaths=coverage.xml
      '''
    }
  }
}


    stage('Build & Push') {
      steps {
        sh 'docker build -t "${FULL_IMAGE}" .'
        sh 'docker push "${FULL_IMAGE}"'
      }
    }

    stage('Deploy HOT') {
      agent { docker { image 'dtzar/helm-kubectl:3.14.4'; args '--add-host=host.docker.internal:host-gateway'; reuseNode true } }
      steps {
        withKubeConfig(credentialsId: 'kubernetes-config', contextName: "${HOT_CONTEXT}") {
          sh '''
            set -e
            
            kubectl config set-cluster kind-hot \
               --server="https://host.docker.internal:6444" \
               --insecure-skip-tls-verify=true

            kubectl config current-context
            kubectl config view --minify -o jsonpath="{.clusters[0].cluster.server}"; echo
            kubectl get nodes

            kubectl apply -f k8s/ns.yaml
            kubectl apply -f k8s/service.yaml
            kubectl -n python-backend apply -f k8s/deployment.yaml || true
            kubectl -n python-backend set image deploy/backend backend="${FULL_IMAGE}"
            kubectl -n python-backend rollout status deploy/backend --timeout=120s
          '''
        }
      }
    }

    stage('Deploy STANDBY') {
      agent { docker { image 'dtzar/helm-kubectl:3.14.4'; args '--add-host=host.docker.internal:host-gateway'; reuseNode true } }
      steps {
        withKubeConfig(credentialsId: 'kubernetes-config', contextName: "${STBY_CONTEXT}") {
          sh '''
            set -e
            kubectl config set-cluster kind-standby \
               --server="https://host.docker.internal:7444" \
               --insecure-skip-tls-verify=true

            kubectl config current-context
            kubectl config view --minify -o jsonpath="{.clusters[0].cluster.server}"; echo
            kubectl get nodes

            kubectl apply -f k8s/ns.yaml
            kubectl apply -f k8s/service.yaml
            kubectl -n python-backend apply -f k8s/deployment.yaml || true
            kubectl -n python-backend set image deploy/backend backend="${FULL_IMAGE}"
            kubectl -n python-backend rollout status deploy/backend --timeout=120s
          '''
        }
      }
    }

  }
}



