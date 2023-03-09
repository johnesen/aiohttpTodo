from aiohttp.web import Application, run_app

from api import RestResource
from models import Todo, Base, engine
from sqlalchemy import engine_from_config


Base.metadata.create_all(bind=engine)
todo = {}
app = Application()
person_resource = RestResource("todo", todo)
person_resource.register(app.router)

if __name__ == "__main__":
    run_app(app)
