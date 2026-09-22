from ferrox_py.core.provider import injectable
import strawberry
from strawberry.fastapi import GraphQLRouter
from fastapi import FastAPI

@injectable()
class GraphQLTransport:
    def setup(self, app: FastAPI, query_cls, mutation_cls=None):
        schema = strawberry.Schema(query=query_cls, mutation=mutation_cls)
        graphql_app = GraphQLRouter(schema)
        app.include_router(graphql_app, prefix="/graphql")
