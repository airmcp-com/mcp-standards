# Package Manager Intelligence System
**Comprehensive Design Specification**
**Date**: 2025-10-20
**Version**: 2.0

---

## Executive Summary

This document specifies a comprehensive package manager detection and preference learning system that reduces user corrections from 3-5 repetitions to 1-2 through intelligent detection, semantic clustering, and Bayesian confidence scoring.

**Key Innovations**:
- **Intelligent Detection**: Automatic project file analysis (uv.lock, poetry.lock, package.json)
- **Semantic Clustering**: AgentDB embeddings cluster similar corrections ("use uv" + "prefer uv" = same pattern)
- **Bayesian Confidence**: Success/failure tracking with probabilistic updates
- **Cross-Project Learning**: Share preferences across similar project types
- **Proactive Application**: Predict and apply before corrections needed

**Expected Impact**:
- Corrections reduced: 3-5 → 1-2 (60-70% reduction)
- Learning speed: 2-3 days → same session
- Confidence accuracy: 75% → 90%+
- Context pollution: -2,000 tokens (fewer repeated instructions)

---

## 1. Problem Analysis

### 1.1 Current Pain Point

**Real-world scenario** (documented in v2-system-analysis.md):

```
Conversation 1:
User: "install pytest"
Claude: "I'll use pip install pytest"
User: "Actually, use uv not pip"  ← Correction #1

Conversation 2 (same session):
User: "install requests"
Claude: "I'll use pip install requests"
User: "Use uv not pip!"  ← Correction #2

Conversation 3:
User: "install pandas"
Claude: "I'll use pip install pandas"
User: "USE UV NOT PIP!!!"  ← Correction #3

[Pattern detected at 3 occurrences, promoted to preference]

Conversation 4:
User: "install numpy"
Claude: "I'll use uv pip install numpy"  ← Finally learned!
```

**Root Causes**:
1. **Keyword-only matching**: "use uv" ≠ "prefer uv" ≠ "always use uv" (treated as different patterns)
2. **No context detection**: Project has `uv.lock` but system ignores it
3. **Fixed threshold**: Requires exactly 3 corrections, no semantic understanding
4. **No cross-project learning**: Learned preference in Project A doesn't apply to Project B
5. **Reactive only**: Never predicts, always waits for user correction

### 1.2 Desired Outcome

```
v2 Workflow with Package Manager Intelligence:

Conversation 1 (new project):
User: "install pytest"
[System detects uv.lock in project root]
[System searches AgentDB: "python package installation" → finds 0 patterns]
Claude: "I'll use pip install pytest"
User: "Actually, use uv not pip"  ← Correction #1
[System stores embedding: "prefer uv over pip for python packages"]
[System updates confidence: 0.0 → 0.4 (Bayesian prior)]

Conversation 2 (same project, 5 min later):
User: "install requests"
[System detects uv.lock → confidence boost +0.3]
[System searches AgentDB: "python package" → finds "prefer uv" (0.7 confidence)]
Claude: "I'll use uv pip install requests"  ← Learned after 1 correction!
[No user correction → success signal → confidence 0.7 → 0.85]

Conversation 3 (different project, same machine):
[System detects poetry.lock → different manager]
User: "install fastapi"
[System searches: "python package" → finds "prefer uv" (0.85), "prefer poetry" (0.2)]
[System cross-references: poetry.lock detected → suggests poetry]
Claude: "I'll use poetry add fastapi"  ← Zero corrections, inferred from project context!
```

**Reduction Achieved**:
- Corrections: 3 → 1 (67% reduction)
- Learning time: Multiple conversations → Same conversation
- Cross-project: Manual repetition → Automatic inference

---

## 2. System Architecture

### 2.1 Component Overview

```
┌─────────────────────────────────────────────────────────────────┐
│         Package Manager Intelligence System (PMIS)              │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              1. Project File Detector                     │ │
│  │  • Scans for uv.lock, poetry.lock, Pipfile, package.json │ │
│  │  • Reads pyproject.toml [tool.*] sections                │ │
│  │  • Caches results for 5min (avoid repeated scans)        │ │
│  │  • Confidence boost: +0.3 if lock file found             │ │
│  └─────────────────┬─────────────────────────────────────────┘ │
│                    │                                           │
│                    ▼                                           │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │       2. Semantic Preference Clustering (AgentDB)         │ │
│  │  • Embeds corrections: "use uv" → 384-dim vector         │ │
│  │  • Clusters similar: "prefer uv" + "always uv" → same    │ │
│  │  • HNSW search: <1ms for "package management" query      │ │
│  │  • Threshold: 0.7 cosine similarity = same pattern       │ │
│  └─────────────────┬─────────────────────────────────────────┘ │
│                    │                                           │
│                    ▼                                           │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │          3. Bayesian Confidence Scoring                   │ │
│  │  • Prior: 0.4 (first correction)                         │ │
│  │  • Success: confidence × 1.2 (capped at 0.95)            │ │
│  │  • Failure: confidence × 0.7 (min 0.1)                   │ │
│  │  • Decay: -0.05/week if unused                           │ │
│  └─────────────────┬─────────────────────────────────────────┘ │
│                    │                                           │
│                    ▼                                           │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │       4. Cross-Project Learning Engine                    │ │
│  │  • Detects similar projects via embeddings               │ │
│  │  • Shares patterns: 3+ projects → global preference      │ │
│  │  • Project-type specific: Django → pytest not unittest   │ │
│  └─────────────────┬─────────────────────────────────────────┘ │
│                    │                                           │
│                    ▼                                           │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │          5. Proactive Application Layer                   │ │
│  │  • Pre-command prediction: "install X" → check patterns  │ │
│  │  • Context injection: Add to Claude prompt if >0.7 conf  │ │
│  │  • Suggestion mode: "Did you mean 'uv pip install'?"     │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘

         ▼                              ▼
┌─────────────────┐          ┌──────────────────────┐
│  AgentDB        │          │  SQLite              │
│  (Vector Store) │          │  (Audit Trail)       │
│                 │          │                      │
│ • Embeddings    │          │ • Full corrections   │
│ • HNSW graph    │          │ • Timestamps         │
│ • <1ms search   │          │ • Success/fail log   │
│ • Semantic      │          │ • Compliance         │
└─────────────────┘          └──────────────────────┘
```

### 2.2 Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    User Command Flow                            │
└─────────────────────────────────────────────────────────────────┘

1. User Input: "install pytest"
   │
   ▼
2. PMIS Pre-Processing
   ├─► Project File Detector
   │   ├─ Scan: uv.lock found ✓
   │   ├─ Read: pyproject.toml [tool.uv] ✓
   │   └─ Confidence Boost: +0.3
   │
   ├─► Semantic Search (AgentDB)
   │   ├─ Query: "python package installation pytest"
   │   ├─ Embedding: [0.234, -0.567, ...] (384-dim)
   │   ├─ HNSW Search: <1ms
   │   └─ Results: [
   │       {pattern: "prefer uv over pip", confidence: 0.85, similarity: 0.92},
   │       {pattern: "use poetry for deps", confidence: 0.45, similarity: 0.73}
   │     ]
   │
   ├─► Cross-Project Check
   │   ├─ Similar projects: 4 found (all use uv)
   │   ├─ Global preference: "uv for Python projects" (0.9 confidence)
   │   └─ Context boost: +0.1
   │
   └─► Final Decision
       ├─ Pattern: "prefer uv over pip"
       ├─ Confidence: 0.85 + 0.3 (file) + 0.1 (cross-project) = 1.0 → capped at 0.95
       ├─ Threshold: 0.7 → APPLY
       └─ Inject to prompt: "Use 'uv pip install' for Python packages"

3. Claude Execution
   ├─ Reads injected context
   └─ Executes: "uv pip install pytest"

4. Outcome Tracking
   ├─ Wait 30s for user correction
   ├─ No correction → SUCCESS
   ├─ Update confidence: 0.95 × 1.1 = 0.95 (capped)
   └─ Store in ReasoningBank:
       {
         pattern_id: "pkg_mgr_uv_python",
         outcome: "success",
         confidence_before: 0.85,
         confidence_after: 0.95,
         timestamp: "2025-10-20T22:43:00Z"
       }

5. Learning Update
   ├─ AgentDB: Update vector metadata (confidence: 0.95)
   ├─ SQLite: Append audit log
   └─ CLAUDE.md: Auto-update if confidence crossed 0.9 threshold
```

---

## 3. Algorithm Specifications

### 3.1 Project File Detection Algorithm

```python
"""
Project File Analysis for Package Manager Detection
"""

from pathlib import Path
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
import tomllib  # Python 3.11+
import json

@dataclass
class PackageManagerSignal:
    """Detected package manager with confidence score"""
    manager: str  # "uv", "pip", "poetry", "npm", "pnpm", "yarn"
    confidence: float  # 0.0-1.0
    evidence: list[str]  # Files that support this detection
    metadata: dict  # Additional context (version, config)


class ProjectFileDetector:
    """
    Detects preferred package manager from project files.

    Detection Strategy:
    1. Lock files (highest confidence)
    2. Config files (medium confidence)
    3. Executable scripts (low confidence)

    Confidence Scoring:
    - Lock file present: 0.9
    - Config section present: 0.7
    - Script reference: 0.5
    - Multiple signals: max(signals) + 0.1
    """

    # Detection patterns (priority order)
    DETECTION_PATTERNS = {
        # Python ecosystem
        "uv": {
            "lock_files": ["uv.lock"],
            "config_files": ["pyproject.toml"],
            "config_sections": ["tool.uv"],
            "confidence_boost": 0.9
        },
        "poetry": {
            "lock_files": ["poetry.lock"],
            "config_files": ["pyproject.toml"],
            "config_sections": ["tool.poetry"],
            "confidence_boost": 0.9
        },
        "pipenv": {
            "lock_files": ["Pipfile.lock"],
            "config_files": ["Pipfile"],
            "config_sections": [],
            "confidence_boost": 0.9
        },
        "pip": {
            "lock_files": ["requirements.txt.lock"],  # Rare but exists
            "config_files": ["requirements.txt", "requirements-dev.txt"],
            "config_sections": [],
            "confidence_boost": 0.5  # Lower, as it's the default
        },

        # JavaScript ecosystem
        "pnpm": {
            "lock_files": ["pnpm-lock.yaml"],
            "config_files": ["pnpm-workspace.yaml"],
            "config_sections": [],
            "confidence_boost": 0.9
        },
        "yarn": {
            "lock_files": ["yarn.lock"],
            "config_files": [".yarnrc.yml", ".yarnrc"],
            "config_sections": [],
            "confidence_boost": 0.9
        },
        "npm": {
            "lock_files": ["package-lock.json"],
            "config_files": ["package.json"],
            "config_sections": [],
            "confidence_boost": 0.7
        },
    }

    def __init__(self, cache_ttl_seconds: int = 300):
        """
        Initialize detector with caching.

        Args:
            cache_ttl_seconds: Cache detection results for this long
        """
        self._cache: Dict[str, Tuple[PackageManagerSignal, float]] = {}
        self._cache_ttl = cache_ttl_seconds

    async def detect(self, project_path: Path) -> Optional[PackageManagerSignal]:
        """
        Detect package manager for a project.

        Args:
            project_path: Root directory of the project

        Returns:
            PackageManagerSignal if detected, None otherwise
        """
        # Check cache
        cache_key = str(project_path.resolve())
        if cache_key in self._cache:
            signal, cached_at = self._cache[cache_key]
            if time.time() - cached_at < self._cache_ttl:
                return signal

        # Scan for signals
        detected_signals = []

        for manager, patterns in self.DETECTION_PATTERNS.items():
            evidence = []
            confidence = 0.0
            metadata = {}

            # Check lock files (highest confidence)
            for lock_file in patterns["lock_files"]:
                lock_path = project_path / lock_file
                if lock_path.exists():
                    evidence.append(f"lock:{lock_file}")
                    confidence = max(confidence, patterns["confidence_boost"])
                    metadata["lock_file"] = str(lock_path)

            # Check config files
            for config_file in patterns["config_files"]:
                config_path = project_path / config_file
                if config_path.exists():
                    evidence.append(f"config:{config_file}")
                    confidence = max(confidence, patterns["confidence_boost"] - 0.2)

                    # Parse config for additional metadata
                    if config_file.endswith(".toml"):
                        metadata.update(self._parse_toml_config(
                            config_path,
                            patterns["config_sections"]
                        ))
                    elif config_file == "package.json":
                        metadata.update(self._parse_package_json(config_path))

            # Check config sections (for tools in shared files)
            if patterns["config_sections"]:
                for section in patterns["config_sections"]:
                    if section in metadata:
                        confidence = max(confidence, patterns["confidence_boost"])
                        evidence.append(f"section:{section}")

            # Multiple signals boost confidence
            if len(evidence) > 1:
                confidence = min(1.0, confidence + 0.1)

            if evidence:
                detected_signals.append(PackageManagerSignal(
                    manager=manager,
                    confidence=confidence,
                    evidence=evidence,
                    metadata=metadata
                ))

        # Return highest confidence signal
        if detected_signals:
            best_signal = max(detected_signals, key=lambda s: s.confidence)
            self._cache[cache_key] = (best_signal, time.time())
            return best_signal

        return None

    def _parse_toml_config(self, path: Path, sections: list[str]) -> dict:
        """Parse pyproject.toml and extract relevant sections"""
        try:
            with path.open("rb") as f:
                data = tomllib.load(f)

            metadata = {}
            for section in sections:
                parts = section.split(".")
                current = data
                for part in parts:
                    if part in current:
                        current = current[part]
                        metadata[section] = current
                    else:
                        break

            return metadata
        except Exception:
            return {}

    def _parse_package_json(self, path: Path) -> dict:
        """Parse package.json for package manager hints"""
        try:
            with path.open("r") as f:
                data = json.load(f)

            return {
                "packageManager": data.get("packageManager"),
                "engines": data.get("engines", {}),
                "scripts": data.get("scripts", {})
            }
        except Exception:
            return {}


# Example usage:
detector = ProjectFileDetector()
signal = await detector.detect(Path("/path/to/project"))

if signal:
    print(f"Detected: {signal.manager}")
    print(f"Confidence: {signal.confidence:.2f}")
    print(f"Evidence: {signal.evidence}")
    # Output:
    # Detected: uv
    # Confidence: 1.00
    # Evidence: ['lock:uv.lock', 'config:pyproject.toml', 'section:tool.uv']
```

### 3.2 Semantic Clustering Algorithm

```python
"""
Semantic Preference Clustering using AgentDB embeddings
"""

from typing import List, Tuple
import numpy as np
from dataclasses import dataclass

@dataclass
class CorrectionPattern:
    """A user correction pattern with embedding"""
    id: str
    text: str  # "use uv not pip"
    embedding: np.ndarray  # 384-dim vector
    category: str  # "package-manager"
    confidence: float
    occurrence_count: int
    last_seen: float  # timestamp


class SemanticClusterer:
    """
    Clusters similar corrections using vector embeddings.

    Approach:
    1. Embed each correction: "use uv not pip" → [0.234, -0.567, ...]
    2. Compute pairwise similarities (cosine distance)
    3. Cluster if similarity > 0.7 (same pattern)
    4. Merge clusters: average embeddings, sum occurrences

    Benefits:
    - "use uv" + "prefer uv" + "always use uv" → 1 pattern
    - Reduces corrections needed: 3 → 1 (same semantic intent)
    - Cross-language support (if using multilingual embeddings)
    """

    SIMILARITY_THRESHOLD = 0.70  # Cosine similarity threshold
    CLUSTER_MERGE_THRESHOLD = 0.85  # Very similar → merge

    def __init__(self, embedding_manager, agentdb_store):
        """
        Initialize clusterer.

        Args:
            embedding_manager: EmbeddingManager instance (from embeddings.py)
            agentdb_store: AgentDB VectorStore instance
        """
        self.embedder = embedding_manager
        self.agentdb = agentdb_store

    async def add_correction(
        self,
        correction_text: str,
        category: str = "package-manager"
    ) -> Tuple[str, bool]:
        """
        Add a correction and cluster with similar patterns.

        Args:
            correction_text: The correction (e.g., "use uv not pip")
            category: Category for filtering

        Returns:
            (pattern_id, is_new) - ID of pattern, whether it's new or merged
        """
        # Generate embedding
        embedding = self.embedder.encode(correction_text, normalize=True)

        # Search for similar patterns in AgentDB
        similar_patterns = await self.agentdb.search(
            query_vector=embedding,
            k=5,
            filter={"category": category},
            threshold=self.SIMILARITY_THRESHOLD
        )

        if similar_patterns:
            # Found similar pattern(s)
            best_match = similar_patterns[0]

            if best_match["similarity"] >= self.CLUSTER_MERGE_THRESHOLD:
                # Very similar → merge into existing pattern
                pattern_id = best_match["id"]
                await self._merge_into_pattern(
                    pattern_id,
                    correction_text,
                    embedding
                )
                return (pattern_id, False)  # Merged into existing

            else:
                # Somewhat similar → increment occurrence of closest match
                pattern_id = best_match["id"]
                await self._increment_pattern_occurrence(pattern_id)
                return (pattern_id, False)

        # No similar patterns → create new
        pattern_id = await self._create_new_pattern(
            correction_text,
            embedding,
            category
        )
        return (pattern_id, True)

    async def find_similar(
        self,
        query_text: str,
        category: str = None,
        min_confidence: float = 0.0,
        top_k: int = 5
    ) -> List[CorrectionPattern]:
        """
        Find patterns similar to a query.

        Args:
            query_text: Query string (e.g., "python package installation")
            category: Optional category filter
            min_confidence: Minimum confidence threshold
            top_k: Maximum results

        Returns:
            List of similar patterns, sorted by similarity
        """
        # Generate query embedding
        query_embedding = self.embedder.encode(query_text, normalize=True)

        # Search AgentDB
        filters = {}
        if category:
            filters["category"] = category
        if min_confidence > 0:
            filters["confidence"] = {"$gte": min_confidence}

        results = await self.agentdb.search(
            query_vector=query_embedding,
            k=top_k,
            filter=filters if filters else None
        )

        # Convert to CorrectionPattern objects
        patterns = []
        for result in results:
            patterns.append(CorrectionPattern(
                id=result["id"],
                text=result["metadata"]["text"],
                embedding=np.array(result["vector"]),
                category=result["metadata"]["category"],
                confidence=result["metadata"]["confidence"],
                occurrence_count=result["metadata"]["occurrence_count"],
                last_seen=result["metadata"]["last_seen"]
            ))

        return patterns

    async def _merge_into_pattern(
        self,
        pattern_id: str,
        new_text: str,
        new_embedding: np.ndarray
    ):
        """Merge a new correction into an existing pattern"""
        # Retrieve existing pattern
        pattern = await self.agentdb.get(pattern_id)

        # Update metadata
        old_count = pattern["metadata"]["occurrence_count"]
        new_count = old_count + 1

        # Average embeddings (simple approach)
        # More sophisticated: weighted by confidence
        old_embedding = np.array(pattern["vector"])
        merged_embedding = (old_embedding * old_count + new_embedding) / new_count
        merged_embedding = merged_embedding / np.linalg.norm(merged_embedding)  # Normalize

        # Update in AgentDB
        await self.agentdb.update(
            id=pattern_id,
            vector=merged_embedding.tolist(),
            metadata={
                **pattern["metadata"],
                "occurrence_count": new_count,
                "last_seen": time.time(),
                "variations": pattern["metadata"].get("variations", []) + [new_text]
            }
        )

    async def _increment_pattern_occurrence(self, pattern_id: str):
        """Increment occurrence count for a pattern"""
        pattern = await self.agentdb.get(pattern_id)
        await self.agentdb.update(
            id=pattern_id,
            metadata={
                **pattern["metadata"],
                "occurrence_count": pattern["metadata"]["occurrence_count"] + 1,
                "last_seen": time.time()
            }
        )

    async def _create_new_pattern(
        self,
        text: str,
        embedding: np.ndarray,
        category: str
    ) -> str:
        """Create a new pattern"""
        import hashlib
        pattern_id = hashlib.sha256(text.encode()).hexdigest()[:16]

        await self.agentdb.add(
            id=pattern_id,
            vector=embedding.tolist(),
            metadata={
                "text": text,
                "category": category,
                "confidence": 0.4,  # Initial Bayesian prior
                "occurrence_count": 1,
                "created_at": time.time(),
                "last_seen": time.time(),
                "variations": [text]
            }
        )

        return pattern_id


# Example usage:
clusterer = SemanticClusterer(embedding_manager, agentdb_store)

# User correction 1
pattern_id_1, is_new = await clusterer.add_correction("use uv not pip")
# Output: ("a3f2e1b4", True) - New pattern created

# User correction 2 (semantically similar)
pattern_id_2, is_new = await clusterer.add_correction("prefer uv over pip")
# Output: ("a3f2e1b4", False) - Merged into existing pattern!

# User correction 3 (different phrasing)
pattern_id_3, is_new = await clusterer.add_correction("always use uv for packages")
# Output: ("a3f2e1b4", False) - Same pattern again!

# Search for similar patterns
patterns = await clusterer.find_similar("python package management")
# Output: [CorrectionPattern(text="use uv not pip", confidence=0.7, occurrence_count=3)]
```

### 3.3 Bayesian Confidence Scoring

```python
"""
Bayesian Confidence Scoring based on success/failure outcomes
"""

from typing import Optional
from dataclasses import dataclass
from enum import Enum

class Outcome(Enum):
    """Possible outcomes of applying a pattern"""
    SUCCESS = "success"  # Applied, no user correction
    FAILURE = "failure"  # Applied, user corrected again
    PARTIAL = "partial"  # Applied, user modified slightly
    IGNORED = "ignored"  # Not applied (low confidence)


@dataclass
class ConfidenceUpdate:
    """Result of a confidence update"""
    old_confidence: float
    new_confidence: float
    reason: str
    outcome: Outcome


class BayesianConfidenceScorer:
    """
    Updates pattern confidence based on Bayesian inference.

    Confidence Interpretation:
    - 0.0-0.3: Low (don't apply automatically)
    - 0.3-0.7: Medium (suggest to user)
    - 0.7-0.9: High (apply automatically)
    - 0.9-1.0: Very High (apply + promote to CLAUDE.md)

    Update Rules:
    - SUCCESS: confidence × 1.2 (capped at 0.95)
    - FAILURE: confidence × 0.6 (floor at 0.1)
    - PARTIAL: confidence × 0.95 (slight decrease)
    - UNUSED: -0.05 per week (decay)

    Bayesian Reasoning:
    P(pattern_correct | outcome) = P(outcome | pattern_correct) × P(pattern_correct) / P(outcome)

    Simplified:
    - Prior: 0.4 (first correction is informative but not definitive)
    - Likelihood: success = 0.9, failure = 0.1
    - Posterior: updated confidence
    """

    # Confidence thresholds
    APPLY_THRESHOLD = 0.7  # Auto-apply if confidence >= this
    SUGGEST_THRESHOLD = 0.5  # Suggest to user if >= this

    # Update multipliers
    SUCCESS_BOOST = 1.2
    FAILURE_PENALTY = 0.6
    PARTIAL_PENALTY = 0.95
    DECAY_PER_WEEK = 0.05

    # Bounds
    MIN_CONFIDENCE = 0.1
    MAX_CONFIDENCE = 0.95  # Never 1.0 (leave room for doubt)

    # Bayesian priors
    INITIAL_PRIOR = 0.4  # First correction
    LIKELIHOOD_SUCCESS = 0.9  # P(success | pattern_correct)
    LIKELIHOOD_FAILURE = 0.1  # P(failure | pattern_correct)

    def __init__(self):
        """Initialize scorer"""
        pass

    def update_confidence(
        self,
        current_confidence: float,
        outcome: Outcome,
        context: Optional[dict] = None
    ) -> ConfidenceUpdate:
        """
        Update confidence based on outcome.

        Args:
            current_confidence: Current confidence score
            outcome: Outcome of pattern application
            context: Additional context (e.g., project type, time since last use)

        Returns:
            ConfidenceUpdate with new confidence and reasoning
        """
        old_confidence = current_confidence
        new_confidence = current_confidence
        reason = ""

        if outcome == Outcome.SUCCESS:
            # Pattern applied successfully, no user correction
            # Bayesian update: posterior ∝ likelihood × prior
            new_confidence = current_confidence * self.SUCCESS_BOOST
            reason = f"Applied successfully, boosting by {self.SUCCESS_BOOST}x"

            # Extra boost if multiple successes
            if context and context.get("consecutive_successes", 0) >= 3:
                new_confidence *= 1.1
                reason += " (3+ consecutive successes)"

        elif outcome == Outcome.FAILURE:
            # User corrected again - pattern was wrong
            new_confidence = current_confidence * self.FAILURE_PENALTY
            reason = f"User corrected, penalizing by {self.FAILURE_PENALTY}x"

            # Extra penalty if high-confidence failure (worse than low-confidence failure)
            if current_confidence > 0.8:
                new_confidence *= 0.9
                reason += " (high-confidence failure)"

        elif outcome == Outcome.PARTIAL:
            # User modified slightly - pattern was close but not perfect
            new_confidence = current_confidence * self.PARTIAL_PENALTY
            reason = f"User modified, slight penalty {self.PARTIAL_PENALTY}x"

        elif outcome == Outcome.IGNORED:
            # Pattern not applied (confidence too low)
            # No change, but track as missed opportunity
            reason = "Pattern not applied (confidence too low)"

        # Apply bounds
        new_confidence = max(self.MIN_CONFIDENCE, min(self.MAX_CONFIDENCE, new_confidence))

        # Apply decay if pattern is old
        if context and "days_since_last_use" in context:
            days_old = context["days_since_last_use"]
            weeks_old = days_old / 7.0
            decay = self.DECAY_PER_WEEK * weeks_old
            new_confidence = max(self.MIN_CONFIDENCE, new_confidence - decay)
            if decay > 0.01:
                reason += f" (decayed by {decay:.2f} due to {weeks_old:.1f} weeks of non-use)"

        return ConfidenceUpdate(
            old_confidence=old_confidence,
            new_confidence=new_confidence,
            reason=reason,
            outcome=outcome
        )

    def should_apply(self, confidence: float) -> bool:
        """Determine if pattern should be auto-applied"""
        return confidence >= self.APPLY_THRESHOLD

    def should_suggest(self, confidence: float) -> bool:
        """Determine if pattern should be suggested to user"""
        return confidence >= self.SUGGEST_THRESHOLD

    def calculate_initial_confidence(
        self,
        correction_text: str,
        project_signals: Optional[list] = None
    ) -> float:
        """
        Calculate initial confidence for a new pattern.

        Args:
            correction_text: The correction text
            project_signals: List of signals from ProjectFileDetector

        Returns:
            Initial confidence (Bayesian prior)
        """
        confidence = self.INITIAL_PRIOR

        # Boost if project files support this
        if project_signals:
            # Example: "use uv" + uv.lock detected → boost confidence
            for signal in project_signals:
                if signal.manager.lower() in correction_text.lower():
                    confidence += signal.confidence * 0.3

        # Boost if correction is very specific
        if len(correction_text.split()) > 5:
            # Longer corrections are more informative
            confidence += 0.1

        # Cap at initial maximum
        return min(0.6, confidence)


# Example usage:
scorer = BayesianConfidenceScorer()

# Initial correction: "use uv not pip"
initial_confidence = scorer.calculate_initial_confidence(
    "use uv not pip",
    project_signals=[PackageManagerSignal(manager="uv", confidence=0.9, ...)]
)
# Output: 0.67 (0.4 base + 0.27 from uv.lock detection)

# User makes same command → pattern applied successfully
update = scorer.update_confidence(initial_confidence, Outcome.SUCCESS)
print(f"Confidence: {update.old_confidence:.2f} → {update.new_confidence:.2f}")
print(f"Reason: {update.reason}")
# Output:
# Confidence: 0.67 → 0.80
# Reason: Applied successfully, boosting by 1.2x

# Should we auto-apply now?
if scorer.should_apply(update.new_confidence):
    print("Auto-applying pattern from now on")
# Output: Auto-applying pattern from now on
```

### 3.4 Cross-Project Learning

```python
"""
Cross-Project Learning Engine - Share patterns across similar projects
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from collections import Counter

@dataclass
class ProjectProfile:
    """Profile of a project for similarity matching"""
    path: str
    project_type: str  # "python-django", "python-fastapi", "node-express"
    package_manager: str
    embedding: np.ndarray  # Embedding of project characteristics
    patterns: List[str]  # Pattern IDs used in this project


class CrossProjectLearner:
    """
    Learn patterns across similar projects.

    Strategy:
    1. Embed project characteristics: dependencies, file structure, config
    2. Find similar projects via AgentDB vector search
    3. If pattern appears in 3+ similar projects → promote to global
    4. Apply project-type-specific patterns (e.g., Django → pytest not unittest)

    Benefits:
    - New Django project → automatically uses patterns from other Django projects
    - Reduces "cold start" for new projects
    - Discovers cross-project conventions (e.g., all FastAPI projects use uvicorn)
    """

    SIMILAR_PROJECT_THRESHOLD = 0.75  # Cosine similarity
    GLOBAL_PROMOTION_THRESHOLD = 3  # Appear in N projects → global

    def __init__(self, embedding_manager, agentdb_store, sqlite_db):
        """
        Initialize cross-project learner.

        Args:
            embedding_manager: EmbeddingManager instance
            agentdb_store: AgentDB VectorStore for project embeddings
            sqlite_db: SQLite connection for pattern tracking
        """
        self.embedder = embedding_manager
        self.agentdb = agentdb_store
        self.db = sqlite_db

    async def create_project_profile(
        self,
        project_path: Path
    ) -> ProjectProfile:
        """
        Create a semantic profile of a project.

        Args:
            project_path: Root directory of project

        Returns:
            ProjectProfile with embedding
        """
        # Extract project characteristics
        characteristics = []

        # 1. Package manager
        detector = ProjectFileDetector()
        pm_signal = await detector.detect(project_path)
        if pm_signal:
            characteristics.append(f"package-manager:{pm_signal.manager}")

        # 2. Project type (detect from dependencies, file structure)
        project_type = self._detect_project_type(project_path, pm_signal)
        characteristics.append(f"type:{project_type}")

        # 3. Dependencies (top 10 most important)
        dependencies = self._extract_key_dependencies(project_path, pm_signal)
        characteristics.extend([f"dep:{dep}" for dep in dependencies[:10]])

        # 4. File structure (presence of key directories)
        structure = self._analyze_structure(project_path)
        characteristics.extend([f"structure:{s}" for s in structure])

        # Create embedding from characteristics
        profile_text = " ".join(characteristics)
        embedding = self.embedder.encode(profile_text, normalize=True)

        # Get patterns used in this project
        patterns = await self._get_project_patterns(str(project_path))

        return ProjectProfile(
            path=str(project_path),
            project_type=project_type,
            package_manager=pm_signal.manager if pm_signal else "unknown",
            embedding=embedding,
            patterns=patterns
        )

    async def find_similar_projects(
        self,
        project_profile: ProjectProfile,
        top_k: int = 10
    ) -> List[ProjectProfile]:
        """
        Find projects similar to the given one.

        Args:
            project_profile: Profile of current project
            top_k: Maximum number of similar projects

        Returns:
            List of similar project profiles
        """
        # Search AgentDB for similar project embeddings
        results = await self.agentdb.search(
            query_vector=project_profile.embedding,
            k=top_k,
            filter={"type": "project_profile"},
            threshold=self.SIMILAR_PROJECT_THRESHOLD
        )

        # Convert to ProjectProfile objects
        similar_projects = []
        for result in results:
            if result["metadata"]["path"] != project_profile.path:  # Exclude self
                similar_projects.append(ProjectProfile(
                    path=result["metadata"]["path"],
                    project_type=result["metadata"]["project_type"],
                    package_manager=result["metadata"]["package_manager"],
                    embedding=np.array(result["vector"]),
                    patterns=result["metadata"]["patterns"]
                ))

        return similar_projects

    async def get_recommended_patterns(
        self,
        project_profile: ProjectProfile
    ) -> List[Dict]:
        """
        Get recommended patterns for a project based on similar projects.

        Args:
            project_profile: Profile of current project

        Returns:
            List of recommended patterns with confidence scores
        """
        # Find similar projects
        similar_projects = await self.find_similar_projects(project_profile)

        if not similar_projects:
            return []

        # Count pattern occurrences across similar projects
        pattern_counts = Counter()
        for project in similar_projects:
            for pattern_id in project.patterns:
                pattern_counts[pattern_id] += 1

        # Calculate confidence based on prevalence
        total_projects = len(similar_projects)
        recommendations = []

        for pattern_id, count in pattern_counts.most_common():
            prevalence = count / total_projects

            # Only recommend if pattern is common enough
            if prevalence >= 0.3:  # Present in 30%+ of similar projects
                # Fetch pattern details from AgentDB
                pattern = await self.agentdb.get(pattern_id)

                recommendations.append({
                    "pattern_id": pattern_id,
                    "text": pattern["metadata"]["text"],
                    "confidence": prevalence,  # Confidence based on prevalence
                    "occurrence_in_similar": count,
                    "total_similar_projects": total_projects,
                    "reason": f"Used in {count}/{total_projects} similar {project_profile.project_type} projects"
                })

        return recommendations

    async def check_global_promotion(self, pattern_id: str) -> bool:
        """
        Check if a pattern should be promoted to global (all projects).

        Args:
            pattern_id: Pattern to check

        Returns:
            True if should be promoted to global CLAUDE.md
        """
        # Query SQLite: how many distinct projects use this pattern?
        cursor = self.db.execute("""
            SELECT COUNT(DISTINCT project_path) as project_count
            FROM pattern_usage
            WHERE pattern_id = ?
        """, (pattern_id,))

        result = cursor.fetchone()
        project_count = result[0] if result else 0

        # Promote if used in 3+ projects
        return project_count >= self.GLOBAL_PROMOTION_THRESHOLD

    def _detect_project_type(
        self,
        project_path: Path,
        pm_signal: Optional[PackageManagerSignal]
    ) -> str:
        """Detect project type from files and dependencies"""
        # Python projects
        if pm_signal and pm_signal.manager in ["uv", "pip", "poetry", "pipenv"]:
            # Check for framework-specific files
            if (project_path / "manage.py").exists():
                return "python-django"
            elif (project_path / "main.py").exists() or (project_path / "app" / "main.py").exists():
                # FastAPI is common with main.py
                return "python-fastapi"
            elif (project_path / "setup.py").exists():
                return "python-library"
            else:
                return "python-application"

        # JavaScript projects
        elif pm_signal and pm_signal.manager in ["npm", "yarn", "pnpm"]:
            package_json = project_path / "package.json"
            if package_json.exists():
                with package_json.open() as f:
                    data = json.load(f)
                    deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}

                    if "next" in deps:
                        return "node-nextjs"
                    elif "react" in deps:
                        return "node-react"
                    elif "express" in deps:
                        return "node-express"
            return "node-application"

        return "unknown"

    def _extract_key_dependencies(
        self,
        project_path: Path,
        pm_signal: Optional[PackageManagerSignal]
    ) -> List[str]:
        """Extract top dependencies from project"""
        dependencies = []

        if pm_signal and pm_signal.manager in ["uv", "poetry"]:
            # Parse pyproject.toml
            pyproject = project_path / "pyproject.toml"
            if pyproject.exists():
                with pyproject.open("rb") as f:
                    data = tomllib.load(f)
                    deps = data.get("project", {}).get("dependencies", [])
                    # Extract package names (before version specifiers)
                    dependencies = [dep.split(">=")[0].split("==")[0].strip() for dep in deps]

        elif pm_signal and pm_signal.manager in ["npm", "yarn", "pnpm"]:
            # Parse package.json
            package_json = project_path / "package.json"
            if package_json.exists():
                with package_json.open() as f:
                    data = json.load(f)
                    dependencies = list(data.get("dependencies", {}).keys())

        return dependencies

    def _analyze_structure(self, project_path: Path) -> List[str]:
        """Analyze project directory structure"""
        structure_signals = []

        # Common directory patterns
        key_dirs = ["src", "tests", "docs", "app", "lib", "components", "api"]
        for dir_name in key_dirs:
            if (project_path / dir_name).is_dir():
                structure_signals.append(dir_name)

        return structure_signals

    async def _get_project_patterns(self, project_path: str) -> List[str]:
        """Get all patterns used in a project from SQLite"""
        cursor = self.db.execute("""
            SELECT DISTINCT pattern_id
            FROM pattern_usage
            WHERE project_path = ?
        """, (project_path,))

        return [row[0] for row in cursor.fetchall()]


# Example usage:
learner = CrossProjectLearner(embedding_manager, agentdb_store, sqlite_db)

# New Django project
project_profile = await learner.create_project_profile(Path("/path/to/new-django-app"))
# Output: ProjectProfile(type="python-django", package_manager="uv", ...)

# Get recommended patterns from similar Django projects
recommendations = await learner.get_recommended_patterns(project_profile)
# Output: [
#   {
#     "pattern_id": "test_framework_pytest",
#     "text": "use pytest not unittest for testing",
#     "confidence": 0.85,
#     "occurrence_in_similar": 17,
#     "total_similar_projects": 20,
#     "reason": "Used in 17/20 similar python-django projects"
#   },
#   ...
# ]

# Check if a pattern should be global
is_global = await learner.check_global_promotion("pkg_mgr_uv_python")
if is_global:
    print("Promoting to global CLAUDE.md")
```

### 3.5 Proactive Application

```python
"""
Proactive Application Layer - Predict and apply patterns before user corrections
"""

from typing import List, Optional, Dict
from dataclasses import dataclass
from enum import Enum

class ApplicationMode(Enum):
    """How to apply a pattern"""
    AUTO_APPLY = "auto_apply"  # Silently apply (high confidence)
    SUGGEST = "suggest"  # Ask user first (medium confidence)
    PASSIVE = "passive"  # Don't apply, wait for correction (low confidence)


@dataclass
class PatternApplication:
    """Represents applying a pattern to a command"""
    pattern_id: str
    pattern_text: str
    confidence: float
    mode: ApplicationMode
    transformation: str  # What to change
    reason: str  # Why this pattern applies


class ProactiveApplicator:
    """
    Proactively apply patterns before user corrections.

    Workflow:
    1. Intercept command: "install pytest"
    2. Search for relevant patterns: "python package installation"
    3. Find: "use uv not pip" (confidence 0.85)
    4. Transform: "install pytest" → "uv pip install pytest"
    5. Inject into Claude's context or auto-execute

    Benefits:
    - Zero corrections for high-confidence patterns
    - Faster workflow (no back-and-forth)
    - Learning happens in background
    """

    def __init__(
        self,
        semantic_clusterer,
        confidence_scorer,
        project_file_detector,
        cross_project_learner
    ):
        """
        Initialize proactive applicator.

        Args:
            semantic_clusterer: SemanticClusterer instance
            confidence_scorer: BayesianConfidenceScorer instance
            project_file_detector: ProjectFileDetector instance
            cross_project_learner: CrossProjectLearner instance
        """
        self.clusterer = semantic_clusterer
        self.scorer = confidence_scorer
        self.detector = project_file_detector
        self.cross_project = cross_project_learner

    async def analyze_command(
        self,
        command: str,
        project_path: Optional[Path] = None
    ) -> List[PatternApplication]:
        """
        Analyze a command and find applicable patterns.

        Args:
            command: User's command (e.g., "install pytest")
            project_path: Current project path (for context)

        Returns:
            List of applicable patterns with modes
        """
        applications = []

        # 1. Detect project context
        project_signal = None
        if project_path:
            project_signal = await self.detector.detect(project_path)

        # 2. Semantic search for relevant patterns
        patterns = await self.clusterer.find_similar(
            query_text=command,
            min_confidence=0.3,  # Low threshold for discovery
            top_k=10
        )

        # 3. Boost confidence with project context
        for pattern in patterns:
            boosted_confidence = pattern.confidence
            boost_reasons = []

            # Boost if project files support this pattern
            if project_signal and project_signal.manager in pattern.text.lower():
                boosted_confidence += 0.3
                boost_reasons.append(f"{project_signal.manager} detected in project")

            # Boost from cross-project learning
            if project_path:
                project_profile = await self.cross_project.create_project_profile(project_path)
                if pattern.id in project_profile.patterns:
                    boosted_confidence += 0.2
                    boost_reasons.append("used in this project before")

            # Determine application mode
            if boosted_confidence >= self.scorer.APPLY_THRESHOLD:
                mode = ApplicationMode.AUTO_APPLY
            elif boosted_confidence >= self.scorer.SUGGEST_THRESHOLD:
                mode = ApplicationMode.SUGGEST
            else:
                mode = ApplicationMode.PASSIVE

            # Create transformation
            transformation = self._create_transformation(command, pattern)

            applications.append(PatternApplication(
                pattern_id=pattern.id,
                pattern_text=pattern.text,
                confidence=boosted_confidence,
                mode=mode,
                transformation=transformation,
                reason=" + ".join([f"Confidence: {pattern.confidence:.2f}"] + boost_reasons)
            ))

        # Sort by confidence
        applications.sort(key=lambda a: a.confidence, reverse=True)

        return applications

    def _create_transformation(self, command: str, pattern: CorrectionPattern) -> str:
        """
        Create the transformation to apply pattern to command.

        Args:
            command: Original command
            pattern: Pattern to apply

        Returns:
            Transformed command
        """
        # Simple heuristics for package manager transformations
        # In production, this would use LLM or rule-based system

        pattern_lower = pattern.text.lower()

        # "use uv not pip" pattern
        if "uv" in pattern_lower and "pip" in pattern_lower:
            if command.startswith("pip install"):
                return command.replace("pip install", "uv pip install")
            elif "install" in command and "pip" not in command:
                return f"uv pip {command}"

        # "use poetry" pattern
        elif "poetry" in pattern_lower:
            if "install" in command:
                pkg = command.split("install")[-1].strip()
                return f"poetry add {pkg}"

        # "use npm" vs "use yarn" vs "use pnpm"
        elif any(pm in pattern_lower for pm in ["npm", "yarn", "pnpm"]):
            for pm in ["npm", "yarn", "pnpm"]:
                if pm in pattern_lower:
                    # Replace package manager in command
                    for old_pm in ["npm", "yarn", "pnpm"]:
                        if old_pm in command and old_pm != pm:
                            return command.replace(old_pm, pm)

        # No transformation possible
        return command

    async def inject_into_context(
        self,
        applications: List[PatternApplication]
    ) -> str:
        """
        Create context injection for Claude's prompt.

        Args:
            applications: List of pattern applications

        Returns:
            Text to inject into system prompt
        """
        if not applications:
            return ""

        # Filter to only auto-apply patterns
        auto_apply = [a for a in applications if a.mode == ApplicationMode.AUTO_APPLY]

        if not auto_apply:
            return ""

        # Build context injection
        lines = ["**Learned Preferences (apply automatically)**:"]
        for app in auto_apply:
            lines.append(f"- {app.pattern_text} (confidence: {app.confidence:.0%})")
            if app.transformation:
                lines.append(f"  Example: `{app.transformation}`")

        return "\n".join(lines)

    async def suggest_to_user(
        self,
        applications: List[PatternApplication]
    ) -> Optional[str]:
        """
        Create suggestion prompt for user (medium confidence patterns).

        Args:
            applications: List of pattern applications

        Returns:
            Suggestion text or None
        """
        # Filter to suggest-mode patterns
        suggest = [a for a in applications if a.mode == ApplicationMode.SUGGEST]

        if not suggest:
            return None

        # Pick top suggestion
        top = suggest[0]

        return (
            f"I notice you might prefer '{top.transformation}' "
            f"(based on: {top.reason}). "
            f"Should I use this from now on?"
        )


# Example usage:
applicator = ProactiveApplicator(
    semantic_clusterer,
    confidence_scorer,
    project_file_detector,
    cross_project_learner
)

# User command: "install pytest"
command = "install pytest"
project_path = Path("/path/to/project")

# Analyze command
applications = await applicator.analyze_command(command, project_path)

# Check what to do
for app in applications:
    if app.mode == ApplicationMode.AUTO_APPLY:
        print(f"Auto-applying: {app.transformation}")
        # Execute: uv pip install pytest
    elif app.mode == ApplicationMode.SUGGEST:
        suggestion = await applicator.suggest_to_user([app])
        print(f"Suggestion: {suggestion}")

# Output:
# Auto-applying: uv pip install pytest
# (No user correction needed!)
```

---

## 4. Integration with Existing System

### 4.1 Modified Pattern Extractor

```python
"""
Enhanced pattern_extractor.py with package manager intelligence
"""

from pathlib import Path
from typing import Optional

class EnhancedPatternExtractor:
    """
    Enhanced pattern extractor with package manager intelligence.

    Integrates:
    - ProjectFileDetector
    - SemanticClusterer (AgentDB)
    - BayesianConfidenceScorer
    - CrossProjectLearner
    - ProactiveApplicator
    """

    def __init__(self, db_path: Path, agentdb_path: Path):
        """Initialize with both SQLite and AgentDB"""
        # Existing SQLite for audit trail
        self.sqlite_db = sqlite3.connect(db_path)

        # New AgentDB for semantic search
        from src.intelligence.memory.embeddings import EmbeddingManager
        from src.intelligence.memory.persistence import PersistentMemory

        self.embedder = EmbeddingManager()
        self.agentdb = PersistentMemory(
            db_path=agentdb_path,
            embedding_model="all-MiniLM-L6-v2"
        )

        # Initialize components
        self.project_detector = ProjectFileDetector()
        self.semantic_clusterer = SemanticClusterer(self.embedder, self.agentdb)
        self.confidence_scorer = BayesianConfidenceScorer()
        self.cross_project_learner = CrossProjectLearner(
            self.embedder,
            self.agentdb,
            self.sqlite_db
        )
        self.applicator = ProactiveApplicator(
            self.semantic_clusterer,
            self.confidence_scorer,
            self.project_detector,
            self.cross_project_learner
        )

    async def process_correction(
        self,
        correction_text: str,
        category: str = "package-manager",
        project_path: Optional[Path] = None
    ) -> dict:
        """
        Process a user correction with full intelligence stack.

        Args:
            correction_text: The correction (e.g., "use uv not pip")
            category: Category of correction
            project_path: Current project path

        Returns:
            Processing result with confidence and recommendations
        """
        # 1. Detect project context
        project_signal = None
        if project_path:
            project_signal = await self.project_detector.detect(project_path)

        # 2. Add to semantic cluster
        pattern_id, is_new = await self.semantic_clusterer.add_correction(
            correction_text,
            category
        )

        # 3. Calculate/update confidence
        if is_new:
            confidence = self.confidence_scorer.calculate_initial_confidence(
                correction_text,
                project_signals=[project_signal] if project_signal else None
            )
        else:
            # Retrieve existing confidence
            pattern = await self.agentdb.get(pattern_id)
            confidence = pattern["metadata"]["confidence"]

        # 4. Store in SQLite for audit
        self.sqlite_db.execute("""
            INSERT INTO pattern_corrections (
                pattern_id,
                correction_text,
                category,
                project_path,
                confidence,
                timestamp
            ) VALUES (?, ?, ?, ?, ?, datetime('now'))
        """, (pattern_id, correction_text, category, str(project_path) if project_path else None, confidence))
        self.sqlite_db.commit()

        # 5. Check for cross-project patterns
        if project_path:
            profile = await self.cross_project_learner.create_project_profile(project_path)
            similar_projects = await self.cross_project_learner.find_similar_projects(profile)

            # Check if should promote to global
            should_promote = await self.cross_project_learner.check_global_promotion(pattern_id)
        else:
            similar_projects = []
            should_promote = False

        # 6. Update CLAUDE.md if confidence crossed threshold
        if confidence >= 0.9 or should_promote:
            from src.intelligence.claudemd_manager import ClaudeMdManager
            manager = ClaudeMdManager()
            await manager.add_preference(
                category=category,
                preference=correction_text,
                confidence=confidence,
                scope="global" if should_promote else "project"
            )

        return {
            "pattern_id": pattern_id,
            "is_new": is_new,
            "confidence": confidence,
            "project_signal": project_signal,
            "similar_projects_count": len(similar_projects),
            "promoted_to_global": should_promote,
            "should_auto_apply": self.confidence_scorer.should_apply(confidence)
        }

    async def predict_for_command(
        self,
        command: str,
        project_path: Optional[Path] = None
    ) -> dict:
        """
        Predict which patterns apply to a command before execution.

        Args:
            command: User's command
            project_path: Current project path

        Returns:
            Prediction result with transformations
        """
        applications = await self.applicator.analyze_command(command, project_path)

        # Get top application
        if applications:
            top = applications[0]

            return {
                "should_transform": top.mode == ApplicationMode.AUTO_APPLY,
                "transformation": top.transformation if top.mode == ApplicationMode.AUTO_APPLY else None,
                "suggestion": await self.applicator.suggest_to_user(applications) if top.mode == ApplicationMode.SUGGEST else None,
                "confidence": top.confidence,
                "reason": top.reason,
                "all_patterns": [
                    {
                        "pattern": a.pattern_text,
                        "confidence": a.confidence,
                        "mode": a.mode.value
                    } for a in applications
                ]
            }

        return {
            "should_transform": False,
            "transformation": None,
            "suggestion": None,
            "all_patterns": []
        }

    async def record_outcome(
        self,
        pattern_id: str,
        outcome: Outcome,
        context: Optional[dict] = None
    ):
        """
        Record the outcome of applying a pattern.

        Args:
            pattern_id: Pattern that was applied
            outcome: Result (success/failure/partial)
            context: Additional context
        """
        # Retrieve current confidence
        pattern = await self.agentdb.get(pattern_id)
        current_confidence = pattern["metadata"]["confidence"]

        # Update confidence
        update = self.confidence_scorer.update_confidence(
            current_confidence,
            outcome,
            context
        )

        # Store outcome in SQLite (ReasoningBank)
        self.sqlite_db.execute("""
            INSERT INTO reasoning_episodes (
                pattern_id,
                outcome,
                confidence_before,
                confidence_after,
                reason,
                timestamp
            ) VALUES (?, ?, ?, ?, ?, datetime('now'))
        """, (
            pattern_id,
            outcome.value,
            update.old_confidence,
            update.new_confidence,
            update.reason
        ))
        self.sqlite_db.commit()

        # Update AgentDB with new confidence
        await self.agentdb.update(
            id=pattern_id,
            metadata={
                **pattern["metadata"],
                "confidence": update.new_confidence,
                "last_outcome": outcome.value,
                "last_updated": time.time()
            }
        )
```

### 4.2 Database Schema Extensions

```sql
-- Add to existing SQLite schema

-- Pattern corrections (audit trail)
CREATE TABLE IF NOT EXISTS pattern_corrections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_id TEXT NOT NULL,
    correction_text TEXT NOT NULL,
    category TEXT NOT NULL,
    project_path TEXT,
    confidence REAL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_pattern_corrections_pattern ON pattern_corrections(pattern_id);
CREATE INDEX idx_pattern_corrections_project ON pattern_corrections(project_path);

-- Reasoning episodes (outcome tracking)
CREATE TABLE IF NOT EXISTS reasoning_episodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_id TEXT NOT NULL,
    outcome TEXT NOT NULL CHECK(outcome IN ('success', 'failure', 'partial', 'ignored')),
    confidence_before REAL,
    confidence_after REAL,
    reason TEXT,
    context TEXT,  -- JSON
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_reasoning_episodes_pattern ON reasoning_episodes(pattern_id);
CREATE INDEX idx_reasoning_episodes_outcome ON reasoning_episodes(outcome);

-- Pattern usage (cross-project tracking)
CREATE TABLE IF NOT EXISTS pattern_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_id TEXT NOT NULL,
    project_path TEXT NOT NULL,
    usage_count INTEGER DEFAULT 1,
    first_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(pattern_id, project_path)
);

CREATE INDEX idx_pattern_usage_pattern ON pattern_usage(pattern_id);
CREATE INDEX idx_pattern_usage_project ON pattern_usage(project_path);

-- Project profiles (for cross-project learning)
CREATE TABLE IF NOT EXISTS project_profiles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_path TEXT NOT NULL UNIQUE,
    project_type TEXT NOT NULL,
    package_manager TEXT,
    dependencies TEXT,  -- JSON array
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_project_profiles_type ON project_profiles(project_type);
```

---

## 5. Test Scenarios

### 5.1 Unit Tests

```python
"""
Unit tests for package manager intelligence system
"""

import pytest
from pathlib import Path
import tempfile
import json

class TestProjectFileDetector:
    """Test project file detection"""

    async def test_detect_uv_from_lock_file(self):
        """Should detect uv from uv.lock file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            (project_path / "uv.lock").touch()

            detector = ProjectFileDetector()
            signal = await detector.detect(project_path)

            assert signal is not None
            assert signal.manager == "uv"
            assert signal.confidence >= 0.9
            assert "lock:uv.lock" in signal.evidence

    async def test_detect_poetry_from_config(self):
        """Should detect poetry from pyproject.toml"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)

            # Create pyproject.toml with [tool.poetry]
            pyproject = project_path / "pyproject.toml"
            pyproject.write_text("""
[tool.poetry]
name = "test-project"
version = "1.0.0"
            """)

            detector = ProjectFileDetector()
            signal = await detector.detect(project_path)

            assert signal is not None
            assert signal.manager == "poetry"
            assert "tool.poetry" in signal.metadata

    async def test_cache_detection_results(self):
        """Should cache detection results for performance"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            (project_path / "uv.lock").touch()

            detector = ProjectFileDetector(cache_ttl_seconds=60)

            # First call - should scan filesystem
            signal1 = await detector.detect(project_path)

            # Delete lock file
            (project_path / "uv.lock").unlink()

            # Second call - should return cached result
            signal2 = await detector.detect(project_path)

            assert signal1.manager == signal2.manager == "uv"


class TestSemanticClusterer:
    """Test semantic clustering"""

    async def test_cluster_similar_corrections(self):
        """Should cluster semantically similar corrections"""
        clusterer = SemanticClusterer(embedding_manager, agentdb_store)

        # Add similar corrections
        id1, is_new1 = await clusterer.add_correction("use uv not pip")
        id2, is_new2 = await clusterer.add_correction("prefer uv over pip")
        id3, is_new3 = await clusterer.add_correction("always use uv for packages")

        # Should merge into same pattern
        assert id1 == id2 == id3
        assert is_new1 == True
        assert is_new2 == False  # Merged
        assert is_new3 == False  # Merged

    async def test_find_similar_patterns(self):
        """Should find patterns via semantic search"""
        clusterer = SemanticClusterer(embedding_manager, agentdb_store)

        # Add pattern
        await clusterer.add_correction("use uv not pip", category="package-manager")

        # Search with different wording
        patterns = await clusterer.find_similar("python package management tools")

        assert len(patterns) > 0
        assert any("uv" in p.text.lower() for p in patterns)


class TestBayesianConfidenceScorer:
    """Test confidence scoring"""

    def test_success_boosts_confidence(self):
        """Successful application should increase confidence"""
        scorer = BayesianConfidenceScorer()

        initial = 0.5
        update = scorer.update_confidence(initial, Outcome.SUCCESS)

        assert update.new_confidence > initial
        assert update.new_confidence <= scorer.MAX_CONFIDENCE

    def test_failure_reduces_confidence(self):
        """Failed application should decrease confidence"""
        scorer = BayesianConfidenceScorer()

        initial = 0.8
        update = scorer.update_confidence(initial, Outcome.FAILURE)

        assert update.new_confidence < initial
        assert update.new_confidence >= scorer.MIN_CONFIDENCE

    def test_confidence_decay_over_time(self):
        """Unused patterns should decay in confidence"""
        scorer = BayesianConfidenceScorer()

        initial = 0.9
        context = {"days_since_last_use": 30}  # 30 days old

        update = scorer.update_confidence(initial, Outcome.IGNORED, context)

        # Should decay (30 days = ~4 weeks = 0.2 decay)
        assert update.new_confidence < initial


class TestCrossProjectLearner:
    """Test cross-project learning"""

    async def test_find_similar_projects(self):
        """Should find projects with similar characteristics"""
        learner = CrossProjectLearner(embedding_manager, agentdb_store, sqlite_db)

        # Create Django project profile
        profile = ProjectProfile(
            path="/path/to/django-app",
            project_type="python-django",
            package_manager="uv",
            embedding=np.random.rand(384),  # Mock
            patterns=["pkg_mgr_uv", "test_framework_pytest"]
        )

        # Store in AgentDB (mock)
        # ... store profile ...

        # Find similar
        similar = await learner.find_similar_projects(profile)

        # Should find other Django projects
        assert all(p.project_type == "python-django" for p in similar)

    async def test_global_promotion_threshold(self):
        """Should promote patterns used in 3+ projects"""
        learner = CrossProjectLearner(embedding_manager, agentdb_store, sqlite_db)

        # Add pattern usage in 3 projects
        for i in range(3):
            sqlite_db.execute("""
                INSERT INTO pattern_usage (pattern_id, project_path)
                VALUES (?, ?)
            """, ("pkg_mgr_uv", f"/project{i}"))
        sqlite_db.commit()

        # Check promotion
        should_promote = await learner.check_global_promotion("pkg_mgr_uv")

        assert should_promote == True


class TestProactiveApplicator:
    """Test proactive application"""

    async def test_auto_apply_high_confidence(self):
        """High confidence patterns should auto-apply"""
        applicator = ProactiveApplicator(
            semantic_clusterer,
            confidence_scorer,
            project_detector,
            cross_project_learner
        )

        # Mock high-confidence pattern in AgentDB
        # ...

        command = "install pytest"
        applications = await applicator.analyze_command(command)

        assert len(applications) > 0
        top = applications[0]

        if top.confidence >= 0.7:
            assert top.mode == ApplicationMode.AUTO_APPLY
            assert "uv" in top.transformation.lower()

    async def test_suggest_medium_confidence(self):
        """Medium confidence patterns should suggest"""
        applicator = ProactiveApplicator(...)

        # Mock medium-confidence pattern
        # ...

        command = "install pytest"
        applications = await applicator.analyze_command(command)

        if applications:
            medium_conf = [a for a in applications if 0.5 <= a.confidence < 0.7]
            if medium_conf:
                assert medium_conf[0].mode == ApplicationMode.SUGGEST
```

### 5.2 Integration Tests

```python
"""
Integration tests for full workflow
"""

class TestPackageManagerIntelligence:
    """End-to-end integration tests"""

    async def test_first_correction_learning(self):
        """First correction should establish pattern with boosted confidence"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            (project_path / "uv.lock").touch()  # Signal: project uses uv

            extractor = EnhancedPatternExtractor(sqlite_db, agentdb_path)

            # User corrects: "use uv not pip"
            result = await extractor.process_correction(
                "use uv not pip",
                category="package-manager",
                project_path=project_path
            )

            # Should detect uv.lock and boost confidence
            assert result["confidence"] >= 0.7  # Base 0.4 + boost 0.3
            assert result["project_signal"].manager == "uv"

    async def test_second_correction_merges(self):
        """Second similar correction should merge into same pattern"""
        extractor = EnhancedPatternExtractor(sqlite_db, agentdb_path)

        # First correction
        result1 = await extractor.process_correction("use uv not pip")
        pattern_id_1 = result1["pattern_id"]

        # Second correction (different wording)
        result2 = await extractor.process_correction("prefer uv over pip")
        pattern_id_2 = result2["pattern_id"]

        # Should merge into same pattern
        assert pattern_id_1 == pattern_id_2
        assert result2["is_new"] == False

    async def test_prediction_applies_pattern(self):
        """After learning, should predict and apply pattern"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            (project_path / "uv.lock").touch()

            extractor = EnhancedPatternExtractor(sqlite_db, agentdb_path)

            # Learn pattern
            await extractor.process_correction(
                "use uv not pip",
                project_path=project_path
            )

            # Predict for command
            prediction = await extractor.predict_for_command(
                "install pytest",
                project_path
            )

            # Should auto-apply
            assert prediction["should_transform"] == True
            assert "uv" in prediction["transformation"].lower()

    async def test_cross_project_learning(self):
        """Pattern should transfer to similar projects"""
        extractor = EnhancedPatternExtractor(sqlite_db, agentdb_path)

        # Project 1: Learn pattern
        project1 = Path("/tmp/django-app-1")
        project1.mkdir(exist_ok=True)
        (project1 / "manage.py").touch()  # Django signal
        (project1 / "uv.lock").touch()

        await extractor.process_correction(
            "use pytest not unittest",
            category="test-framework",
            project_path=project1
        )

        # Project 2: Similar Django project
        project2 = Path("/tmp/django-app-2")
        project2.mkdir(exist_ok=True)
        (project2 / "manage.py").touch()  # Django signal

        # Should recommend pytest (from similar project)
        prediction = await extractor.predict_for_command(
            "run tests",
            project_path=project2
        )

        # Should suggest pytest
        assert len(prediction["all_patterns"]) > 0
        assert any("pytest" in p["pattern"].lower() for p in prediction["all_patterns"])

    async def test_outcome_tracking_adjusts_confidence(self):
        """Success/failure outcomes should adjust confidence"""
        extractor = EnhancedPatternExtractor(sqlite_db, agentdb_path)

        # Learn pattern
        result = await extractor.process_correction("use uv not pip")
        pattern_id = result["pattern_id"]
        initial_confidence = result["confidence"]

        # Record success
        await extractor.record_outcome(pattern_id, Outcome.SUCCESS)

        # Check confidence increased
        pattern = await extractor.agentdb.get(pattern_id)
        new_confidence = pattern["metadata"]["confidence"]

        assert new_confidence > initial_confidence
```

### 5.3 Performance Tests

```python
"""
Performance benchmarks
"""

import time

class TestPerformance:
    """Performance benchmarks"""

    async def test_project_detection_speed(self):
        """Project detection should be <10ms"""
        detector = ProjectFileDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            (project_path / "uv.lock").touch()

            start = time.time()
            signal = await detector.detect(project_path)
            duration_ms = (time.time() - start) * 1000

            assert duration_ms < 10

    async def test_semantic_search_speed(self):
        """Semantic search should be <5ms"""
        clusterer = SemanticClusterer(embedding_manager, agentdb_store)

        # Pre-populate with 1000 patterns
        for i in range(1000):
            await clusterer.add_correction(f"pattern {i}")

        # Search
        start = time.time()
        patterns = await clusterer.find_similar("test query")
        duration_ms = (time.time() - start) * 1000

        assert duration_ms < 5

    async def test_end_to_end_latency(self):
        """Full workflow should be <50ms"""
        extractor = EnhancedPatternExtractor(sqlite_db, agentdb_path)

        start = time.time()
        prediction = await extractor.predict_for_command("install pytest")
        duration_ms = (time.time() - start) * 1000

        assert duration_ms < 50
```

---

## 6. Success Metrics

### 6.1 Quantitative Metrics

| Metric | Baseline (Current) | Target (v2) | Measurement Method |
|--------|-------------------|-------------|-------------------|
| **Corrections to Learn** | 3-5 | 1-2 | Count corrections until pattern confidence >0.7 |
| **Learning Time** | 2-3 days | Same session | Time from first to last correction |
| **Prediction Accuracy** | N/A (no prediction) | >85% | Correct predictions / total commands |
| **False Positive Rate** | N/A | <5% | Incorrect auto-applies / total auto-applies |
| **Context Token Reduction** | 0 | -2,000 | Fewer repeated instructions in CLAUDE.md |
| **Detection Latency** | N/A | <10ms | Time to detect project package manager |
| **Search Latency** | 50ms+ (FTS5) | <5ms | Time to search similar patterns (AgentDB) |

### 6.2 Qualitative Metrics

| Aspect | Success Criteria |
|--------|-----------------|
| **User Experience** | Users report "Claude learned my preference after 1-2 corrections" |
| **Transparency** | Users understand why pattern was applied (clear reasoning) |
| **Accuracy** | Auto-applied patterns match user's actual preferences >90% of time |
| **Adaptability** | System adjusts confidence when user changes preferences |
| **Cross-Project** | Patterns learned in one project apply to similar projects |

### 6.3 A/B Test Design

```python
"""
A/B test to measure impact of package manager intelligence
"""

# Control Group (current system):
# - Keyword-based pattern matching
# - Fixed threshold (3 occurrences)
# - No project context detection
# - No semantic clustering

# Treatment Group (new system):
# - Semantic pattern clustering
# - Bayesian confidence scoring
# - Project file detection
# - Cross-project learning
# - Proactive application

# Metrics to track:
metrics = {
    "corrections_to_learn": [],  # Per pattern
    "time_to_learn_hours": [],  # Time from first to confident
    "false_positives": [],  # Incorrect auto-applies
    "user_satisfaction_rating": [],  # 1-5 scale
    "context_tokens_saved": [],  # Tokens not sent repeatedly
}

# Minimum sample size: 50 users per group (100 total)
# Test duration: 2 weeks
# Success criteria:
# - 50%+ reduction in corrections_to_learn
# - 80%+ reduction in time_to_learn
# - <5% false_positive_rate
# - >4.0 user_satisfaction_rating
```

---

## 7. Implementation Roadmap

### 7.1 Phase 1: Foundation (Week 1)

**Goal**: Set up core infrastructure

Tasks:
1. Install dependencies
   ```bash
   # Add to pyproject.toml
   dependencies = [
       "sentence-transformers>=2.2.0",
       "faiss-cpu>=1.7.4",
       "numpy>=1.24.0"
   ]
   ```

2. Implement `ProjectFileDetector`
   - File: `/src/intelligence/package_mgr/detector.py`
   - Tests: `/tests/test_detector.py`

3. Extend database schema
   - Add tables: `pattern_corrections`, `reasoning_episodes`, `pattern_usage`, `project_profiles`
   - Migration script: `/src/mcp_standards/schema_migration.py`

4. Set up AgentDB integration
   - Initialize PersistentMemory (already exists in `/src/intelligence/memory/persistence.py`)
   - Configure for package manager patterns

**Deliverables**:
- Working project file detection (<10ms)
- Database schema extended
- 80%+ test coverage

### 7.2 Phase 2: Semantic Clustering (Week 2)

**Goal**: Enable semantic pattern matching

Tasks:
1. Implement `SemanticClusterer`
   - File: `/src/intelligence/package_mgr/clusterer.py`
   - Integrate with existing `EmbeddingManager`

2. Implement `BayesianConfidenceScorer`
   - File: `/src/intelligence/package_mgr/scorer.py`
   - Bayesian update logic

3. Update `pattern_extractor.py`
   - Add semantic clustering calls
   - Store patterns in AgentDB

4. Integration tests
   - Test merging of similar corrections
   - Test confidence updates

**Deliverables**:
- Semantic clustering working (<5ms search)
- Corrections reduced: 3 → 2 (intermediate milestone)
- Integration tests passing

### 7.3 Phase 3: Cross-Project & Proactive (Week 3)

**Goal**: Enable cross-project learning and proactive application

Tasks:
1. Implement `CrossProjectLearner`
   - File: `/src/intelligence/package_mgr/cross_project.py`
   - Project profile embeddings

2. Implement `ProactiveApplicator`
   - File: `/src/intelligence/package_mgr/applicator.py`
   - Command analysis and transformation

3. Integrate with CLAUDE.md manager
   - Auto-update when patterns promoted
   - Event-driven updates

4. End-to-end tests
   - Full workflow tests
   - Performance benchmarks

**Deliverables**:
- Cross-project learning working
- Proactive prediction >85% accuracy
- Corrections reduced: 3 → 1 (final goal)

### 7.4 Phase 4: Polish & Deploy (Week 4)

**Goal**: Production-ready system

Tasks:
1. Performance optimization
   - Cache tuning
   - Batch operations
   - Memory profiling

2. Error handling
   - Graceful degradation (if AgentDB fails → fallback to keyword matching)
   - User-friendly error messages

3. Documentation
   - API documentation
   - User guide
   - Architecture diagrams

4. A/B test setup
   - Metrics collection
   - Control vs treatment groups

**Deliverables**:
- Production-ready code
- <50ms end-to-end latency
- Complete documentation
- A/B test running

---

## 8. Risk Mitigation

### Risk 1: Embedding Generation Latency

**Risk**: Generating embeddings for every correction adds latency

**Impact**: Medium (user experience)

**Mitigation**:
- Use fast local model (all-MiniLM-L6-v2: ~50ms per embedding)
- Cache embeddings for common patterns
- Batch embed corrections (if multiple in one session)
- Fallback to keyword matching if embedding fails

**Status**: Low concern (existing EmbeddingManager is fast)

### Risk 2: False Positives

**Risk**: Auto-applying wrong pattern frustrates users

**Impact**: High (user trust)

**Mitigation**:
- Conservative confidence threshold (0.7 for auto-apply)
- Suggest mode for medium confidence (0.5-0.7)
- Track false positives and demote patterns
- Allow user to disable auto-apply

**Status**: Mitigated through Bayesian scoring

### Risk 3: Storage Bloat

**Risk**: AgentDB + SQLite = 2x storage

**Impact**: Low (disk space cheap)

**Mitigation**:
- Prune old low-confidence patterns (monthly)
- Compress embeddings (float16 instead of float32)
- Limit AgentDB to 100K patterns (sufficient for most users)

**Status**: Acceptable tradeoff

### Risk 4: Semantic Clustering Errors

**Risk**: Different patterns merged incorrectly (e.g., "use uv" + "use poetry")

**Impact**: Medium (learning accuracy)

**Mitigation**:
- High similarity threshold (0.85 for merging)
- Manual review for promoted patterns
- User can "unmerge" patterns via tool

**Status**: Low concern (threshold tuned conservatively)

---

## 9. Conclusion

This comprehensive package manager intelligence system reduces user corrections from 3-5 to 1-2 through:

1. **Intelligent Detection**: Automatic project file analysis (uv.lock, poetry.lock, etc.) provides immediate context
2. **Semantic Clustering**: AgentDB embeddings cluster similar corrections ("use uv" + "prefer uv" = same pattern)
3. **Bayesian Confidence**: Success/failure tracking adjusts confidence probabilistically
4. **Cross-Project Learning**: Patterns transfer across similar projects
5. **Proactive Application**: Predict and apply before corrections needed

**Expected Impact**:
- 60-70% reduction in repetitive corrections
- Learning time: days → same session
- Context pollution: -2,000 tokens
- User satisfaction: "Finally, it learns!"

**Implementation**: 4 weeks, phased rollout, A/B tested

This system transforms the frustrating "use uv not pip" loop into a one-time learning experience, delivering on the core promise of mcp-standards: **learn once, apply forever**.
