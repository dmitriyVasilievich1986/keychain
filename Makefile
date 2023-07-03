build_run: build run

build:
	cd frontend; npm run build
shell:
	./venv/bin/flask --app backend/app.py shell
run:
	./venv/bin/python backend/app.py