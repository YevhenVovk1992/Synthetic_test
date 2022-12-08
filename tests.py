import os
import unittest
import unittest.mock
import app
import database
import tempfile

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

import models


class APITestCase(unittest.TestCase):
    class DatabaseMock:
        pass

    def setUp(self):
        self.engine = create_engine('sqlite:///:memory:')
        self.session = scoped_session(sessionmaker(autocommit=False,
                                                   autoflush=False,
                                                   bind=self.engine))
        database.Base.query = self.session.query_property()
        database.Base.metadata.create_all(bind=self.engine)

        self.db_fd, app.app.config['DATABASE'] = tempfile.mkstemp()
        app.app.config['TESTING'] = True
        self.app = app.app.test_client()
        with app.app.app_context():
            database.init_db()

        board = models.Board(
            status='OPEN'
        )
        task1 = models.Task(
            status=False,
            text="TEST TEXT",
            board_id=1
        )
        task2 = models.Task(
            status=True,
            text="TEST TEXT",
            board_id=1
        )
        self.session.add(board)
        self.session.add(task1)
        self.session.add(task2)
        self.session.commit()

    def tearDown(self):
        self.session.remove()
        os.close(self.db_fd)
        os.unlink(app.app.config['DATABASE'])

    def test_get_boards(self):
        rv = self.app.get('/todo/api/v1.0/board')
        self.assertEqual(rv.status_code, 200)
        self.assertNotEqual(len(rv.json), 0)

    def test_get_tasks(self):
        rv = self.app.get('/todo/api/v1.0/tasks')
        self.assertEqual(len(rv.json), 2)
        self.assertEqual(rv.status_code, 200)

    def test_get_tasks_with_status(self):
        rv = self.app.get('todo/api/v1.0/tasks?status=False')
        data = rv.json
        self.assertEqual(data[0]['status'], False)
        self.assertEqual(rv.status_code, 200)

    def test_get_tasks_with_board_id(self):
        rv = self.app.get('/todo/api/v1.0/tasks?board=1')
        data = rv.json
        self.assertEqual(data[0]['board_id'], 1)
        self.assertEqual(rv.status_code, 200)

    def test_get_tasks_with_board_id_error_1(self):
        rv = self.app.get('/todo/api/v1.0/tasks?board=99999999')
        self.assertEqual(rv.status_code, 400)

    def test_get_tasks_with_board_id_error_2(self):
        rv = self.app.get('/todo/api/v1.0/tasks?board=1.2')
        data = rv.json
        self.assertEqual(rv.status_code, 500)
        self.assertEqual(data['error'], 'board must be integer')

    def test_get_tasks_with_query_error(self):
        rv = self.app.get('/todo/api/v1.0/tasks?accord=999')
        self.assertEqual(rv.status_code, 400)

    def test_get_tasks_with_status_error(self):
        rv = self.app.get('/todo/api/v1.0/tasks?status=1')
        self.assertEqual(rv.status_code, 400)

    @unittest.mock.patch('database.db_session.commit', DatabaseMock)
    def test_create_task(self):
        rv = self.app.post('/todo/api/v1.0/tasks', json={"text": "Create test task", "board_id": "1"})
        self.assertEqual(rv.status_code, 201)

    def test_create_task_error_empty_json(self):
        rv = self.app.post('/todo/api/v1.0/tasks', json={})
        self.assertEqual(rv.status_code, 400)

    def test_create_task_error_json(self):
        rv = self.app.post('/todo/api/v1.0/tasks', json={"text_1": "Create new task", "board_id": "2"})
        self.assertEqual(rv.status_code, 400)

    def test_create_task_error_board_id(self):
        rv = self.app.post('/todo/api/v1.0/tasks', json={"text": "Create 2 new task", "board_id": '999999'})
        self.assertEqual(rv.status_code, 500)

    def test_get_tasks_with_id(self):
        rv = self.app.get('/todo/api/v1.0/tasks/1')
        self.assertEqual(rv.status_code, 200)

    def test_get_tasks_with_error_id(self):
        rv = self.app.get('/todo/api/v1.0/tasks/99999')
        self.assertEqual(rv.status_code, 404)

    def test_update_task(self):
        task = models.Task.query.filter_by(id=1).first()
        status = task.status
        self.assertFalse(status)
        rv = self.app.put('/todo/api/v1.0/tasks/1', json={"status": "true"})
        task2 = models.Task.query.filter_by(id=1).first()
        new_status = task2.status
        self.assertTrue(new_status)
        self.assertEqual(rv.status_code, 204)

    def test_update_task_empty_json(self):
        rv = self.app.put('/todo/api/v1.0/tasks/1', json={})
        self.assertEqual(rv.status_code, 400)

    def test_update_task_error_json(self):
        rv = self.app.put('/todo/api/v1.0/tasks/1', json={"status": "TRUE1"})
        self.assertEqual(rv.status_code, 400)

    @unittest.mock.patch('database.db_session.commit', DatabaseMock)
    def test_delete_task(self):
        task = models.Task(
            text='TEST',
            board_id=1
        )
        self.session.add(task)
        self.session.commit()
        id_task = task.id
        rv = self.app.delete(f'/todo/api/v1.0/tasks/{id_task}')
        self.assertEqual(rv.status_code, 204)

    def test_delete_task_error(self):
        rv = self.app.delete(f'/todo/api/v1.0/tasks/99999999')
        self.assertEqual(rv.status_code, 404)


if __name__ == '__main__':
    unittest.main()
