from super_trunfo_shared.observability import mask_sensitive_data


def test_masks_sensitive_values_recursively() -> None:
    payload = {
        "email": "tachian@example.com",
        "cpf": "123.456.789-10",
        "telefone": "+55 85 99999-1234",
        "celular": "+55 85 88888-4321",
        "full_name": "Tachian Silva",
        "password": "super-secret",
        "nested": [{"token": "abc"}],
    }

    masked = mask_sensitive_data(payload)

    assert masked["email"] == "t***@example.com"
    assert masked["cpf"] == "***.***.***-10"
    assert masked["telefone"] == "***********34"
    assert masked["celular"] == "***********21"
    assert masked["full_name"] == "T*** S***"
    assert masked["password"] == "[REDACTED]"
    assert masked["nested"][0]["token"] == "[REDACTED]"
