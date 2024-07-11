python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

flask db init
flask db migrate -m "Initial migration."
flask db upgrade
flask run