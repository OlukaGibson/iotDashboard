python -m venv venv
venv\Scripts\activate

flask db init
flask db migrate -m "Initial migration."
flask db upgrade
flask run