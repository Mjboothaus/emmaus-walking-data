# See https://just.systems/

#app_py := "src/Main.py" in .env
#server_port := "8080" in .env


# Load variables from .env file

set dotenv-load

# Show available just commands

help:
  @just -l


name:
	#!/usr/bin/env bash
	echo $PROJECT_NAME


docs:
	open $DOCS_URL


port-process port:
	sudo lsof -i :$SERVER_PORT


# Create the local Python venv (.venv_$PROJECT_NAME) and install requirements(.txt)

venv dev_deploy:
	#!/usr/bin/env bash
	#pip-compile requirements-{{dev_deploy}}.in
	python3 -m venv .venv_{{dev_deploy}}_$PROJECT_NAME
	. .venv_{{dev_deploy}}_$PROJECT_NAME/bin/activate
	python3 -m pip install --upgrade pip
	pip install -r requirements-{{dev_deploy}}.in
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


# Utilities

pipx:
	pipx reinstall-all