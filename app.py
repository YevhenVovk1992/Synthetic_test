import os
import dotenv

from flask import Flask, jsonify, request

import database
import models

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


@app.route('/todo/api/v1.0/')
def hello_world():
    return 'Hello World!'


@app.route('/todo/api/v1.0/board', methods=['GET'])
def get_boards():
    database.init_db()
    board_list = models.Board.query.all()
    return jsonify([item.to_dict() for item in board_list])


@app.route('/todo/api/v1.0/tasks', methods=['GET', 'POST'])
def get_tasks():
    if request.method == "GET":
        task_list = models.Task.query.all()
        return jsonify([item.to_dict() for item in task_list])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
