import os
from dataclasses import dataclass


@dataclass(frozen=True)
class NftFeatureFlags:
    blockchain_enabled: bool = False


def nft_feature_flags_from_environment() -> NftFeatureFlags:
    return NftFeatureFlags(
        blockchain_enabled=_enabled(os.getenv("FEATURE_NFT_ENABLED", "false"))
    )


def _enabled(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "on"}
