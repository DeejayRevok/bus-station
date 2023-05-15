class QueryHandlerNotFound(Exception):
    def __init__(self, query_handler_name: str):
        self.query_handler_name = query_handler_name
        super().__init__(f"Query handler {query_handler_name} not found")
