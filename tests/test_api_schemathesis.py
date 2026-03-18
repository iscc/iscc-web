# -*- coding: utf-8 -*-
import schemathesis.openapi
import pathlib
from schemathesis import Config
from schemathesis.config._projects import HealthCheck
from schemathesis.checks import not_a_server_error

HERE = pathlib.Path(__file__).parent.absolute()
SCHEMA_PATH = HERE.parent / "iscc_web/static/docs/openapi.yaml"
schema = schemathesis.openapi.from_path(
    SCHEMA_PATH,
    config=Config(suppress_health_check=[HealthCheck.too_slow]),
)
schema.location = "http://localhost:44555/api/v1"


@schema.parametrize()
def test_api(case):
    case.call_and_validate(checks=[not_a_server_error])
