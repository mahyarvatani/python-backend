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
    stage('Checkout'){ steps { checkout scm } }

    stage('Unit Tests') {
      agent { docker { image 'python:3.12-slim' } }
      steps {
        sh '''
          python -m venv .venv
          . .venv/bin/activate
          python -m pip install --upgrade pip
          pip install -r requirements-dev.txt
          pytest -q
        '''
      }
    }

    stage('Build & Push'){
      steps {
        sh 'docker build -t "${FULL_IMAGE}" .'
        sh 'docker push "${FULL_IMAGE}"'
      }
    }
stage('Deploy HOT') {
  agent { docker { image 'lachlanevenson/k8s-kubectl:v1.30.4'
                   args '--add-host=host.docker.internal:host-gateway' } }
  steps {
    withKubeConfig([credentialsId: 'kubernetes-config', contextName: 'kind-hot']) {
      sh '''
        kubectl apply -f k8s/ns.yaml
        kubectl apply -f k8s/service.yaml
        kubectl apply -f k8s/ingress.yaml
        kubectl -n apps apply -f k8s/deployment.yaml || true
        kubectl -n apps set image deploy/backend backend="${FULL_IMAGE}"
        kubectl -n apps rollout status deploy/backend --timeout=120s
      '''
    }
  }
}

stage('Deploy STANDBY') {
  agent { docker { image 'lachlanevenson/k8s-kubectl:v1.30.4'
                   args '--add-host=host.docker.internal:host-gateway' } }
  steps {
    withKubeConfig([credentialsId: 'kubernetes-config', contextName: 'kind-standby']) {
      sh '''
        kubectl apply -f k8s/ns.yaml
        kubectl apply -f k8s/service.yaml
        kubectl apply -f k8s/ingress.yaml
        kubectl -n apps apply -f k8s/deployment.yaml || true
        kubectl -n apps set image deploy/backend backend="${FULL_IMAGE}"
        kubectl -n apps rollout status deploy/backend --timeout=120s
      '''
    }
  }
}


  }
}

