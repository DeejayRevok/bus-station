class HandlerNotFoundForQuery(Exception):
    def __init__(self, query_name: str):
        self.query_name = query_name
        super(HandlerNotFoundForQuery, self).__init__(f"Handler for query {query_name} not found")
