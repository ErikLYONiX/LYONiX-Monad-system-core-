#!/usr/bin/env python3
"""
LYONiX System SLS — Monad Core Engine
======================================
Foundational multi-perspective geometric reasoning engine.

Creator: Erik L. Palmer
License: See LICENSE file in this repository

Design goals
------------
- Fast, NumPy-only multi-view analysis
- Explicit, non-mutating scale transforms
- Grounded mathematical primitives (φ, digital root, vortex cycle, polar)
- Clean extension surface for domain tiers (finance, weather, science, provenance, ...)
- Self-test + micro-benchmark so reviewers can verify claims in seconds

This is the SLS foundation layer. Specialized intelligence tiers are built on top.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from math import sqrt
from typing import Any, Dict, List, Optional, Sequence, Tuple
import time

import numpy as np

# =============================================================================
# Verified mathematical primitives
# =============================================================================

PHI: float = (1.0 + sqrt(5.0)) / 2.0          # golden ratio
PSI: float = (1.0 - sqrt(5.0)) / 2.0
VORTEX_CYCLE: List[int] = [1, 2, 4, 8, 7, 5]  # digital_root(2^n) cycle


def digital_root(n: int) -> int:
    """Digital root with 9 retained for positive multiples of 9; 0 stays 0."""
    if n == 0:
        return 0
    return 1 + (abs(int(n)) - 1) % 9


def polar_complement(n: int) -> int:
    """Polar complement mod 9: d + polar(d) = 9 (with 9 ↔ 9)."""
    d = digital_root(n)
    return 9 if d in (0, 9) else 9 - d


def vortex_weights(length: int) -> np.ndarray:
    """Repeating vortex-cycle weights as a float vector."""
    return np.asarray([VORTEX_CYCLE[i % 6] for i in range(length)], dtype=float)


def phi_scale(data: np.ndarray, power: float = 1.0) -> np.ndarray:
    """Scale array by φ**power (non-mutating)."""
    return np.asarray(data, dtype=float) * (PHI ** power)


# =============================================================================
# Result containers
# =============================================================================

@dataclass
class PerspectiveResult:
    view: str
    insight_score: float
    energy: float
    shape: Tuple[int, ...]
    summary: Dict[str, float] = field(default_factory=dict)


@dataclass
class MultiViewResult:
    perspectives: Dict[str, PerspectiveResult]
    disagreement: float
    consensus_insight: float
    elapsed_ms: float


# =============================================================================
# Monad Geometric Engine
# =============================================================================

class MonadGeometricEngine:
    """
    Multi-perspective geometric reasoning engine.

    Core idea
    ---------
    Analyze the same data under several deterministic transforms
    ("vantage points") and quantify disagreement. High disagreement
    flags instability or regime change; low disagreement flags consensus.

    Vantage points (default)
    ------------------------
    - standard   : identity
    - inside_out : reverse along primary axis
    - boundary   : φ-scaled attenuation (highlights relative structure)
    - long_term  : cumulative mean (trend / integral view)
    - vortex     : element-wise modulation by the vortex cycle weights
    - polar_proxy: sign-aware polar-style fold of rank magnitudes

    Scale handling is explicit and non-mutating: use `scaled_view()`.
    """

    DEFAULT_VIEWS = ("standard", "inside_out", "boundary", "long_term", "vortex", "polar_proxy")

    def __init__(self, views: Optional[Sequence[str]] = None):
        self.vantage_points: List[str] = list(views) if views else list(self.DEFAULT_VIEWS)
        self._history: List[Dict[str, Any]] = []

    # ----- internal transforms (pure) -----------------------------------------

    @staticmethod
    def _as_2d(data: np.ndarray) -> np.ndarray:
        arr = np.asarray(data, dtype=float)
        if arr.ndim == 0:
            return arr.reshape(1, 1)
        if arr.ndim == 1:
            return arr.reshape(-1, 1)
        return arr

    def _transform(self, data: np.ndarray, view: str) -> np.ndarray:
        x = self._as_2d(data)
        if view == "standard":
            return x
        if view == "inside_out":
            return np.flip(x, axis=0)
        if view == "boundary":
            return x * (1.0 / PHI)                    # φ^{-1} attenuation
        if view == "long_term":
            c = np.cumsum(x, axis=0)
            n = np.arange(1, x.shape[0] + 1, dtype=float).reshape(-1, 1)
            return c / n
        if view == "vortex":
            w = vortex_weights(x.shape[0]).reshape(-1, 1)
            return x * w
        if view == "polar_proxy":
            flat = np.abs(x).ravel()
            if flat.size == 0:
                return x
            order = np.argsort(flat)
            ranks = np.empty_like(order, dtype=float)
            ranks[order] = np.linspace(1, 9, flat.size)
            polar_ranks = np.array([polar_complement(int(r)) for r in ranks], dtype=float)
            scale = (polar_ranks / 9.0).reshape(x.shape)
            return np.sign(x) * np.abs(x) * scale
        raise ValueError(f"Unknown view: {view!r}. Valid: {self.vantage_points}")

    @staticmethod
    def _insight(arr: np.ndarray) -> float:
        if arr.size == 0:
            return 0.0
        return float(np.mean(np.abs(arr)))

    @staticmethod
    def _energy(arr: np.ndarray) -> float:
        if arr.size == 0:
            return 0.0
        return float(np.sum(arr * arr))

    # ----- public API ---------------------------------------------------------

    def perspective(self, data: np.ndarray, view: str = "standard") -> PerspectiveResult:
        """Single vantage-point analysis."""
        t = self._transform(data, view)
        return PerspectiveResult(
            view=view,
            insight_score=self._insight(t),
            energy=self._energy(t),
            shape=tuple(t.shape),
            summary={
                "mean": float(np.mean(t)) if t.size else 0.0,
                "std": float(np.std(t)) if t.size else 0.0,
                "max_abs": float(np.max(np.abs(t))) if t.size else 0.0,
            },
        )

    def analyze_multi_view(self, data: np.ndarray) -> MultiViewResult:
        """
        Run all configured vantage points and compute disagreement.

        disagreement = std of insight scores across views
        consensus_insight = mean of insight scores
        """
        t0 = time.perf_counter()
        perspectives: Dict[str, PerspectiveResult] = {}
        insights: List[float] = []
        for view in self.vantage_points:
            res = self.perspective(data, view)
            perspectives[view] = res
            insights.append(res.insight_score)
        elapsed = (time.perf_counter() - t0) * 1000.0
        arr = np.asarray(insights, dtype=float)
        disagreement = float(np.std(arr)) if arr.size else 0.0
        consensus = float(np.mean(arr)) if arr.size else 0.0
        result = MultiViewResult(
            perspectives=perspectives,
            disagreement=disagreement,
            consensus_insight=consensus,
            elapsed_ms=elapsed,
        )
        self._history.append({
            "action": "analyze_multi_view",
            "shape": tuple(np.asarray(data).shape),
            "disagreement": disagreement,
            "elapsed_ms": elapsed,
        })
        return result

    def scaled_view(self, data: np.ndarray, scale_factor: float) -> np.ndarray:
        """Non-mutating scale transform."""
        return np.asarray(data, dtype=float) * float(scale_factor)

    def phi_zoom(self, data: np.ndarray, levels: int = 1) -> np.ndarray:
        """Scale by φ**levels (non-mutating)."""
        return phi_scale(data, power=float(levels))

    def disagreement_series(
        self, series: np.ndarray, window: int = 32
    ) -> np.ndarray:
        """
        Rolling multi-view disagreement on a 1-D series.
        Useful for regime-change / anomaly hints in time-series tiers.
        """
        s = np.asarray(series, dtype=float).ravel()
        if s.size < window:
            mv = self.analyze_multi_view(s)
            return np.array([mv.disagreement])
        out = []
        for i in range(0, s.size - window + 1):
            chunk = s[i : i + window]
            out.append(self.analyze_multi_view(chunk).disagreement)
        return np.asarray(out, dtype=float)

    @property
    def history(self) -> List[Dict[str, Any]]:
        return list(self._history)

    def reset_history(self) -> None:
        self._history.clear()


# =============================================================================
# Self-test + micro-benchmark (reviewer can run: python monad_core.py)
# =============================================================================

def _self_test():
    checks = {}
    checks["phi_identity"] = abs(PHI ** 2 - (PHI + 1)) < 1e-14
    checks["vortex_len"] = VORTEX_CYCLE == [1, 2, 4, 8, 7, 5]
    checks["digital_root_9"] = digital_root(18) == 9
    checks["polar_involution"] = all(
        polar_complement(polar_complement(d)) == d for d in range(1, 10)
    )
    eng = MonadGeometricEngine()
    rng = np.random.default_rng(0)
    data = rng.normal(size=(64, 3))
    mv = eng.analyze_multi_view(data)
    checks["all_views"] = set(mv.perspectives.keys()) == set(eng.vantage_points)
    checks["disagreement_nonneg"] = mv.disagreement >= 0.0
    checks["nonmutating_scale"] = np.allclose(
        eng.scaled_view(data, 2.0), data * 2.0
    )
    checks["history_len"] = len(eng.history) >= 1
    ok = all(checks.values())
    return ok, checks


def _benchmark():
    eng = MonadGeometricEngine()
    rng = np.random.default_rng(1)
    results = {}
    for n in (100, 1000, 10000):
        data = rng.normal(size=(n, 3))
        t0 = time.perf_counter()
        for _ in range(20):
            eng.analyze_multi_view(data)
        elapsed = (time.perf_counter() - t0) / 20 * 1000.0
        results[f"multi_view_{n}x3_ms"] = elapsed
    series = rng.normal(size=2000)
    t0 = time.perf_counter()
    _ = eng.disagreement_series(series, window=64)
    results["rolling_disagreement_2000_ms"] = (time.perf_counter() - t0) * 1000.0
    return results


if __name__ == "__main__":
    print("=" * 70)
    print("  LYONiX System SLS — Monad Core Engine")
    print("  Creator: Erik L. Palmer")
    print("=" * 70)

    ok, checks = _self_test()
    print("\n[Self-test]")
    for k, v in checks.items():
        print(f"  {k:<24} {'PASS' if v else 'FAIL'}")
    print(f"  overall: {'PASS' if ok else 'FAIL'}")

    print("\n[Micro-benchmark]")
    bench = _benchmark()
    for k, v in bench.items():
        print(f"  {k:<32} {v:8.3f} ms")

    print("\n[Demo — multi-view on synthetic series]")
    eng = MonadGeometricEngine()
    demo = np.random.default_rng(2).normal(size=(120, 1))
    mv = eng.analyze_multi_view(demo)
    print(f"  consensus_insight = {mv.consensus_insight:.4f}")
    print(f"  disagreement      = {mv.disagreement:.4f}")
    print(f"  elapsed           = {mv.elapsed_ms:.3f} ms")
    for name, res in mv.perspectives.items():
        print(f"    {name:<12} insight={res.insight_score:.4f}  energy={res.energy:.2f}")

    print("\n" + "=" * 70)
    print("  Status: foundation ready for domain-tier extensions")
    print("=" * 70)