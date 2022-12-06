import os
import dotenv

from flask import Flask, jsonify, request, abort, make_response

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


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/todo/api/v1.0/board', methods=['GET'])
def get_boards():
    database.init_db()
    board_list = models.Board.query.all()
    return jsonify([item.to_dict() for item in board_list])


@app.route('/todo/api/v1.0/tasks', methods=['GET', 'POST'])
def get_tasks():
    database.init_db()
    if request.method == "GET":
        task_list = []
        filter_param = dict(request.values)
        if filter_param and 'status' in filter_param:
            task_list = models.Task.query.filter_by(status=filter_param['status']).all()
        elif filter_param and 'board' in filter_param:
            task_list = models.Task.query.filter_by(board_id=filter_param['board']).all()
        else:
            abort(400)
        if not filter_param:
            task_list = models.Task.query.all()
        return jsonify([item.to_dict() for item in task_list])
    if request.method == "POST":
        create_data = dict(request.get_json())
        if not create_data:
            abort(400)
        else:
            if 'text' not in create_data and 'board_id' not in create_data:
                abort(400)
        new_task = models.Task(
            text=create_data.get('text'),
            board_id=create_data.get('board_id')
        )
        try:
            database.db_session.add(new_task)
            database.db_session.commit()
        except Exception as error:
            return jsonify(error=str(error))
        return jsonify(new_task.to_dict()), 201


@app.get('/todo/api/v1.0/tasks/<int:id_task>')
def get_one_task(id_task: int):
    database.init_db()
    get_task = models.Task.query.filter_by(id=id_task).first()
    if not get_task:
        abort(404)
    return jsonify(get_task.to_dict())


@app.put('/todo/api/v1.0/tasks/<int:id_task>')
def update_task(id_task):
    database.init_db()
    get_task = models.Task.query.filter_by(id=id_task).first()
    if not get_task:
        abort(404)
    new_status = request.get_json().get('status', None)
    if not new_status:
        abort(400)
    get_task.status = bool(new_status)
    database.db_session.add(get_task)
    database.db_session.commit()
    return jsonify(get_task.to_dict())


@app.delete('/todo/api/v1.0/tasks/<int:id_task>')
def delete_task(id_task):
    database.init_db()
    get_task = models.Task.query.filter_by(id=id_task).first()
    if not get_task:
        abort(404)
    database.db_session.delete(get_task)
    database.db_session.commit()
    return jsonify(delete_task=id_task)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
