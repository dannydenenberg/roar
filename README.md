# Roar
A tweeting app (clone) made with [Flask](https://flask.palletsprojects.com/en/2.0.x/).

When adding to git, do NOT include `venv` and `__pycache__`. Run `pip freeze > requirements.txt` to get all of your dependencies into a requirements file and DO include that.

The `@click.command("init-db")` decorator makes a function call when you type: `flask init-db`. Do this to initialize the database for the first time (it wipes previous data).

The `url_for("auth.login")` is for the "auth" blueprint and the `login` function.

To read in the database and interact with it:
- Run `sqlite3 database.sqlite`.
- Run `.mode column` and `.headers on`
- Then run your query: `select * from users;` etc..

Make sure when running JavaScript inside of a .html file, it gets put inside a block. It won't get run otherwise.

### Running

1. `cd` into the main directory.
2. Create and initialize a virtual enviornment with `python3 -m venv venv` and `. venv/bin/activate`.
3. Install the dependencies with `pip install -r requirements.txt`.
4. If you are running the program for the first time and don't have the database set up, run `flask init-db`.
5. Run the program! `flask run`.
6. (extra step>) If you want to run the application on the url `localhost`, do this: `flask run --host=0.0.0.0 --port=80`.
