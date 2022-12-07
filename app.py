import os
from typing import Union

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


@app.errorhandler(400)
def not_found(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)


def get_task_or_404(task_id: int):
    task = models.Task.query.filter_by(id=task_id).first()
    if not task:
        abort(404)
    return task


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
        if not filter_param:
            task_list = models.Task.query.all()
        else:
            if 'status' in filter_param:
                get_status = filter_param['status']
                task_list = models.Task.query.filter_by(
                    status=get_status).all() if get_status in ('true', 'false') else []
            elif 'board' in filter_param:
                try:
                    board_id = int(filter_param['board'])
                except ValueError:
                    return jsonify({'error': 'board must be integer'}), 500
                task_list = models.Task.query.filter_by(board_id=board_id).all()
            if not task_list:
                abort(400)
        return jsonify([item.to_dict() for item in task_list])

    if request.method == "POST":
        create_data = dict(request.get_json())
        if not create_data:
            abort(400)
        else:
            if 'text' not in create_data or 'board_id' not in create_data:
                abort(400)
        all_board = [itm.id for itm in models.Board.query.all()]
        get_text = create_data.get('text')
        get_board_id = create_data.get('board_id')
        if get_board_id not in all_board:
            return jsonify({'error': 'board_id not in DB'}), 500
        new_task = models.Task(
            text=get_text,
            board_id=get_board_id
        )
        try:
            database.db_session.add(new_task)
            database.db_session.commit()
        except Exception as error:
            return jsonify(error=str(error)), 502
        return jsonify(new_task.to_dict()), 201


@app.get('/todo/api/v1.0/tasks/<int:id_task>')
def get_one_task(id_task: int):
    database.init_db()
    get_task = get_task_or_404(id_task)
    return jsonify(get_task.to_dict())


@app.put('/todo/api/v1.0/tasks/<int:id_task>')
def update_task(id_task):
    database.init_db()
    get_task = get_task_or_404(id_task)
    new_status = request.get_json().get('status', None)
    if not new_status:
        abort(400)
    get_task.status = bool(new_status) if new_status in ('true', 'false') else abort(400)
    try:
        database.db_session.add(get_task)
        database.db_session.commit()
    except Exception as error:
        return jsonify(error=str(error)), 502
    return jsonify(get_task.to_dict()), 204


@app.delete('/todo/api/v1.0/tasks/<int:id_task>')
def delete_task(id_task):
    database.init_db()
    get_task = get_task_or_404(id_task)
    try:
        database.db_session.delete(get_task)
        database.db_session.commit()
    except Exception as error:
        return jsonify(error=str(error)), 502
    return jsonify(delete_task=id_task), 204


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
