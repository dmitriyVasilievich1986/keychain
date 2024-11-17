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
	flask --app keychain.app:create_app shell
run:
	flask --app keychain.app:create_app run
build_run: build run
