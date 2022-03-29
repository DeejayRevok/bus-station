import json
from dataclasses import asdict

from bus_station.query_terminal.query_response import QueryResponse
from bus_station.query_terminal.serialization.query_response_serializer import QueryResponseSerializer


class QueryResponseJSONSerializer(QueryResponseSerializer):
    def serialize(self, query_response: QueryResponse) -> str:
        return json.dumps(asdict(query_response))
