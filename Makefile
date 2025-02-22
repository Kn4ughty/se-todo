MAIN_FILE_PATH = src/main.py



run:
	# flask --app $(MAIN_FILE_PATH) run
	cd ./src/; gunicorn 'main:app'

run-debug:
	flask --app $(MAIN_FILE_PATH) --debug run

clear-db:
	rm ~/.local/share/naught/todo/db.sqlite3
