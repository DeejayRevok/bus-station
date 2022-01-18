class HandlerForQueryAlreadyRegistered(Exception):
    def __init__(self, query_name: str):
        self.query_name = query_name
        super(HandlerForQueryAlreadyRegistered, self).__init__(f"Handler for query {query_name} already registered")
