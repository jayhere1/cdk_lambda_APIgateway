
ENV_REPO_VERION ?= $(REPO_VERSION)

cdk-diff:
	npx cdk diff \
	--parameters REPOVERSION=$(ENV_REPO_VERION)

cdk-deploy:
	npx cdk deploy \
	--parameters REPOVERSION=$(ENV_REPO_VERION)