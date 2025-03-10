MAIN_FILE_PATH = src/main.py
#
# debug: setup run-debug
#
#
# setup:
# 	source $(pwd)/.venv/bin/activate
#
run:
	# flask --app $(MAIN_FILE_PATH) run
	cd ./src/; gunicorn -b 0.0.0.0 'main:app'

run-debug:
	flask --app $(MAIN_FILE_PATH) --debug run

clear-db:
	rm ~/.local/share/naught/todo/db.sqlite3
