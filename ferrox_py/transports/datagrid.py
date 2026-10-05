from ferrox_py.core.provider import injectable
from typing import Any, Callable, Dict, List, Optional, Type, Set, cast, AsyncGenerator, Any, Callable, Dict, List, Optional, Type, Set, cast, AsyncGenerator, Dict, Any, List

class DataGridQuery:
    def __init__(self, skip: int, take: int, filters: List[Dict[Any, Any]], sort: Dict[str, int]) -> None:
        self.skip = skip
        self.take = take
        self.filters = filters
        self.sort = sort

@injectable()
class DataGridHelper:
    def parse_query(self, query_params: Dict[Any, Any]) -> DataGridQuery:
        """
        Parses generic query params into a structured AST for database projection.
        Example query: ?skip=0&take=20&sort=name:-1&filter=status:eq:active
        """
        skip = int(query_params.get("skip", 0))
        take = int(query_params.get("take", 10))
        
        sort = {}
        if "sort" in query_params:
            for s in query_params["sort"].split(","):
                field, direction = s.split(":")
                sort[field] = int(direction)
                
        filters = []
        if "filter" in query_params:
            for f in query_params["filter"].split(","):
                field, op, val = f.split(":")
                filters.append({"field": field, "operator": op, "value": val})
                
        return DataGridQuery(skip=skip, take=take, filters=filters, sort=sort)
