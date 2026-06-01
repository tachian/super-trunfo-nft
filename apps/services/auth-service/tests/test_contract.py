from pathlib import Path

import yaml
from app.main import app


def test_auth_service_openapi_exposes_register_and_login_contracts() -> None:
    openapi = app.openapi()

    register = openapi["paths"]["/auth/register"]["post"]
    login = openapi["paths"]["/auth/login"]["post"]
    profile = openapi["paths"]["/players/me"]["get"]

    assert "requestBody" in register
    assert "requestBody" in login
    assert "201" in register["responses"]
    assert "409" in register["responses"]
    assert "200" in login["responses"]
    assert "401" in login["responses"]
    assert "200" in profile["responses"]
    assert "401" in profile["responses"]


def test_platform_contract_documents_authentication_endpoints() -> None:
    contract = yaml.safe_load(Path("packages/api-contracts/openapi/platform.yaml").read_text())

    register = contract["paths"]["/auth/register"]["post"]
    login = contract["paths"]["/auth/login"]["post"]
    profile = contract["paths"]["/players/me"]["get"]

    assert register["operationId"] == "registerPlayer"
    assert login["operationId"] == "loginPlayer"
    assert profile["operationId"] == "getCurrentPlayerProfile"
    assert "requestBody" in register
    assert "requestBody" in login
    assert "201" in register["responses"]
    assert "200" in login["responses"]
    assert "200" in profile["responses"]
