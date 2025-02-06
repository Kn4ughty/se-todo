MAIN_FILE_PATH = src/main.py



run:
	flask --app $(MAIN_FILE_PATH) run

run-debug:
	flask --app $(MAIN_FILE_PATH) --debug run

