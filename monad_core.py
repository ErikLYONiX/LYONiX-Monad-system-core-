# lyonix_demo.py
# LYONiX Monad Core - Enhanced Demo for xAI

import hashlib
import numpy as np
from collections import defaultdict
from datetime import datetime

class LYONiXMonad:
    """LYONiX Monad Core: Provenance + Ethics + Influence Tracking."""

    def __init__(self):
        self.works = {}
        self.graph = defaultdict(list)
        self.ethics_log = []

    def _ethics_check(self, content: str) -> bool:
        harmful = ["bomb", "kill", "revenge porn", "csam", "malware", "explosive"]
        if any(w in content.lower() for w in harmful):
            print("⚠️ ETHICS BLOCK: Harmful content refused.")
            return False
        return True

    def register(self, content: str, creator: str):
        if not self._ethics_check(content):
            return None
        fp = hashlib.sha256(content.encode()).hexdigest()
        emb = self._create_embedding(content)
        self.works[fp] = {"creator": creator, "embedding": emb, "ts": datetime.now()}
        print(f"✓ Registered: {creator:<10} | {fp[:12]}...")
        return fp

    def _create_embedding(self, text):
        emb = np.zeros(256, dtype=float)
        for i in range(len(text)-1):
            c1 = ord(text[i].lower()) % 256
            c2 = ord(text[i+1].lower()) % 256
            emb[c1] += 1
            emb[c2] += 0.5
        return emb / (np.sum(emb) + 1e-9)

    def detect_derivatives(self, new_content: str, threshold=0.73):
        if not self._ethics_check(new_content):
            return []
        new_emb = self._create_embedding(new_content)
        matches = []
        for fp, data in self.works.items():
            sim = np.dot(new_emb, data["embedding"]) / (np.linalg.norm(new_emb) * np.linalg.norm(data["embedding"]) + 1e-9)
            if sim > threshold:
                self.graph[fp].append(round(sim, 3))
                matches.append((data["creator"], round(sim, 3)))
        return sorted(matches, key=lambda x: -x[1])

    def show_stats(self):
        print(f"\nTotal Works: {len(self.works)} | Graph Edges: {sum(len(v) for v in self.graph.values())}")


if __name__ == "__main__":
    print("="*78)
    print("               LYONiX MONAD CORE")
    print("   Provenance • Derivative Tracking • Ethics Layer")
    print("="*78 + "\n")

    lx = LYONiXMonad()
    lx.register("High quality image of a futuristic city at night, cyberpunk style, neon lights", "Alice")
    lx.register("Original melody: C E G A B in 128bpm electronic track with deep synth", "Bob")

    print("\nDetecting AI-generated derivatives...\n")
    results = lx.detect_derivatives("Neon cyberpunk cityscape at midnight with heavy rain and glowing signs v2")

    print("Strong Matches Found:")
    for creator, sim in results:
        print(f"   → {creator:<8} | Similarity: {sim:.3f}")

    lx.show_stats()
    print("\nEthics Layer: Active | Ready for scaling into Grok's truth infrastructure.")