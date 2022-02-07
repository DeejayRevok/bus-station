from bus_station.query_terminal.query import Query


class QueryExecutionFailed(Exception):
    def __init__(self, query: Query, reason: str):
        self.query = query
        self.reason = reason
        super().__init__(f"{query} execution has failed due to {reason}")
