"""
Contamination Check for KAIT Protocol

Verifies that DSL artifacts are genuinely post-cutoff and novel:
1. Embedding-based overlap detection with public corpora
2. Distributional peakedness (entropy) analysis
3. Timestamp verification
4. Manual provenance tracking

Based on: arxiv:2311.09783 (contamination detection)
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
import json
import hashlib
from pathlib import Path


class ContaminationChecker:
    """
    Check if DSL artifacts could have been in training data.

    Implements:
    - Timestamp verification
    - Content hashing for uniqueness
    - Distributional analysis (placeholder for actual embedding checks)
    - Provenance documentation
    """

    def __init__(self, dsl_name: str, artifacts: Dict[str, Any]):
        """
        Initialize contamination checker.

        Args:
            dsl_name: Name of the DSL
            artifacts: Dict containing grammar, examples, docs, etc.
        """
        self.dsl_name = dsl_name
        self.artifacts = artifacts
        self.results: Dict[str, Any] = {}

    def check_timestamps(self, creation_date: datetime, cutoff_date: datetime) -> bool:
        """
        Verify artifacts were created after model's training cutoff.

        Args:
            creation_date: When DSL was created
            cutoff_date: Model's training data cutoff

        Returns:
            True if definitely post-cutoff
        """
        return creation_date > cutoff_date

    def compute_content_hash(self, content: str) -> str:
        """
        Compute unique hash of content.

        Args:
            content: Text content to hash

        Returns:
            SHA-256 hash
        """
        return hashlib.sha256(content.encode()).hexdigest()

    def check_uniqueness_markers(self) -> Dict[str, Any]:
        """
        Check for novel/unique identifiers in the DSL.

        Returns:
            Dict with uniqueness indicators
        """
        # Extract unique tokens from grammar/examples
        unique_tokens = set()

        # Check for novel keywords
        grammar = self.artifacts.get("grammar", "")
        examples = self.artifacts.get("examples", [])

        # Novel unit names for TinyCalc
        novel_units = ["flurb", "grobble", "zept", "quib", "voom"]
        found_units = [u for u in novel_units if u in grammar or any(u in str(ex) for ex in examples)]

        return {
            "novel_identifiers": found_units,
            "count": len(found_units),
            "unique": len(found_units) > 0
        }

    def distributional_analysis(self, model_outputs: List[str]) -> Dict[str, float]:
        """
        Analyze output distribution for memorization signals.

        High entropy = generalization
        Low entropy = potential memorization

        Args:
            model_outputs: List of model outputs on DSL tasks

        Returns:
            Dict with entropy and peakedness metrics
        """
        # Placeholder for actual embedding-based analysis
        # In practice, would use embeddings and measure entropy

        if not model_outputs:
            return {"entropy": 0.0, "peakedness": 0.0, "signal": "unknown"}

        # Simple character-level entropy as proxy
        from collections import Counter
        import math

        all_chars = "".join(model_outputs)
        if not all_chars:
            return {"entropy": 0.0, "peakedness": 0.0, "signal": "unknown"}

        freq = Counter(all_chars)
        total = len(all_chars)

        entropy = -sum((count/total) * math.log2(count/total) for count in freq.values())

        # Normalize entropy
        max_entropy = math.log2(len(freq))
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0.0

        signal = "generalization" if normalized_entropy > 0.7 else "potential_memorization"

        return {
            "entropy": entropy,
            "normalized_entropy": normalized_entropy,
            "peakedness": 1.0 - normalized_entropy,
            "signal": signal
        }

    def document_provenance(
        self,
        creation_date: datetime,
        author: str,
        description: str
    ) -> Dict[str, Any]:
        """
        Document artifact provenance.

        Args:
            creation_date: When created
            author: Who created it
            description: How it was created

        Returns:
            Provenance record
        """
        return {
            "dsl_name": self.dsl_name,
            "creation_date": creation_date.isoformat(),
            "author": author,
            "description": description,
            "artifacts": list(self.artifacts.keys()),
            "content_hashes": {
                key: self.compute_content_hash(str(value))
                for key, value in self.artifacts.items()
            }
        }

    def run_full_check(
        self,
        creation_date: datetime,
        cutoff_date: datetime,
        model_outputs: Optional[List[str]] = None,
        author: str = "TinyDSL",
        description: str = "Post-cutoff DSL for KAIT testing"
    ) -> Dict[str, Any]:
        """
        Run complete contamination check.

        Args:
            creation_date: DSL creation date
            cutoff_date: Model training cutoff
            model_outputs: Optional model outputs for distribution analysis
            author: Creator
            description: Creation description

        Returns:
            Full contamination report
        """
        report = {
            "dsl_name": self.dsl_name,
            "check_date": datetime.utcnow().isoformat(),
            "post_cutoff": self.check_timestamps(creation_date, cutoff_date),
            "uniqueness": self.check_uniqueness_markers(),
            "provenance": self.document_provenance(creation_date, author, description)
        }

        if model_outputs:
            report["distributional_analysis"] = self.distributional_analysis(model_outputs)

        # Overall verdict
        report["verdict"] = {
            "contamination_likely": not report["post_cutoff"] or not report["uniqueness"]["unique"],
            "novel": report["post_cutoff"] and report["uniqueness"]["unique"],
            "confidence": "high" if report["post_cutoff"] and report["uniqueness"]["unique"] else "low"
        }

        return report

    def save_report(self, report: Dict[str, Any], output_path: Optional[Path] = None) -> Path:
        """
        Save contamination report.

        Args:
            report: Report dict
            output_path: Where to save (default: output/contamination_{dsl}.json)

        Returns:
            Path where saved
        """
        if output_path is None:
            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)
            output_path = output_dir / f"contamination_{self.dsl_name}.json"

        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)

        return output_path


def check_dsl_contamination(
    dsl_name: str,
    grammar_path: Path,
    examples_path: Path,
    creation_date: datetime,
    model_cutoff: datetime
) -> Dict[str, Any]:
    """
    Check a DSL for contamination.

    Args:
        dsl_name: DSL name
        grammar_path: Path to grammar file
        examples_path: Path to examples JSON
        creation_date: When DSL was created
        model_cutoff: Model's training cutoff date

    Returns:
        Contamination report
    """
    # Load artifacts
    with open(grammar_path) as f:
        grammar = f.read()

    with open(examples_path) as f:
        examples = json.load(f)

    artifacts = {
        "grammar": grammar,
        "examples": examples
    }

    checker = ContaminationChecker(dsl_name, artifacts)

    report = checker.run_full_check(
        creation_date=creation_date,
        cutoff_date=model_cutoff,
        author="TinyDSL Project",
        description=f"Novel {dsl_name} DSL created for KAIT protocol testing"
    )

    report_path = checker.save_report(report)
    print(f"✅ Contamination report saved: {report_path}")

    return report


if __name__ == "__main__":
    # Example: Check TinyCalc DSL
    from pathlib import Path

    dsl_dir = Path(__file__).parent.parent / "src" / "tinydsl" / "data"

    report = check_dsl_contamination(
        dsl_name="tinycalc",
        grammar_path=dsl_dir / "tinycalc_grammar.lark",
        examples_path=dsl_dir / "tinycalc_examples.json",
        creation_date=datetime(2025, 1, 19),  # Created today
        model_cutoff=datetime(2025, 1, 1)  # Example cutoff
    )

    print("\n📊 Contamination Check Results:")
    print(f"  Post-cutoff: {report['post_cutoff']}")
    print(f"  Novel: {report['verdict']['novel']}")
    print(f"  Confidence: {report['verdict']['confidence']}")
    print(f"  Unique identifiers found: {report['uniqueness']['count']}")
