build_run: build run

isort:
	python -m isort keychain
black:
	python -m black keychain
flake:
	python -m flake8 keychain
pylint:
	python -m pylint keychain
format: isort black flake pylint

build:
	cd frontend; npm run build
shell:
	flask --app keychain/app.py shell
run:
	python keychain/app.py