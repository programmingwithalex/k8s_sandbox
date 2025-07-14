# ************************************************************************** #
# * if on windows, install `make` using `choco install make`
# ************************************************************************** #

# * need to be unique to ensure all pods updated with new image
# TAG := $(shell powershell -NoProfile -Command "Get-Date -Format 'yyyyMMddHHmmss'")
ENVIRONMENT=prod
TAG=latest-$(ENVIRONMENT)
NAMESPACE=alex-sandbox-$(ENVIRONMENT)
VALUES_FILE=values-$(ENVIRONMENT).yaml
# VALUES_FILE=values-prod.yaml

PROMETHEUS_STACK_NAME=monitoring
PROMETHEUS_NAMESPACE=monitoring

# ********************* Configuration for K3D Cluster *********************
AWS_ACCOUNT_ID=212135963698
AWS_REGION=us-east-1
ECR_REPO_APP_AUTH=$(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/eks-sandbox-alex/auth-service
ECR_REPO_APP_1=$(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/eks-sandbox-alex/app-1
ECR_REPO_APP_2=$(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/eks-sandbox-alex/app-2
KUBE_CONTEXT=arn:aws:eks:$(AWS_REGION):$(AWS_ACCOUNT_ID):cluster/web-quickstart
# *********************************************************************** #

# ********************* Configuration for Frontend *********************
APP_NAME_FRONTEND=react-frontend
DOCKERFILE_FRONTEND=react-frontend/Dockerfile
BUILD_CONTEXT_FRONTEND=react-frontend
HELM_CHART_PATH_FRONTEND=react-frontend-deployment
ECR_REPO_FRONTEND=$(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com/eks-sandbox-alex/react-frontend
# ********************************************************************* #

# ********************* Configuration for Auth Service *********************
APP_NAME_AUTH=auth
DOCKERFILE_AUTH=auth/Dockerfile
BUILD_CONTEXT_AUTH=auth
HELM_CHART_PATH_AUTH=auth-deployment
# *********************************************************************** #

# ********************* Configuration for App 1 *********************
APP_NAME_APP_1=app1
DOCKERFILE_APP_1=app1/Dockerfile
BUILD_CONTEXT_APP_1=app1
CLUSTER_NAME_APP_1=web-quickstart
HELM_CHART_PATH_APP_1=app1-deployment
# *********************************************************************** #

# ********************* Configuration for App 2 *********************
APP_NAME_APP_2=app2
DOCKERFILE_APP_2=app2/Dockerfile
BUILD_CONTEXT_APP_2=app2
CLUSTER_NAME_APP_2=web-quickstart
HELM_CHART_PATH_APP_2=app2-deployment
# *********************************************************************** #

# # ********************* Configuration for Ingress ALB *********************
INGRESS_NAME_ALB=fastapi-ingress-alb
INGRESS_CHART_PATH_ALB=ingress_alb
INGRESS_FILENAME_ALB_CONTROLLER=ingress_class_alb_controller.yaml
# *********************************************************************** #

# # ********************* Configuration for Ingress Nginx *********************
INGRESS_NAME_NGINX_API=fastapi-ingress-nginx-api
INGRESS_CHART_PATH_NGINX_API=ingress_nginx_api

INGRESS_NAME_NGINX_FRONTEND=fastapi-ingress-nginx-frontend
INGRESS_CHART_PATH_NGINX_FRONTEND=ingress_nginx_frontend
# *********************************************************************** #

ecr-login: ## Login to AWS ECR
	aws ecr get-login-password --region $(AWS_REGION) | \
	docker login --username AWS --password-stdin $(AWS_ACCOUNT_ID).dkr.ecr.$(AWS_REGION).amazonaws.com

# ********************* Composite Targets *********************
# * \.PHONY\ - says target (\deploy-app-1\) is not a real file, just a name for a command to run
# * Without it, make will check if there's a file or directory named \deploy-app-1\, and if one exists,
# * it won’t run commands because thinks work is already done
.PHONY: delete-all deploy-all ecr-login deploy-prometheus-stack deploy-ingressclass-alb-controller \
	deploy-nginx-controller deploy-nginx-controller-dev deploy-nginx-controller-prod \
	deploy-react-frontend \
	deploy-auth-service-ecr deploy-app-1-ecr deploy-app-2-ecr \
	deploy-auth-service deploy-app-1 deploy-app-2 \
	deploy-app-api-ingress deploy-app-frontend-ingress deploy-alb-ingress \
	delete-prometheus-stack delete-app-1 delete-app-2 delete-app-ingress delete-alb-ingress \
	delete-nginx-controller

# * can run \make deploy-all\ or \make deploy-app-1\, \make deploy-app-2\, etc.
deploy-all: deploy-prometheus-stack deploy-nginx-controller deploy-react-frontend deploy-auth-service deploy-app-1 deploy-app-2 \
	deploy-app-api-ingress deploy-app-frontend-ingress deploy-alb-ingress

deploy-ecr: deploy-auth-service-ecr deploy-app-1-ecr deploy-app-2-ecr

deploy-apps: deploy-react-frontend deploy-auth-service deploy-app-1 deploy-app-2

deploy-ingress: deploy-app-api-ingress deploy-app-frontend-ingress deploy-alb-ingress
# *********************************************************************** #

# ********************* Deployment Targets ****************************** #

# ************************************************************************ #
# * first is without Helm, second is with
# kubectl rollout restart deployment $(APP_NAME_APP_1)
# helm upgrade --install $(INGRESS_NAME) $(HELM_CHART_PATH_APP_1)
# ************************************************************************ #

# deploys prometheus and grafana
# set `grafana.persistence.enabled=true` to enable persistent storage for Grafana
# set `grafana.persistence.size=10Gi` to set the size of the persistent storage
# set `grafana.persistence.storageClassName=gp2` to use the gp2 storage class
deploy-prometheus-stack:
	helm repo add prometheus-community https://prometheus-community.github.io/helm-charts || true
	helm repo update
	helm upgrade --install $(PROMETHEUS_STACK_NAME) prometheus-community/kube-prometheus-stack \
		--namespace $(PROMETHEUS_NAMESPACE) --create-namespace \
		-f grafana/values_elb.yaml \
		--set grafana.persistence.enabled=true \
		--set grafana.persistence.size=10Gi \
		--set grafana.persistence.storageClassName=gp2

# * deploys the Nginx ingress controller (L7) - only needs to be run once at cluster creation
# * must have `controller.metrics.enabled=true` and `controller.extraArgs.metrics-per-host=true`
# *   for Prometheus to export metrics into Grafana
#
# * must set `controller.scope.enabled=true` to allow ingresses in different namespaces
# * reference in `ingress-nginx/values.yaml` for `ingress.ingressClassName` as `nginx-dev` or `nginx-prod`
#
# * must set `controller.metrics.service.enabled=true` and `controller.metrics.serviceMonitor.enabled=true`
# *   to enable Prometheus to scrape metrics from the Nginx ingress controller
# * must set `controller.metrics.serviceMonitor.namespace=$(PROMETHEUS_NAMESPACE)` to ensure
# *   that the service monitor is created in the same namespace as Prometheus
# * `controller.metrics.serviceMonitor.labels.release=$(PROMETHEUS_NAMESPACE)`
# *    doesn't actually work, so we need to label the ServiceMonitor manually
# *    with:
# * 		`kubectl label servicemonitor ingress-nginx-$(ENVIRONMENT)-controller \
# *    		 -n $(PROMETHEUS_NAMESPACE) release=$(PROMETHEUS_NAMESPACE) --overwrite || true`
# *   to ensure that Prometheus can scrape metrics from the Nginx ingress controller
#
# * must match `servicemonitor.yaml > metadata.labels.release` value (currently `monitoring`)
#
# * label setter override on separate line at bottom needed because doesn't work
# *   ~~`--set controller.metrics.serviceMonitor.labels.release=$(PROMETHEUS_NAMESPACE)`~~ - doesn't work
deploy-nginx-controller:
	helm upgrade --install ingress-nginx-$(ENVIRONMENT) ingress-nginx/ingress-nginx \
		--namespace $(NAMESPACE) --create-namespace \
		--set controller.service.type=ClusterIP \
		--set controller.ingressClassResource.enabled=true \
		--set controller.ingressClassResource.name=nginx-$(ENVIRONMENT) \
		--set controller.ingressClass=nginx-$(ENVIRONMENT) \
		--set controller.metrics.enabled=true \
		--set controller.extraArgs.metrics-per-host=true \
		--set controller.scope.enabled=true \
		--set controller.metrics.service.enabled=true \
		--set controller.metrics.serviceMonitor.enabled=true \
		--set controller.metrics.serviceMonitor.namespace=$(PROMETHEUS_NAMESPACE) \
		--set controller.metrics.serviceMonitor.labels.release=$(PROMETHEUS_NAMESPACE)

	kubectl -n $(PROMETHEUS_NAMESPACE) label servicemonitor ingress-nginx-$(ENVIRONMENT)-controller \
		release=$(PROMETHEUS_NAMESPACE) --overwrite

# * deploys the ALB ingress controller - only needs to be run once at cluster creation
deploy-ingressclass-alb-controller:
	kubectl --context $(KUBE_CONTEXT) apply \
	  -f $(INGRESS_CHART_PATH_ALB)/$(INGRESS_FILENAME_ALB_CONTROLLER)

deploy-react-frontend: ecr-login ## Build, push, and deploy frontend
	docker build -t $(APP_NAME_FRONTEND):$(TAG) -f $(DOCKERFILE_FRONTEND) $(BUILD_CONTEXT_FRONTEND)
	docker tag $(APP_NAME_FRONTEND):$(TAG) $(ECR_REPO_FRONTEND):$(TAG)
	docker push $(ECR_REPO_FRONTEND):$(TAG)

	helm upgrade --install $(APP_NAME_FRONTEND) $(HELM_CHART_PATH_FRONTEND) \
		--kube-context $(KUBE_CONTEXT) \
		--namespace $(NAMESPACE) --create-namespace \
		--set image.repository=$(ECR_REPO_FRONTEND) \
		--set image.tag=$(TAG)

deploy-auth-service-ecr: ecr-login
	docker build -t $(APP_NAME_AUTH):$(TAG) -f $(DOCKERFILE_AUTH) $(BUILD_CONTEXT_AUTH)
	docker tag $(APP_NAME_AUTH):$(TAG) $(ECR_REPO_APP_AUTH):$(TAG)
	docker push $(ECR_REPO_APP_AUTH):$(TAG)

deploy-auth-service: deploy-auth-service-ecr
	helm upgrade --install $(APP_NAME_AUTH) $(HELM_CHART_PATH_AUTH) \
		--kube-context $(KUBE_CONTEXT) \
		--namespace $(NAMESPACE) --create-namespace \
		--set image.repository=$(ECR_REPO_APP_AUTH) \
		--set image.tag=$(TAG) \
		-f $(HELM_CHART_PATH_AUTH)/$(VALUES_FILE)

deploy-app-1-ecr: ecr-login
	docker build -t $(APP_NAME_APP_1):$(TAG) -f $(DOCKERFILE_APP_1) $(BUILD_CONTEXT_APP_1)
	docker tag $(APP_NAME_APP_1):$(TAG) $(ECR_REPO_APP_1):$(TAG)
	docker push $(ECR_REPO_APP_1):$(TAG)

deploy-app-1: deploy-app-1-ecr
	helm upgrade --install $(APP_NAME_APP_1) $(HELM_CHART_PATH_APP_1) \
	  --kube-context $(KUBE_CONTEXT) \
	  --namespace $(NAMESPACE) --create-namespace \
	  --set image.repository=$(ECR_REPO_APP_1) \
	  --set image.tag=$(TAG) \
	  -f $(HELM_CHART_PATH_APP_1)/$(VALUES_FILE)

deploy-app-2-ecr: ecr-login
	docker build -t $(APP_NAME_APP_2):$(TAG) -f $(DOCKERFILE_APP_2) $(BUILD_CONTEXT_APP_2)
	docker tag $(APP_NAME_APP_2):$(TAG) $(ECR_REPO_APP_2):$(TAG)
	docker push $(ECR_REPO_APP_2):$(TAG)

deploy-app-2: deploy-app-2-ecr
	helm upgrade --install $(APP_NAME_APP_2) $(HELM_CHART_PATH_APP_2) \
	  --kube-context $(KUBE_CONTEXT) \
	  --namespace $(NAMESPACE) --create-namespace \
	  --set image.repository=$(ECR_REPO_APP_2) \
	  --set image.tag=$(TAG) \
	  -f $(HELM_CHART_PATH_APP_2)/$(VALUES_FILE)

# * creates ingress CR (custom resource) to tell the Nginx ingress controller how to route traffic
deploy-app-api-ingress:
	helm upgrade --install $(INGRESS_NAME_NGINX_API) $(INGRESS_CHART_PATH_NGINX_API) \
	--kube-context $(KUBE_CONTEXT) \
	--namespace $(NAMESPACE) --create-namespace \
	-f $(INGRESS_CHART_PATH_NGINX_API)/$(VALUES_FILE)

# * creates ingress CR (custom resource) to tell the Nginx ingress controller how to route traffic
deploy-app-frontend-ingress:
	helm upgrade --install $(INGRESS_NAME_NGINX_FRONTEND) $(INGRESS_CHART_PATH_NGINX_FRONTEND) \
	--kube-context $(KUBE_CONTEXT) \
	--namespace $(NAMESPACE) --create-namespace \
	-f $(INGRESS_CHART_PATH_NGINX_FRONTEND)/$(VALUES_FILE)

# * creates ingress CR (custom resource) to forward external traffic to the nginx‑ingress‑controller Service
deploy-alb-ingress:
	helm upgrade --install $(INGRESS_NAME_ALB) $(INGRESS_CHART_PATH_ALB) \
	  --kube-context $(KUBE_CONTEXT) \
	  --namespace $(NAMESPACE) --create-namespace \
	  -f $(INGRESS_CHART_PATH_ALB)/$(VALUES_FILE)


# ********************* Deletion Targets *********************
delete-all: delete-prometheus-stack delete-alb-ingress delete-app-ingress-api \
	delete-app-ingress-frontend delete-auth-service delete-app-1 delete-app-2

delete-prometheus-stack:
	helm uninstall $(PROMETHEUS_STACK_NAME) -n $(PROMETHEUS_NAMESPACE) || true
	kubectl delete namespace $(PROMETHEUS_NAMESPACE) --ignore-not-found

delete-nginx-controller:
	helm uninstall ingress-nginx-$(ENVIRONMENT) --namespace $(NAMESPACE) || true

delete-auth-service:
	helm uninstall $(APP_NAME_AUTH) --namespace $(NAMESPACE) || true

delete-app-1:
	helm uninstall $(APP_NAME_APP_1) --namespace $(NAMESPACE) || true

delete-app-2:
	helm uninstall $(APP_NAME_APP_2) --namespace $(NAMESPACE) || true

delete-app-ingress-api:
	helm uninstall $(INGRESS_NAME_NGINX_API) --namespace $(NAMESPACE) || true

delete-app-ingress-frontend:
	helm uninstall $(INGRESS_NAME_NGINX_FRONTEND) --namespace $(NAMESPACE) || true

delete-alb-ingress:
	helm uninstall $(INGRESS_NAME_ALB) --namespace $(NAMESPACE) || true
# *********************************************************************** #

# ********************* ArgoCD Deploy & Sync Targets *********************
# must ensure `argocd` namespace is created first with `kubectl create namespace argocd`
argocd-create-namespace:
	kubectl apply -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

argocd-app1:
	kubectl apply -f $(HELM_CHART_PATH_APP_1)/argocd-$(ENVIRONMENT).yaml
	argocd app sync app1-$(ENVIRONMENT)

argocd-app2:
	kubectl apply -f $(HELM_CHART_PATH_APP_2)/argocd-$(ENVIRONMENT).yaml
	argocd app sync app2-$(ENVIRONMENT)

argocd-auth:
	kubectl apply -f $(HELM_CHART_PATH_AUTH)/argocd-$(ENVIRONMENT).yaml
	argocd app sync auth-$(ENVIRONMENT)

argocd-frontend:
	kubectl apply -f $(HELM_CHART_PATH_FRONTEND)/argocd-$(ENVIRONMENT).yaml
	argocd app sync react-frontend-$(ENVIRONMENT)

argocd-all: argocd-create-namespace argocd-app1 argocd-app2 argocd-auth argocd-frontend

argocd-applicationset:
	kubectl apply -n argocd -f applications_sets/application_set.yaml
