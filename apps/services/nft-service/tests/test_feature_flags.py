from app.config import NftFeatureFlags, nft_feature_flags_from_environment


def test_nft_feature_flag_defaults_to_disabled(monkeypatch) -> None:
    monkeypatch.delenv("FEATURE_NFT_ENABLED", raising=False)

    flags = nft_feature_flags_from_environment()

    assert flags == NftFeatureFlags(blockchain_enabled=False)


def test_nft_feature_flag_accepts_enabled_values(monkeypatch) -> None:
    monkeypatch.setenv("FEATURE_NFT_ENABLED", "true")

    flags = nft_feature_flags_from_environment()

    assert flags.blockchain_enabled is True


def test_nft_feature_flag_rejects_unknown_values(monkeypatch) -> None:
    monkeypatch.setenv("FEATURE_NFT_ENABLED", "definitely")

    flags = nft_feature_flags_from_environment()

    assert flags.blockchain_enabled is False
