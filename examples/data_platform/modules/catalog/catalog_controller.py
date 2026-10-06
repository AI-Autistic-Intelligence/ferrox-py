from ferrox_py.core.container import Container
from ferrox_py.core.controllers import BaseController
from ferrox_py.databases.mongodb import MongoService
from ferrox_py.transports.datagrid import DataGridHelper


class CatalogController(BaseController):
    def __init__(self, container: Container):
        super().__init__(prefix="/catalog", tags=["Catalog"])
        self.container = container
        
        # Lazy dependency injection
        # (In a real app, container resolves these automatically via @module)
        self.datagrid = DataGridHelper()
        self.mongo = MongoService()
        
        @self.router.get("/datasets")
        async def list_datasets(skip: int = 0, take: int = 10, sort: str = None, filter: str = None):
            """
            Queries the Data Catalog metadata using DataGrid abstractions.
            """
            query_params = {"skip": skip, "take": take}
            if sort: query_params["sort"] = sort
            if filter: query_params["filter"] = filter
                
            ast = self.datagrid.parse_query(query_params)
            
            # Simulated Mongo cursor execution
            # db = self.mongo.get_database("data_platform")
            # cursor = db.catalog.find(ast.filters).skip(ast.skip).limit(ast.take)
            
            return self.ok({
                "query_ast": {
                    "skip": ast.skip,
                    "take": ast.take,
                    "filters": ast.filters,
                    "sort": ast.sort
                },
                "results": ["dataset_weather", "dataset_finance"]
            }, "Catalog queried successfully")
