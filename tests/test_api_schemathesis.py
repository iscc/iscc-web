# -*- coding: utf-8 -*-
import pathlib

import schemathesis.openapi
from schemathesis import Config
from schemathesis.checks import not_a_server_error
from schemathesis.config import HealthCheck

from tests.conftest import server_api_path, server_host, server_port


HERE = pathlib.Path(__file__).parent.absolute()
SCHEMA_PATH = HERE.parent / "iscc_web/static/docs/openapi.yaml"
schema = schemathesis.openapi.from_path(
    SCHEMA_PATH,
    config=Config(suppress_health_check=[HealthCheck.too_slow]),
)
schema.location = f"http://{server_host}:{server_port}/{server_api_path}"


@schema.parametrize()
def test_api(case):
    # Generous request timeout: first /iscc and /simprint calls warm up SDK imports and ONNX
    # models in the pool worker, which can exceed the 10s default under parallel test load.
    case.call_and_validate(checks=[not_a_server_error], timeout=60)
