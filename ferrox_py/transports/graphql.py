from typing import Any

import strawberry
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from ferrox_py.core.provider import injectable


@injectable()
class GraphQLTransport:
    def setup(self, app: FastAPI, query_cls, mutation_cls=None) -> Any:  # type: ignore
        schema = strawberry.Schema(query=query_cls, mutation=mutation_cls)
        graphql_app = GraphQLRouter(schema)
        app.include_router(graphql_app, prefix="/graphql")
