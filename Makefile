build_run: build run

isort:
	python -m isort backend
black:
	python -m black backend
flake:
	python -m flake8 backend
pylint:
	python -m pylint backend
format: isort black flake

build:
	cd frontend; npm run build
shell:
	flask --app backend/app.py shell
run:
	python backend/app.py