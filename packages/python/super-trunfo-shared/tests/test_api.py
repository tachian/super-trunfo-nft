from super_trunfo_shared.api import cors_origins_from_environment


def test_cors_origins_are_empty_by_default(monkeypatch) -> None:
    monkeypatch.delenv("SUPER_TRUNFO_CORS_ORIGINS", raising=False)

    assert cors_origins_from_environment() == []


def test_cors_origins_can_be_configured_for_local_development(monkeypatch) -> None:
    monkeypatch.setenv(
        "SUPER_TRUNFO_CORS_ORIGINS",
        "http://localhost:3000, http://127.0.0.1:3000",
    )

    assert cors_origins_from_environment() == [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]
