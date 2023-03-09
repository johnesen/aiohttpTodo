from models import Todo
from datetime import datetime


class TodoRepository:
    @classmethod
    def createTodo(cls, db, user, title, description, is_done, is_deleted):
        todoInstace = Todo(
            user=user,
            title=title,
            description=description,
            created_at=datetime.now(),
            is_done=is_done,
            is_deleted=is_deleted,
        )
        db.add(todoInstace)
        db.commit()
        responseData = {
            "id": todoInstace.id,
            "user": todoInstace.user,
            "title": todoInstace.title,
            "description": todoInstace.description,
            "created_at": str(todoInstace.created_at),
            "is_done": todoInstace.is_done,
            "is_deleted": todoInstace.is_deleted,
        }
        return responseData

    @classmethod
    def getTodos(cls, db):
        responseData = [
            {
                "id": todo.id,
                "user": todo.user,
                "title": todo.title,
                "description": todo.description,
                "is_done": todo.is_done,
                "is_deleted": todo.is_deleted,
                "created_at": str(todo.created_at),
            }
            for todo in db.query(Todo).filter(Todo.is_deleted == False)
        ]
        return responseData

    @classmethod
    def updateTodo(cls, db, todo: Todo, data):
        todo.title = data.get("title") if data.get("title") is not None else todo.tilte
        todo.description = (
            data.get("description")
            if data.get("description") is not None
            else todo.description
        )
        todo.user = data.get("user") if data.get("user") is not None else todo.user

        db.add(todo)
        db.commit()
        responseData = {
            "id": todo.id,
            "user": todo.user,
            "title": todo.title,
            "description": todo.description,
            "is_done": todo.is_done,
            "is_deleted": todo.is_deleted,
            "created_at": str(todo.created_at),
        }
        return responseData