# LYONiX-Monad-system-core-
LYONiX System Core Foundation - MONAD


# LYONiX — MONAD: Core Engine

> **The foundational attribution and provenance layer of the LYONiX System.**

---

## Overview

The **MONAD** is Product 1 of the LYONiX System — a cryptographically secured, economically aware engine for registering creative works, detecting derivative relationships, and flowing attribution value back to original creators.

It solves a problem that no production system has fully addressed: **AI and digital platforms consume creative works at scale with no traceable attribution or compensation mechanism.** The MONAD provides the technical foundation to change that.

---

## What It Does

| Capability | Description |
|---|---|
| **Fingerprinting** | SHA-256 content fingerprints — unique, deterministic, tamper-evident |
| **Feature Extraction** | 256-dim L2-normalized trigram vectors for text; token bigram vectors for code |
| **Similarity Detection** | Cosine similarity with domain-specific thresholds |
| **Derivative Detection** | Separates similarity from derivation using temporal ordering + probability scoring |
| **Provenance Graph** | Directed acyclic graph of creative influence with ancestor/descendant traversal |
| **Immutable Registry** | Append-only, chain-hashed log — tamper with any record and all subsequent hashes break |
| **LYO Economic Engine** | Attribution accounting unit that flows value upstream through derivative chains |

---

## Architecture

```
CoreEngine
├── ImmutableRegistry       # Append-only, chain-hashed work log
├── ProvenanceGraph         # DAG of creative relationships
│   └── detect_derivatives  # Pairwise similarity + derivation scoring
└── LYOEngine               # Attribution accounting and value flow
    ├── trigger_usage()     # 1 LYO per consumption event
    └── trigger_ai_training() # 100 LYO per AI training inclusion
```

---

## Key Design Decisions

### Similarity ≠ Derivation
Most plagiarism systems conflate these. The MONAD explicitly separates them. High cosine similarity alone does not trigger a derivative relationship — temporal ordering and a `derivation_probability()` score must also meet domain-specific thresholds.

### Chain-Hashed Registry
Each registered work hashes the previous record. This creates a tamper-evident chain where:
- Sequence IDs are monotonic — retroactive insertion is impossible
- Priority proof is cryptographic — A registered before B iff `seq(A) < seq(B)`
- Any tampering propagates as detectable hash mismatches

### LYO Is Not Cryptocurrency
LYO is an **accounting unit for creative attribution** — modeled after ASCAP royalty points, not blockchain tokens. It is automated, multi-domain, and cryptographically tracked without the overhead of a distributed ledger.

### Anti-Exploit Logic
- Same-creator self-derivatives: `creator_overlap` penalty zeroes out LYO flow
- Spam derivatives: minimum derivation score gate (`MIN_DS = 0.30`)
- Cascade decay: upstream value diminishes by `0.5^depth` per hop

---

## Installation

```bash
# No external dependencies required for core engine
python lyonix_p1_core_engine.py
```

**Python 3.8+** required. Standard library only.

---

## Quick Start

```python
from lyonix_p1_core_engine import CoreEngine

engine = CoreEngine()

# Register original works
r1 = engine.register_work(
    content="The melody rises at dawn with arpeggiated C major chords",
    creator_id="Alice_Music",
    domain="text"
)

# Register a derivative
r2 = engine.register_work(
    content="The melody rises at morning with arpeggiated C major progressions",
    creator_id="Bob_Remix",
    domain="text"
)

# Query provenance
print(engine.query_work(r1.fingerprint))
# → {is_original: True, influence_score: ..., lyo_balance: ...}

# Trigger an AI training event
engine.economics.trigger_ai_training([r1.fingerprint, r2.fingerprint], "ModelName-v1")

# System report
print(engine.system_report())
```

---

## Supported Domains

| Domain | Feature Method | Similarity Threshold |
|---|---|---|
| `text` | Character trigram frequency | 0.65 |
| `code` | Token bigram frequency | 0.70 |
| `audio` | *(extensible)* | 0.75 |
| `image` | *(extensible)* | 0.80 |
| `video` | *(extensible)* | 0.72 |

---

## LYO Economic Model

```
Usage Event         →  1.0 LYO  → registered work
AI Training Event   → 100.0 LYO → registered work
                           ↓
              10% flows upstream to ancestor works
              Cascade decay: 50% per hop depth
```

**Fairness reporting** includes information entropy across all balances — a single metric indicating whether attribution is concentrating or distributing fairly across creators.

---

## Provenance Graph Topology

The graph classifies every registered work by its structural role:

- **Hub nodes** — many outgoing edges; highly influential originals
- **Sink nodes** — many incoming edges; heavily derived works  
- **Bridge nodes** — connect otherwise separate clusters; undervalued pioneers
- **Orphan nodes** — no connections; fully independent originals

---

## Verifying Chain Integrity

```python
valid, violations = engine.registry.verify_chain()
print(f"Chain valid: {valid}")
# Any violations indicate tampering or corruption
```

---

## Current Limitations

- **O(n²) derivative scan** — suitable for thousands of works; will require approximate nearest-neighbor (FAISS/annoy) for production scale
- **Trigram vectors** — fast and interpretable but do not capture semantic similarity; paraphrase-style derivation may be missed
- **Single-process** — no persistence layer; state lives in memory for this version

---

## Roadmap

- [ ] Semantic embedding layer (sentence-transformers) alongside trigram vectors
- [ ] Persistent storage backend (SQLite → PostgreSQL)
- [ ] ANN index (FAISS) for large-scale similarity search
- [ ] REST API surface for external integration
- [ ] Real-time usage signal ingestion (streaming plays, page views, API calls)
- [ ] Multi-modal feature extractors (audio, image, video)
- [ ] LYONiX Product 2 integration

---

## Part of the LYONiX System

The MONAD is the core foundation layer. All higher LYONiX products run on top of this engine. It provides the shared registry, graph, and economic primitives that every subsequent module depends on.

---

## License
Copyright (c) 2024 Erik L. Palmer. All rights reserved.

This source code is provided for viewing and evaluation 
purposes only. No permission is granted to use, copy, 
modify, merge, publish, distribute, sublicense, or sell 
this software or any derivative works, in whole or in 
part, without explicit written permission from the author.

Proprietary — All Rights Reserved. See LICENSE file.

For licensing inquiries: eriklyonpalmer@gmail.com
---


## Author
Erik L. Palmer 

---

*LYONiX — Attribution infrastructure for the age of AI.*
