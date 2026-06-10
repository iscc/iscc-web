# -*- coding: utf-8 -*-
import schemathesis
import pathlib
from hypothesis import settings, HealthCheck

from tests.conftest import server_host, server_port, server_api_path


HERE = pathlib.Path(__file__).parent.absolute()
SCHEMA_PATH = HERE.parent / "iscc_web/static/docs/openapi.yaml"
schema = schemathesis.from_path(SCHEMA_PATH, base_url=f"http://{server_host}:{server_port}/{server_api_path}")


schema.add_link(
    source=schema["/media"]["POST"],
    target=schema["/media/{media_id}"]["GET"],
    status_code="201",
    parameters={"media_id": "$response.body#/media_id"},
)

schema.add_link(
    source=schema["/media"]["POST"],
    target=schema["/metadata/{media_id}"]["GET"],
    status_code="201",
    parameters={"media_id": "$response.body#/media_id"},
)


@settings(suppress_health_check=[HealthCheck(2)])
@schema.parametrize()
def test_api(case):
    case.call_and_validate()
