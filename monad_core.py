"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  LYONiX — PRODUCT 1: CORE ENGINE                                            ║
║  The foundation everything else runs on                                      ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import hashlib, math, time, json, uuid
from dataclasses import dataclass, field
from typing import Optional
from collections import defaultdict


def cosine_similarity(a, b):
    if not a or not b or len(a) != len(b): return 0.0
    dot = sum(x*y for x,y in zip(a,b))
    na = math.sqrt(sum(x*x for x in a))
    nb = math.sqrt(sum(y*y for y in b))
    return dot/(na*nb) if na*nb > 0 else 0.0

def l2_normalize(vec):
    norm = math.sqrt(sum(v*v for v in vec)) or 1.0
    return [v/norm for v in vec]

def temporal_decay(value, age_seconds, rate=0.001):
    return value * math.exp(-rate * age_seconds)

def derivation_probability(sim, temporal_prior, creator_overlap=0.0):
    if not temporal_prior: return sim * 0.1
    return min(1.0, max(0.0, (sim-0.5)*2.0) * (1.0 - creator_overlap*0.8))

def information_entropy(dist):
    total = sum(dist.values())
    if not total: return 0.0
    return -sum((v/total)*math.log2(v/total) for v in dist.values() if v > 0)

def sha256(text):
    return hashlib.sha256(text.encode()).hexdigest()


def extract_text_features(text, dim=256):
    vec = [0.0] * dim
    t = ' '.join(text.lower().split())
    for i in range(len(t) - 2):
        h = 2166136261
        for c in t[i:i+3]:
            h ^= ord(c); h = (h * 16777619) & 0xFFFFFFFF
        vec[h % dim] += 1.0
    return l2_normalize(vec)

def extract_code_features(code, dim=256):
    import re
    tokens = re.findall(r'\w+|[^\w\s]', code.lower())
    vec = [0.0] * dim
    for i, tok in enumerate(tokens):
        h = hash(tok) & 0xFFFFFFFF; vec[h % dim] += 1.0
        if i < len(tokens)-1:
            h2 = hash(tok+'_'+tokens[i+1]) & 0xFFFFFFFF
            vec[h2 % dim] += 0.5
    return l2_normalize(vec)


@dataclass
class WorkRecord:
    fingerprint: str
    creator_id: str
    domain: str
    sequence_id: int
    registered_at: float
    content_preview: str
    features: list
    trust_score: float = 1.0
    metadata: dict = field(default_factory=dict)
    prev_hash: str = "GENESIS"
    record_hash: str = ""

    def compute_record_hash(self):
        raw = self.fingerprint + self.creator_id + \
              str(self.sequence_id) + str(self.registered_at) + self.prev_hash
        return sha256(raw)

class ImmutableRegistry:
    def __init__(self):
        self._log = []
        self._index = {}
        self._creator_index = defaultdict(list)

    def register(self, content, creator_id, domain="text", metadata=None):
        features = extract_code_features(content) \
                   if domain == "code" else extract_text_features(content)
        fp = sha256(f"{content}::{creator_id}::{domain}::{len(self._log)}")
        prev = self._log[-1].record_hash if self._log else "GENESIS"
        r = WorkRecord(
            fingerprint=fp, creator_id=creator_id, domain=domain,
            sequence_id=len(self._log), registered_at=time.time(),
            content_preview=content[:100], features=features,
            metadata=metadata or {}, prev_hash=prev)
        r.record_hash = r.compute_record_hash()
        self._log.append(r)
        self._index[fp] = r
        self._creator_index[creator_id].append(fp)
        return r

    def verify_chain(self):
        violations = []
        for i, r in enumerate(self._log):
            if r.compute_record_hash() != r.record_hash:
                violations.append(f"Record {i} hash mismatch")
            if i > 0 and r.prev_hash != self._log[i-1].record_hash:
                violations.append(f"Record {i} chain break")
        return len(violations) == 0, violations

    def proves_priority(self, fp_a, fp_b):
        a, b = self._index.get(fp_a), self._index.get(fp_b)
        if not a or not b: return None
        return {
            "a_before_b": a.sequence_id < b.sequence_id,
            "sequence_delta": b.sequence_id - a.sequence_id,
            "time_delta_ms": int((b.registered_at - a.registered_at) * 1000),
            "a_creator": a.creator_id,
            "b_creator": b.creator_id,
        }

    def get_all(self): return list(self._log)
    def get(self, fp): return self._index.get(fp)
    def size(self): return len(self._log)


DOMAIN_THRESHOLDS = {
    "text": 0.65, "audio": 0.75, "image": 0.80,
    "code": 0.70, "video": 0.72, "default": 0.70,
}

@dataclass
class DerivativeEdge:
    source_fp: str
    target_fp: str
    similarity_score: float
    derivation_score: float
    evidence: dict = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)

def detect_derivatives(registry):
    works = registry.get_all()
    edges = []
    for i, wa in enumerate(works):
        for j, wb in enumerate(works):
            if i >= j: continue
            sim = cosine_similarity(wa.features, wb.features)
            thresh = DOMAIN_THRESHOLDS.get(wa.domain, DOMAIN_THRESHOLDS["default"])
            if sim < thresh: continue
            p = registry.proves_priority(wa.fingerprint, wb.fingerprint)
            if not p: continue
            src, tgt = (wa, wb) if p["a_before_b"] else (wb, wa)
            overlap = 1.0 if src.creator_id == tgt.creator_id else 0.0
            ds = derivation_probability(sim, True, overlap)
            if ds < 0.15: continue
            edges.append(DerivativeEdge(
                source_fp=src.fingerprint, target_fp=tgt.fingerprint,
                similarity_score=sim, derivation_score=ds,
                evidence={"sim": sim, "domain": wa.domain, "threshold": thresh}))
    return edges


class ProvenanceGraph:
    def __init__(self, registry):
        self.registry = registry
        self._edges = []
        self._adj = defaultdict(list)
        self._radj = defaultdict(list)

    def rebuild(self, edges):
        self._edges = []
        self._adj = defaultdict(list)
        self._radj = defaultdict(list)
        for e in edges:
            self._edges.append(e)
            self._adj[e.source_fp].append(e)
            self._radj[e.target_fp].append(e)

    def ancestors(self, fp, max_depth=10):
        visited, result, queue = set(), [], [(fp, 0)]
        while queue:
            cur, d = queue.pop(0)
            if d >= max_depth or cur in visited: continue
            visited.add(cur)
            for e in self._radj.get(cur, []):
                result.append((e.source_fp, d+1))
                queue.append((e.source_fp, d+1))
        return result

    def descendants(self, fp, max_depth=10):
        visited, result, queue = set(), [], [(fp, 0)]
        while queue:
            cur, d = queue.pop(0)
            if d >= max_depth or cur in visited: continue
            visited.add(cur)
            for e in self._adj.get(cur, []):
                result.append((e.target_fp, d+1))
                queue.append((e.target_fp, d+1))
        return result

    def influence_score(self, fp):
        direct = sum(e.derivation_score for e in self._adj.get(fp, []))
        cascade = sum(0.5**d for _, d in self.descendants(fp)) * 0.3
        return direct + cascade

    def topology(self):
        all_fps = set(r.fingerprint for r in self.registry.get_all())
        hubs = sinks = bridges = orphans = 0
        for fp in all_fps:
            out = len(self._adj.get(fp, []))
            inn = len(self._radj.get(fp, []))
            if out > 2: hubs += 1
            if inn > 2: sinks += 1
            if out > 0 and inn > 0: bridges += 1
            if out == 0 and inn == 0: orphans += 1
        n = len(all_fps)
        return {
            "total_works": n, "total_edges": len(self._edges),
            "hubs": hubs, "sinks": sinks,
            "bridges": bridges, "orphans": orphans,
            "graph_density": len(self._edges) / max(1, n*(n-1)/2),
        }


class LYOEngine:
    USAGE_LYO  = 1.0
    AI_LYO     = 100.0
    DERIV_RATE = 0.10
    CASCADE    = 0.5
    MIN_DS     = 0.30

    def __init__(self, registry, graph):
        self.registry = registry
        self.graph = graph
        self._balances = defaultdict(float)
        self._tx_log = []

    def trigger_usage(self, fp, multiplier=1.0):
        direct = self.USAGE_LYO * multiplier
        self._balances[fp] += direct
        self._tx_log.append({"type":"usage","fp":fp,"amount":direct,"ts":time.time()})
        for ancestor_fp, depth in self.graph.ancestors(fp):
            for e in self.graph._radj.get(fp, []):
                if e.source_fp == ancestor_fp and e.derivation_score >= self.MIN_DS:
                    upstream = direct * self.DERIV_RATE * (self.CASCADE ** depth)
                    self._balances[ancestor_fp] += upstream

    def trigger_ai_training(self, fps, model_name):
        for fp in fps:
            self._balances[fp] += self.AI_LYO
            self._tx_log.append({
                "type":"ai_training","fp":fp,"model":model_name,
                "amount":self.AI_LYO,"ts":time.time()})
            for afp, d in self.graph.ancestors(fp):
                self._balances[afp] += self.AI_LYO * (self.CASCADE**d) * 0.2

    def get_balance(self, fp):
        w = self.registry.get(fp)
        if not w: return 0.0
        return temporal_decay(self._balances.get(fp, 0.0),
                              time.time() - w.registered_at, 0.0001)

    def fairness_report(self):
        bals = {fp: self.get_balance(fp) for fp in self._balances}
        total = sum(bals.values())
        ct = defaultdict(float)
        for fp, b in bals.items():
            w = self.registry.get(fp)
            if w: ct[w.creator_id] += b
        return {
            "total_lyo": round(total, 2),
            "entropy_bits": round(information_entropy(bals), 3),
            "creator_balances": {k: round(v, 2) for k, v in ct.items()},
        }


class CoreEngine:
    def __init__(self):
        self.registry = ImmutableRegistry()
        self.graph = ProvenanceGraph(self.registry)
        self.economics = LYOEngine(self.registry, self.graph)

    def register_work(self, content, creator_id, domain="text", metadata=None):
        record = self.registry.register(content, creator_id, domain, metadata)
        if self.registry.size() >= 2:
            self.graph.rebuild(detect_derivatives(self.registry))
        return record

    def query_work(self, fingerprint):
        w = self.registry.get(fingerprint)
        if not w: return {"error": "not found"}
        return {
            "fingerprint": fingerprint,
            "creator": w.creator_id,
            "domain": w.domain,
            "sequence_id": w.sequence_id,
            "ancestors": len(self.graph.ancestors(fingerprint)),
            "descendants": len(self.graph.descendants(fingerprint)),
            "influence_score": round(self.graph.influence_score(fingerprint), 4),
            "lyo_balance": round(self.economics.get_balance(fingerprint), 4),
            "is_original": len(self.graph.ancestors(fingerprint)) == 0,
        }

    def system_report(self):
        valid, violations = self.registry.verify_chain()
        return {
            "works_registered": self.registry.size(),
            "chain_valid": valid,
            "chain_violations": violations,
            "graph": self.graph.topology(),
            "economics": self.economics.fairness_report(),
        }


if __name__ == "__main__":
    print("=" * 60)
    print("  LYONiX — PRODUCT 1: CORE ENGINE")
    print("=" * 60)

    engine = CoreEngine()

    works = [
        ("The melody rises at dawn with arpeggiated C major chords breathing with the morning light", "Alice_Music", "text"),
        ("The melody rises at morning with arpeggiated C major progressions breathing with dawn", "Bob_Remix", "text"),
        ("Morning light arpeggio in C major, a melody rising with the dawn breeze", "Carol_Cover", "text"),
        ("Quantum entanglement describes non-local correlations between particle states across space", "Dave_Science", "text"),
        ("Non-local quantum correlations between entangled particle states violate classical locality", "Eve_Research", "text"),
        ("The rain falls softly on cobblestones, percussion of water and ancient stone", "Frank_Poet", "text"),
        ("def fibonacci(n): return n if n<=1 else fibonacci(n-1)+fibonacci(n-2)", "Grace_Code", "code"),
        ("def fib(n): return n if n<=1 else fib(n-1)+fib(n-2)", "Henry_Code", "code"),
    ]

    print("\n[1] REGISTERING WORKS")
    fps = []
    for content, creator, domain in works:
        r = engine.register_work(content, creator, domain)
        fps.append(r.fingerprint)
        print(f"  SEQ#{r.sequence_id:02d} | {creator:<20} | {r.fingerprint[:20]}...")

    print("\n[2] CHAIN INTEGRITY")
    valid, violations = engine.registry.verify_chain()
    print(f"  Valid: {valid} | Violations: {len(violations)}")

    print("\n[3] GRAPH TOPOLOGY")
    topo = engine.graph.topology()
    for k, v in topo.items():
        print(f"  {k:<20}: {v}")

    print("\n[4] DERIVATIVE EDGES DETECTED")
    for src_fp, edges in engine.graph._adj.items():
        src = engine.registry.get(src_fp)
        for e in edges:
            tgt = engine.registry.get(e.target_fp)
            print(f"  {src.creator_id:<20} → {tgt.creator_id:<20} | sim:{e.similarity_score:.3f} deriv:{e.derivation_score:.3f}")

    print("\n[5] LYO SIMULATION — AI TRAINING EVENT")
    engine.economics.trigger_ai_training(fps[:3], "AudioLM-v2")
    for fp in fps[:4]:
        w = engine.registry.get(fp)
        bal = engine.economics.get_balance(fp)
        print(f"  {w.creator_id:<20}: {bal:.2f} LYO")

    print("\n[6] SYSTEM REPORT")
    report = engine.system_report()
    print(f"  Works     : {report['works_registered']}")
    print(f"  Chain OK  : {report['chain_valid']}")
    print(f"  Edges     : {report['graph']['total_edges']}")
    print(f"  Total LYO : {report['economics']['total_lyo']}")
    print(f"  Entropy   : {report['economics']['entropy_bits']} bits")
    print("=" * 60)