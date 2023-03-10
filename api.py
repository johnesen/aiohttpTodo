import inspect
import json
from collections import OrderedDict
from models import Todo
from aiohttp.http_exceptions import HttpBadRequest
from aiohttp.web_exceptions import HTTPMethodNotAllowed
from aiohttp.web import Request, Response
from aiohttp.web_urldispatcher import UrlDispatcher
from repositories import TodoRepository
from models import SessionLocal

db = SessionLocal()


DEFAULT_METHODS = ("GET", "POST", "PUT", "DELETE")


class RestEndpoint:
    def __init__(self):
        self.methods = {}

        for method_name in DEFAULT_METHODS:
            method = getattr(self, method_name.lower(), None)
            if method:
                self.register_method(method_name, method)

    def register_method(self, method_name, method):
        self.methods[method_name.upper()] = method

    async def dispatch(self, request: Request):
        method = self.methods.get(request.method.upper())
        if not method:
            raise HTTPMethodNotAllowed("", DEFAULT_METHODS)

        wanted_args = list(inspect.signature(method).parameters.keys())
        available_args = request.match_info.copy()
        available_args.update({"request": request})

        unsatisfied_args = set(wanted_args) - set(available_args.keys())
        if unsatisfied_args:
            raise HttpBadRequest("")

        return await method(
            **{arg_name: available_args[arg_name] for arg_name in wanted_args}
        )


class ListCreateAPI(RestEndpoint):
    def __init__(self, resource):
        super().__init__()
        self.resource = resource

    async def get(self) -> Response:
        return Response(
            status=200,
            body=self.resource.encode(TodoRepository.getTodos(db=db)),
            content_type="application/json",
        )

    async def post(self, request):
        data = await request.json()
        todo = TodoRepository.createTodo(
            db=db,
            user=data.get("user"),
            title=data.get("title"),
            description=data.get("description"),
            is_done=data.get("is_done") or False,
            is_deleted=data.get("is_deleted") or False,
        )
        return Response(
            status=201,
            body=self.resource.encode(
                data=todo
            ),
            content_type="application/json",
        )


class RetrieveUpdateDeleteAPI(RestEndpoint):
    def __init__(self, resource):
        super().__init__()
        self.resource = resource

    async def get(self, instance_id):
        instance = db.query(Todo).filter(Todo.id == instance_id).first()
        if not instance:
            return Response(
                status=404,
                body=json.dumps({"not found": 404}),
                content_type="application/json",
            )
        responseData = {
            "id": instance.id,
            "user": instance.user,
            "title": instance.title,
            "description": instance.description,
            "is_done": instance.is_done,
            "is_deleted": instance.is_deleted,
            "created_at": str(instance.created_at),
        }
        data = self.resource.encode(responseData)
        return Response(status=200, body=data, content_type="application/json")

    async def put(self, request, instance_id):
        data = await request.json()
        todo = db.query(Todo).filter(Todo.id == instance_id).first()
        if todo == None:
            return Response(
                status=404,
                body=json.dumps(
                    {
                        "message": f"Todo with this id: {instance_id} not found",
                        "status": "todo-not-found",
                    },
                    indent=4,
                    ensure_ascii=True,
                ),
                content_type="application/json",
            )
        todo = TodoRepository.updateTodo(db, todo, data=data)
        return Response(
            status=201,
            body=self.resource.encode(todo),
            content_type="application/json",
        )

    async def delete(self, instance_id):
        todo = db.query(Todo).filter(Todo.id == instance_id).first()
        if not todo:
            return Response(
                status=404,
                body=json.dumps(
                    {"message": f"Todo with this id:{instance_id} was not found"},
                    indent=4,
                    ensure_ascii=True,
                ),
                content_type="application/json",
            )
        db.delete(todo)
        db.commit()
        return Response(
            status=200,
            body=json.dumps(
                {"message": "instance succesully deleted"}, indent=4, ensure_ascii=True
            ),
            content_type="application/json",
        )


class RestResource:
    def __init__(self, todo, collection):
        self.todo = todo
        self.collection = collection
        self.collection_endpoint = ListCreateAPI(self)
        self.instance_endpoint = RetrieveUpdateDeleteAPI(self)

    def register(self, router: UrlDispatcher):
        router.add_route(
            "*", "/{todo}".format(todo=self.todo), self.collection_endpoint.dispatch
        )
        router.add_route(
            "*",
            "/{todo}/{{instance_id}}".format(todo=self.todo),
            self.instance_endpoint.dispatch,
        )


    @staticmethod
    def encode(data):
        return json.dumps(data, indent=4, ensure_ascii=True).encode("utf-8")
