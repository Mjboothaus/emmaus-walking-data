# See https://just.systems/

# Load variables from .env file

set dotenv-load

# Show available just commands

help:
  @just -l
  
docs:
	open $DOCS_URL

port-process port:
	sudo lsof -i :$SERVER_PORT


# Create the local Python venv (.venv_$PROJECT_NAME) and install requirements(.txt)

venv dev_deploy:
	#!/usr/bin/env bash
	pip-compile requirements-{{dev_deploy}}.in
	python3 -m venv .venv_{{dev_deploy}}_$PROJECT_NAME
	. .venv_{{dev_deploy}}_$PROJECT_NAME/bin/activate
	python3 -m pip install --upgrade pip
	pip install -r requirements-{{dev_deploy}}.txt
	python -m ipykernel install --user --name .venv_{{dev_deploy}}_$PROJECT_NAME
	pip install -U prefect
	echo -e '\n' source .venv_{{dev_deploy}}_$PROJECT_NAME/bin/activate '\n'


activate dev_deploy:
	#!/usr/bin/env zsh
	echo -e '\n' source .venv_{{dev_deploy}}_$PROJECT_NAME/bin/activate '\n'


update-reqs dev_deploy:
	pip-compile requirements-{{dev_deploy}}.in
	pip install -r requirements-{{dev_deploy}}.txt --upgrade


rm-venv dev_deploy:
  #!/usr/bin/env bash
  rm -rf .venv_{{dev_deploy}}_$PROJECT_NAME


test:
  pytest


pyenv-list:
	pyenv install -l


pyenv:
	brew update && brew upgrade pyenv
	pyenv install $PYTHON_VERSION
	pyenv local $PYTHON_VERSION
	pipx reinstall-all


stv:
  streamlit --version

# Run app

app:
  streamlit run $STREAMLIT_RUN_PY --server.port $SERVER_PORT --server.address localhost

dockerfile:
  #!/usr/bin/env bash
  python utils/create_dockerfile.py
  

# Build and run app in a (local) Docker container

open-docker:
	open /Applications/Docker.app
	

docker: dockerfile
  pip-compile requirements-deploy.in
  docker build . -t $PROJECT_NAME
  docker run -p $SERVER_PORT$:$SERVER_PORT $PROJECT_NAME


# Google Cloud Run setup: work in progress (still not "STP" without user input)

gcr-setup:
    #!/usr/bin/env bash
    gcloud components update --quiet
    # TODO: Check if project already exists
    gcloud projects create $PROJECT_NAME --quiet
    gcloud beta billing projects link $PROJECT_NAME --billing-account $BILLING_ACCOUNT_GCP --quiet
    gcloud services enable run.googleapis.com --quiet
    gcloud services enable compute.googleapis.com --quiet
    gcloud services enable cloudbuild.googleapis.com --quiet
    gcloud services enable artifactregistry.googleapis.com --quiet
    gcloud config set project $PROJECT_NAME --quiet
    # gcloud config set region $GCP_REGION --quiet
    gcloud config set compute/zone $GCP_REGION --quiet

# check_project_exists := `gcloud projects describe $PROJECT_NAME | grep name | awk {'print $2'}`
# check_eq := `{{check_project_exists}} == $PROJECT_NAME`

#gcr-check-project-exists: IN_PROGRESS
#    #!/usr/bin/env bash
#    if {{check_eq}} { "Good!" } else { "1984" }


# Deploy container to Google Cloud (Cloud Run) and helper commands

gcr-deploy: dockerfile
	#!/usr/bin/env bash
	pip-compile requirements-deploy.in
	start=`date +%s`

	gcloud run deploy \
	--source . $PROJECT_NAME \
	--region $GCP_REGION \
	--allow-unauthenticated \
	--quiet
	
	end=`date +%s`
	runtime=$((end-start))
	echo ""
	echo $runtime seconds to run job
	echo ""


gcr-list-deployed-url:
    gcloud run services list --platform managed | awk 'NR==2 {print $4}'


gcr-app-disable:   # deleting project does not delete app
    gcloud app versions list


# See: https://stackoverflow.com/questions/59423245/how-to-get-or-generate-deploy-url-for-google-cloud-run-services

# Additional commands

# gcloud config list project

# gcloud auth list

# gcloud config get-value project

# gcloud container images list

# gcloud auth configure-docker

#gcloud run deploy helloworld \
#  --image gcr.io/$GOOGLE_CLOUD_PROJECT/helloworld \
#  --platform managed \
#  --region {{GCP_REGION}} \
#  --allow-unauthenticated

# gcloud container images delete gcr.io/$GOOGLE_CLOUD_PROJECT/helloworld

# gcloud run services delete helloworld \
#  --platform managed \
#  --region {{GCP_REGION}}



# To set the active account, run:
#    $ gcloud config set account `ACCOUNT`

# Finally, set the default zone and project configuration.
# gcloud config set compute/zone {{GCP_REGION}}

# Utilities

pipx:
	pipx reinstall-all