# Json API for Synthetic
### TODO list
Link - 
___

___
### What I do?
Technologies used: Flask, Alembic, SQLAlchemy, Postgres

API URLS:
	/todo/api/v1.0/board (method GET) - get a list of boards
	/todo/api/v1.0/tasks (method GET) - get a list of tasks
	/todo/api/v1.0/tasks (method POST) - create task (json data {"text": "Create new task","board_id": "2"})
	/todo/api/v1.0/tasks?status=true (method GET) - get a list of tasks with the filter by status
	/todo/api/v1.0/tasks?board=1 (method GET) - get a list of tasks with the filter by board
	/todo/api/v1.0/tasks/2 (method GET) - get the task by ID
	/todo/api/v1.0/tasks/<int:id_task> (method PUT) - update status of the task by ID (json data {"status": "true"})
	/todo/api/v1.0/tasks/<int:id_task> (method DELETE) - DELETE the task by ID 
	

___
### How to start project?
1. pip install -r requerements.txt;
2. Create .env file and write to it enviroment variables:
	- SESSION_SECRET
	- DB_CONNECT (postgresql+psycopg2://user:password@host:port/synthetic)
	- POSTGRES_PASSWORD	
3. Run 'docker-compose up -d'to make a container for the whole application and database;
4. Create 'synthetic' database and run 'alembic upgrade head';
5. Run app.py
