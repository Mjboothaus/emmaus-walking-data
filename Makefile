pip-compile:
	pip-compile requirements.in

venv-reqs:
	python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt 

install-jupyter-kernel:
	python -m ipykernel install --user --name=.venv