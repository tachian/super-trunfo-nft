from __future__ import annotations

import json
import os
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from time import perf_counter
from uuid import UUID

ROOT = Path(__file__).resolve().parents[1]
MATCHMAKING_SRC = ROOT / "apps" / "services" / "matchmaking-service" / "src"

sys.path.insert(0, str(MATCHMAKING_SRC))

from app.application.use_cases import RequestMatch, RequestMatchCommand  # noqa: E402
from app.infrastructure.repositories import (  # noqa: E402
    InMemoryMatchmakingEventPublisher,
    InMemoryMatchmakingQueueRepository,
)

DEFAULT_REQUESTS = 1_000
DEFAULT_MAX_AVERAGE_MS = 5.0
DEFAULT_MAX_P95_MS = 20.0


@dataclass(frozen=True)
class MatchmakingLoadResult:
    requests: int
    queued: int
    matched: int
    pve_created: int
    total_ms: float
    average_ms: float
    p95_ms: float


def main() -> int:
    request_count = configured_int("MATCHMAKING_LOAD_REQUESTS", DEFAULT_REQUESTS)
    max_average_ms = configured_float(
        "MATCHMAKING_LOAD_MAX_AVERAGE_MS",
        DEFAULT_MAX_AVERAGE_MS,
    )
    max_p95_ms = configured_float("MATCHMAKING_LOAD_MAX_P95_MS", DEFAULT_MAX_P95_MS)

    result = run_load_scenario(request_count)

    print(json.dumps(asdict(result), sort_keys=True))

    if result.average_ms > max_average_ms:
        print(
            f"Average matchmaking latency {result.average_ms:.4f}ms exceeded "
            f"{max_average_ms:.4f}ms.",
            file=sys.stderr,
        )
        return 1

    if result.p95_ms > max_p95_ms:
        print(
            f"P95 matchmaking latency {result.p95_ms:.4f}ms exceeded "
            f"{max_p95_ms:.4f}ms.",
            file=sys.stderr,
        )
        return 1

    return 0


def run_load_scenario(request_count: int) -> MatchmakingLoadResult:
    if request_count < 2:
        raise ValueError("request_count must be greater than or equal to 2")

    if request_count % 2 != 0:
        raise ValueError("request_count must be even to keep deterministic pair counts")

    repository = InMemoryMatchmakingQueueRepository()
    event_publisher = InMemoryMatchmakingEventPublisher()
    use_case = RequestMatch(repository, event_publisher)
    latencies_ms: list[float] = []
    status_counts = {"queued": 0, "matched": 0, "pve_created": 0}
    scenario_start = perf_counter()

    for index in range(request_count):
        level_pair = index // 2
        average_deck_level = 320 + (level_pair % 10)
        request_start = perf_counter()
        result = use_case.execute(
            RequestMatchCommand(
                player_id=UUID(int=index + 1),
                average_deck_level=average_deck_level,
                fallback_after_seconds=10,
            )
        )
        latencies_ms.append((perf_counter() - request_start) * 1_000)
        status_counts[result.status] += 1

    total_ms = (perf_counter() - scenario_start) * 1_000
    expected_pairs = request_count // 2

    if status_counts["queued"] != expected_pairs or status_counts["matched"] != expected_pairs:
        raise AssertionError(
            "load scenario must produce one queued request and one matched request per pair"
        )

    if status_counts["pve_created"] != 0:
        raise AssertionError("load scenario must not create PvE fallback matches")

    return MatchmakingLoadResult(
        requests=request_count,
        queued=status_counts["queued"],
        matched=status_counts["matched"],
        pve_created=status_counts["pve_created"],
        total_ms=round(total_ms, 4),
        average_ms=round(sum(latencies_ms) / len(latencies_ms), 4),
        p95_ms=round(percentile(latencies_ms, 95), 4),
    )


def percentile(values: list[float], percentile_value: int) -> float:
    ordered_values = sorted(values)
    index = round((percentile_value / 100) * (len(ordered_values) - 1))
    return ordered_values[index]


def configured_int(name: str, default: int) -> int:
    return int(os.getenv(name, str(default)))


def configured_float(name: str, default: float) -> float:
    return float(os.getenv(name, str(default)))


if __name__ == "__main__":
    raise SystemExit(main())
