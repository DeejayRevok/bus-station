import json

from bus_station.query_terminal.query_response import QueryResponse
from bus_station.query_terminal.serialization.query_response_deserializer import QueryResponseDeserializer


class QueryResponseJSONDeserializer(QueryResponseDeserializer):
    def deserialize(self, query_response_serialized: str) -> QueryResponse:
        query_response_dict = json.loads(query_response_serialized)
        return QueryResponse(data=query_response_dict.get("data"))
