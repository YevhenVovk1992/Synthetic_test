import os
import dotenv
from flask import Flask

import database


# Loading environment variables into the project
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
dotenv.load_dotenv(dotenv_path)

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.environ.get('SESSION_SECRET')


# This function closes the connection to the database after the view function is executed
@app.teardown_appcontext
def shutdown_session(exception=None) -> None:
    database.db_session.remove()


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
