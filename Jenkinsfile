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

    stage('Unit Tests'){
      steps {
        sh 'python -m venv .venv && . .venv/bin/activate && pip install -r requirements-dev.txt && pytest -q'
      }
    }

    stage('Build & Push'){
      steps {
        sh 'docker build -t "${FULL_IMAGE}" .'
        sh 'docker push "${FULL_IMAGE}"'
      }
    }

    stage('Deploy HOT'){
      steps {
        sh '''
          kubectl --context "${HOT_CONTEXT}" apply -f k8s/ns.yaml
          # no regcred needed
          kubectl --context "${HOT_CONTEXT}" apply -f k8s/service.yaml
          kubectl --context "${HOT_CONTEXT}" apply -f k8s/ingress.yaml
          kubectl --context "${HOT_CONTEXT}" -n apps apply -f k8s/deployment.yaml || true
          kubectl --context "${HOT_CONTEXT}" -n apps set image deploy/backend backend="${FULL_IMAGE}"
          kubectl --context "${HOT_CONTEXT}" -n apps rollout status deploy/backend --timeout=120s
        '''
      }
    }

    stage('Deploy STANDBY'){
      steps {
        sh '''
          kubectl --context "${STBY_CONTEXT}" apply -f k8s/ns.yaml
          kubectl --context "${STBY_CONTEXT}" apply -f k8s/service.yaml
          kubectl --context "${STBY_CONTEXT}" apply -f k8s/ingress.yaml
          kubectl --context "${STBY_CONTEXT}" -n apps apply -f k8s/deployment.yaml || true
          kubectl --context "${STBY_CONTEXT}" -n apps set image deploy/backend backend="${FULL_IMAGE}"
          kubectl --context "${STBY_CONTEXT}" -n apps rollout status deploy/backend --timeout=120s
        '''
      }
    }
  }
}


