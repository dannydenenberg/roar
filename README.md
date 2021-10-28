# Roar
A tweeting app (clone) made with [Flask](https://flask.palletsprojects.com/en/2.0.x/).

When adding to git, do NOT include `venv` and `__pycache__`. Run `pip freeze > requirements.txt` to get all of your dependencies into a requirements file and DO include that.

The `@click.command("init-db")` decorator makes a function call when you type: `flask init-db`. Do this to initialize the database for the first time (it wipes previous data).

### Running

1. `cd` into the main directory.
2. Create and initialize a virtual enviornment with `python3 -m venv venv` and `. venv/bin/activate`.
3. Install the dependencies with `pip install -r requirements.txt`.
4. If you are running the program for the first time and don't have the database set up, run `flask init-db`.
5. Run the program! `flask run`.
