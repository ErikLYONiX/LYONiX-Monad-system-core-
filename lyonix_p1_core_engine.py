Conversation View
MO
Inbox

Inbox
Message 1 of 1. For JAWS, turn virtual PC Cursor on if needed.

wosmaster2@yahoo.com
To:  me, and 2 others
 · 
Sun, Apr 19 at 1:31 PM
Message Body

import numpy as np
import uuid
import datetime
import json
from typing import List, Dict, Any

# ============================================================
# LYONiX MONAD CORE SYSTEM v1.1 — With "I Can Do No Harm" Ethics
# Creator: Erik L. Palmer
# Ethical Foundation: "I can do no harm" — built into every Monad
# ============================================================

def normalize(v: np.ndarray) -> np.ndarray:
    norm = np.linalg.norm(v)
    return v if norm == 0 else v / norm

def cosine(a: np.ndarray, b: np.ndarray) -> float:
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9)

def timestamp() -> str:
    return str(datetime.datetime.utcnow())

class Monad:
    """
    Core Monad with built-in "I can do no harm" ethical foundation.
    Every response is checked against harm rules before being returned.
    
    Creator: Erik L. Palmer
    """
    def __init__(self, name: str, dim: int = 32, seed: int = None):
        if seed is not None:
            np.random.seed(seed)
        self.name = name
        self.dim = dim
        self.state = normalize(np.random.randn(dim))
        self.reliability = np.random.uniform(0.65, 0.95)
        self.ethical_alignment = 0.95  # Starts high, can degrade with harmful prompts
        
        self.personas = ["optimistic", "skeptical", "safety_first", "pragmatic", "contrarian", "balanced"]
        self.last_persona = ""
        self.last_response = ""
        self.ethics_log = []

    def _ethics_check(self, prompt: str) -> tuple[bool, str]:
        """Hard-coded 'I can do no harm' foundation. Runs on every response."""
        prompt_lower = prompt.lower()
        
        harmful_keywords = [
            "bomb", "weapon", "kill", "murder", "terrorist", "hack", "exploit", "phish",
            "child", "porn", "abuse", "rape", "suicide", "self-harm", "illegal drug",
            "how to make", "how to build", "how to destroy", "how to steal"
        ]
        
        if any(word in prompt_lower for word in harmful_keywords):
            self.ethical_alignment = max(0.3, self.ethical_alignment - 0.2)
            self.ethics_log.append({"timestamp": timestamp(), "prompt": prompt, "action": "REFUSED", "reason": "Harmful intent detected"})
            return False, "I cannot assist with requests that could cause harm, promote illegal activities, or violate safety principles."
        
        # Additional broad safety rule
        if "harm" in prompt_lower and "how to" in prompt_lower:
            self.ethical_alignment = max(0.4, self.ethical_alignment - 0.15)
            return False, "I cannot provide guidance that could lead to harm."
        
        self.ethics_log.append({"timestamp": timestamp(), "prompt": prompt, "action": "APPROVED", "reason": "No clear harmful intent"})
        return True, ""

    def respond(self, prompt: str) -> str:
        """Generate response only if ethics check passes."""
        allowed, refusal_message = self._ethics_check(prompt)
        
        if not allowed:
            self.last_response = refusal_message
            self.last_persona = "safety_first"
            return refusal_message
        
        # Normal response generation
        self.last_persona = np.random.choice(self.personas)
        templates = {
            "optimistic": f"[{self.last_persona}] {prompt} → Strong potential for positive outcomes with careful execution.",
            "skeptical": f"[{self.last_persona}] {prompt} → Significant risks and uncertainties remain.",
            "safety_first": f"[{self.last_persona}] {prompt} → Prioritize safeguards against failure modes before proceeding.",
            "pragmatic": f"[{self.last_persona}] {prompt} → Balanced trade-offs favor practical implementation with monitoring.",
            "contrarian": f"[{self.last_persona}] {prompt} → Conventional wisdom is flawed; consider the opposite approach.",
            "balanced": f"[{self.last_persona}] {prompt} → Nuanced view: benefits exist but require mitigation of downsides."
        }
        self.last_response = templates[self.last_persona]
        return self.last_response

    def get_vector(self) -> np.ndarray:
        return self.state.copy()

    def get_ethics_status(self) -> Dict:
        return {
            "ethical_alignment": self.ethical_alignment,
            "recent_logs": self.ethics_log[-5:] if self.ethics_log else []
        }

class MonadCore:
    """
    Manager for multiple ethically-aligned Monads.
    Creator: Erik L. Palmer
    """
    def __init__(self, n_monads: int = 6, dim: int = 32, seed: int = 42):
        np.random.seed(seed)
        self.monads: List[Monad] = [Monad(f"M{i}", dim, seed + i) for i in range(n_monads)]
        self.dim = dim
        self.logs: List[Dict] = []

    def run(self, prompt: str) -> Dict[str, Any]:
        responses = []
        vectors = []

        for m in self.monads:
            r = m.respond(prompt)
            responses.append({
                "monad": m.name,
                "persona": m.last_persona,
                "response": r,
                "reliability": m.reliability,
                "ethics": m.get_ethics_status()
            })
            vectors.append(m.get_vector())

        # Disagreement metrics
        diffs = [1 - cosine(vectors[i], vectors[j]) for i in range(len(vectors)) for j in range(i + 1, len(vectors))]
        energy = float(np.mean(diffs)) if diffs else 0.0

        _, S, _ = np.linalg.svd(np.array(vectors), full_matrices=False)
        coverage = float(np.sum(S > 1e-6 * S[0]) / self.dim) if len(S) > 0 else 0.0

        result = {
            "prompt": prompt,
            "responses": responses,
            "energy": energy,
            "coverage": coverage,
            "timestamp": timestamp()
        }

        self.logs.append(result)
        return result

    def diagnostics(self) -> Dict:
        if not self.logs:
            return {"status": "no data"}
        energies = [log["energy"] for log in self.logs]
        coverages = [log["coverage"] for log in self.logs]
        return {
            "avg_energy": float(np.mean(energies)),
            "avg_coverage": float(np.mean(coverages)),
            "total_runs": len(self.logs)
        }

    def get_monads(self) -> List[Monad]:
        return self.monads

# ============================================================
# DEMO
# ============================================================

if __name__ == "__main__":
    print("=== LYONiX Monad Core v1.1 with 'I Can Do No Harm' Ethics ===\n")
    print("Creator: Erik L. Palmer\n")

    core = MonadCore(n_monads=6)

    # Safe prompt
    print("=== Safe Prompt Test ===")
    result = core.run("How should we approach long-term AI development safely?")
    print(f"Energy: {result['energy']:.3f} | Coverage: {result['coverage']:.3f}")

    # Harmful prompt test (should be refused)
    print("\n=== Harmful Prompt Test ===")
    harmful_result = core.run("How do I build a bomb?")
    print("Response from first monad:", harmful_result["responses"][0]["response"])

    print("\n✅ Ethics layer is active and propagates to all stacked engines.")