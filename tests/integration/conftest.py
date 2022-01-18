import os
from os.path import dirname
from kombu import Connection

import pytest


def kombu_connection_checker(connection_str: str) -> bool:
    try:
        connection = Connection(connection_str)
        connection.connect()
    except Exception:
        return False

    connection.release()
    return True


@pytest.fixture(scope="session")
def docker_compose_file(pytestconfig):
    return os.path.join(dirname(__file__), "resources", "docker-compose.yml")


@pytest.fixture(scope="session")
def rabbitmq(docker_ip, docker_services):
    port = docker_services.port_for("rabbitmq", 5672)
    url = f"amqp://guest:guest@{docker_ip}:{port}//"
    docker_services.wait_until_responsive(timeout=60.0, pause=0.1, check=lambda: kombu_connection_checker(url))
    return {"user": "guest", "password": "guest", "host": docker_ip, "port": port}


@pytest.fixture(scope="session")
def redis(docker_ip, docker_services):
    port = docker_services.port_for("redis", 6379)
    url = f"redis://{docker_ip}:{port}"
    docker_services.wait_until_responsive(timeout=60.0, pause=0.1, check=lambda: kombu_connection_checker(url))
    return {"host": docker_ip, "port": port}


@pytest.fixture(scope="session")
def postgres(docker_ip, docker_services):
    port = docker_services.port_for("postgres", 5432)
    return {"host": docker_ip, "port": port, "user": "test_user", "password": "test_password", "db": "test_db"}


@pytest.fixture(scope="session")
def mongo(docker_ip, docker_services):
    port = docker_services.port_for("mongo", 27017)
    return {"host": docker_ip, "port": port, "user": "test_user", "password": "test_password", "db": "test_db"}


@pytest.fixture(scope="class", autouse=True)
def add_container_services_data(request, rabbitmq: dict, redis: dict, postgres: dict, mongo: dict):
    request.cls.rabbitmq = rabbitmq
    request.cls.redis = redis
    request.cls.postgres = postgres
    request.cls.mongo = mongo
