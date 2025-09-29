# ************************************************************************** #
# * if on windows, install `make` using `choco install make`
# ************************************************************************** #

# ********************* General Configuration *********************
NAMESPACE=alex-sandbox  # default namespace for all apps and ingress resources
# *********************************************************************** #

# ********************* Configuration for App 1 *********************
APP_NAME_APP_1=fastapi-app1
DOCKERFILE_APP_1=app1/Dockerfile
BUILD_CONTEXT_APP_1=app1
CLUSTER_NAME_APP_1=demo
HELM_CHART_PATH_APP_1=app1
# *********************************************************************** #

# ********************* Configuration for App 2 *********************
APP_NAME_APP_2=fastapi-app2
DOCKERFILE_APP_2=app2/Dockerfile
BUILD_CONTEXT_APP_2=app2
CLUSTER_NAME_APP_2=demo
HELM_CHART_PATH_APP_2=app2
# *********************************************************************** #

# ********************* Configuration for MetalLB *********************
METALLB_MANIFEST=https://raw.githubusercontent.com/metallb/metallb/v0.13.12/config/manifests/metallb-native.yaml
METALLB_IP_POOL=metal_lb/metallb-ip-pool.yaml
# *********************************************************************** #

# # ********************* Configuration for Ingress *********************
INGRESS_NAME=fastapi-ingress
INGRESS_CHART_PATH=ingress
# *********************************************************************** #

# ********************* Composite Targets *********************
# * `.PHONY` - says target (`deploy-app1`) is not a real file, just a name for a command to run
# * Without it, make will check if there's a file or directory named `deploy-app1`, and if one exists,
# * it won’t run commands because thinks work is already done
# *
# * `metallb`:
# * 	- load balancer implementation for bare-metal Kubernetes clusters
# * 	- only needs to be deployed once, so it's included in `deploy-all`
# * 	- must be deployed before apps that use it, so it's listed first in `deploy-all`
.PHONY: deploy-all deploy-metallb deploy-ingress deploy-app1 deploy-app2

# * can run `make deploy-all` or `make deploy-app1`, `make deploy-app2`, etc.
deploy-all: deploy-metallb deploy-ingress deploy-app1 deploy-app2
# *********************************************************************** #

# ********************* Deployment Targets *********************

# ************************************************************************ #
# * first is without Helm, second is with Helm
# kubectl rollout restart deployment $(APP_NAME_APP_1)
# helm upgrade --install $(INGRESS_NAME) $(HELM_CHART_PATH_APP_1)
# ************************************************************************ #

# * `--timeout=90s` - wait up to 90 seconds for the controller to be ready
deploy-metallb: ## deploy metallb load balancer
	kubectl apply -f $(METALLB_MANIFEST)
	kubectl -n metallb-system rollout status deploy/controller --timeout=90s
	kubectl apply -f $(METALLB_IP_POOL)

deploy-app1:  ## deploy app1
	docker build -t $(APP_NAME_APP_1) -f $(DOCKERFILE_APP_1) $(BUILD_CONTEXT_APP_1)
	k3d image import $(APP_NAME_APP_1) -c $(CLUSTER_NAME_APP_1)

	helm upgrade --install $(APP_NAME_APP_1) $(HELM_CHART_PATH_APP_1) --namespace $(NAMESPACE) --create-namespace

deploy-app2:  ## deploy app2
	docker build -t $(APP_NAME_APP_2) -f $(DOCKERFILE_APP_2) $(BUILD_CONTEXT_APP_2)
	k3d image import $(APP_NAME_APP_2) -c $(CLUSTER_NAME_APP_2)

	helm upgrade --install $(APP_NAME_APP_2) $(HELM_CHART_PATH_APP_2) --namespace $(NAMESPACE) --create-namespace

deploy-ingress:  ## deploy ingress
	helm upgrade --install $(INGRESS_NAME) $(INGRESS_CHART_PATH) --namespace $(NAMESPACE) --create-namespace
