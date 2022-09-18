# -*- coding: utf-8 -*-
import schemathesis
import pathlib
from hypothesis import settings, HealthCheck


HERE = pathlib.Path(__file__).parent.absolute()
SCHEMA_PATH = HERE.parent / "iscc_web/static/docs/openapi.yaml"
schema = schemathesis.from_path(SCHEMA_PATH, base_url="http://localhost:44555/api/v1")


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
