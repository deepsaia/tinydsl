"""
KAIT Agent - Integrates KAIT evaluation protocol with agent tools.

Provides agent-friendly interface for running KAIT experiments.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pathlib import Path
import json
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../../"))

from tinydsl.agent_tools.generic_dsl_client import GenericDSLClient


class KAITAgent:
    """
    Agent interface for KAIT protocol experiments.

    Wraps the DSL client and KAIT evaluator for agent-friendly usage.
    """

    def __init__(
        self,
        dsl_name: str,
        base_url: str = "http://localhost:8008/api",
        check_contamination: bool = True,
        creation_date: Optional[datetime] = None,
        model_cutoff: Optional[datetime] = None,
    ):
        """
        Initialize KAIT agent.

        Args:
            dsl_name: DSL to test (e.g., 'tinycalc', 'lexi')
            base_url: API base URL
            check_contamination: Whether to run contamination check
            creation_date: DSL creation date (for contamination check)
            model_cutoff: Model training cutoff date (for contamination check)
        """
        self.dsl_name = dsl_name
        self.client = GenericDSLClient(base_url)
        self.baseline_results = None
        self.post_exposure_results = None
        self.transfer_results = None
        self.contamination_report = None

        # Run contamination check if requested
        if check_contamination:
            self.contamination_report = self._run_contamination_check(
                creation_date=creation_date, model_cutoff=model_cutoff
            )

    def run_baseline(self, task_ids: List[str]) -> Dict[str, Any]:
        """
        Run baseline evaluation (before exposure).

        Args:
            task_ids: Task IDs for baseline evaluation

        Returns:
            Baseline results with accuracy
        """
        print(f"📊 Running baseline evaluation on {len(task_ids)} tasks...")
        results = self.client.run_all_tasks(self.dsl_name, task_ids)

        self.baseline_results = {
            "task_ids": task_ids,
            "accuracy": results["evaluation"]["summary"]["accuracy"],
            "details": results["evaluation"]["details"],
        }

        print(f"✅ Baseline accuracy: {self.baseline_results['accuracy']:.2%}")
        return self.baseline_results

    def expose(
        self, episodes: List[str], token_budget: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Exposure phase - agent learns from episodes.

        Args:
            episodes: List of DSL code snippets to learn from
            token_budget: Optional token limit

        Returns:
            Exposure results with online accuracies
        """
        print(f"🎓 Running exposure phase with {len(episodes)} episodes...")

        online_accuracies = []
        total_tokens = 0

        for i, episode_code in enumerate(episodes):
            try:
                # Run the episode
                result = self.client.run(self.dsl_name, episode_code)

                # Simulate accuracy tracking (in real scenario, would test after each episode)
                # For now, just track success
                online_accuracies.append(1.0 if result.get("status") == "ok" else 0.0)

                # Token counting (rough estimate)
                total_tokens += len(episode_code.split())

                if token_budget and total_tokens >= token_budget:
                    print(f"⚠️ Token budget reached after {i+1} episodes")
                    break

            except Exception as e:
                print(f"❌ Episode {i+1} failed: {e}")
                online_accuracies.append(0.0)

        exposure_results = {
            "episodes_completed": len(online_accuracies),
            "total_tokens": total_tokens,
            "online_accuracies": online_accuracies,
            "final_accuracy": online_accuracies[-1] if online_accuracies else 0.0,
        }

        print(
            f"✅ Exposure complete: {exposure_results['final_accuracy']:.2%} final accuracy"
        )
        return exposure_results

    def run_post_exposure(self, task_ids: List[str]) -> Dict[str, Any]:
        """
        Post-exposure evaluation (persistence test).

        Args:
            task_ids: Task IDs for post-exposure evaluation (can overlap with baseline)

        Returns:
            Post-exposure results
        """
        print(f"📈 Running post-exposure evaluation on {len(task_ids)} tasks...")
        results = self.client.run_all_tasks(self.dsl_name, task_ids)

        self.post_exposure_results = {
            "task_ids": task_ids,
            "accuracy": results["evaluation"]["summary"]["accuracy"],
            "details": results["evaluation"]["details"],
        }

        print(
            f"✅ Post-exposure accuracy: {self.post_exposure_results['accuracy']:.2%}"
        )

        # Calculate acquisition gain
        if self.baseline_results:
            ag = (
                self.post_exposure_results["accuracy"]
                - self.baseline_results["accuracy"]
            )
            print(f"📊 Acquisition Gain (AG): {ag:+.2%}")

        return self.post_exposure_results

    def run_transfer(self, transfer_task_ids: List[str]) -> Dict[str, Any]:
        """
        Transfer evaluation (novel compositional tasks).

        Args:
            transfer_task_ids: Task IDs for transfer testing (must be different from baseline)

        Returns:
            Transfer results
        """
        print(f"🔄 Running transfer evaluation on {len(transfer_task_ids)} tasks...")
        results = self.client.run_all_tasks(self.dsl_name, transfer_task_ids)

        self.transfer_results = {
            "task_ids": transfer_task_ids,
            "accuracy": results["evaluation"]["summary"]["accuracy"],
            "details": results["evaluation"]["details"],
        }

        print(f"✅ Transfer Score (TS): {self.transfer_results['accuracy']:.2%}")
        return self.transfer_results

    def _run_contamination_check(
        self,
        creation_date: Optional[datetime] = None,
        model_cutoff: Optional[datetime] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Run contamination check for the DSL.

        Args:
            creation_date: DSL creation date (defaults to 2024-10-18)
            model_cutoff: Model training cutoff (defaults to 2025-01-01)

        Returns:
            Contamination report or None if check fails
        """
        try:
            # Import here to avoid circular dependencies
            sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
            from scripts.check_contamination import ContaminationChecker

            # Default dates
            if creation_date is None:
                creation_date = datetime(2024, 10, 18)
            if model_cutoff is None:
                model_cutoff = datetime(2025, 1, 1)

            # Load DSL artifacts
            data_dir = Path(__file__).parent.parent / "data"
            grammar_path = data_dir / f"{self.dsl_name}_grammar.lark"
            examples_path = data_dir / f"{self.dsl_name}_examples.json"

            if not grammar_path.exists():
                print(f"⚠️  Grammar file not found: {grammar_path}")
                return None

            # Load grammar
            with open(grammar_path) as f:
                grammar = f.read()

            # Load examples (optional)
            examples = []
            if examples_path.exists():
                with open(examples_path) as f:
                    examples = json.load(f)

            artifacts = {"grammar": grammar, "examples": examples}

            # Run contamination check
            checker = ContaminationChecker(self.dsl_name, artifacts)
            report = checker.run_full_check(
                creation_date=creation_date,
                cutoff_date=model_cutoff,
                author="TinyDSL Project",
                description=f"Novel {self.dsl_name} DSL for KAIT protocol testing",
            )

            print(f"✅ Contamination check complete for {self.dsl_name}")
            print(f"   Post-cutoff: {report['post_cutoff']}")
            print(f"   Novel identifiers: {report['uniqueness']['count']}")
            print(f"   Confidence: {report['verdict']['confidence']}")

            return report

        except Exception as e:
            print(f"⚠️  Contamination check failed: {e}")
            return None

    def generate_report(self) -> Dict[str, Any]:
        """
        Generate full KAIT report.

        Returns:
            Comprehensive report with all metrics
        """
        if not self.baseline_results or not self.post_exposure_results:
            raise ValueError(
                "Must run baseline and post-exposure before generating report"
            )

        ag = self.post_exposure_results["accuracy"] - self.baseline_results["accuracy"]
        ts = self.transfer_results["accuracy"] if self.transfer_results else 0.0

        report = {
            "experiment_id": f"{self.dsl_name}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
            "dsl": self.dsl_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metrics": {
                "baseline_accuracy": self.baseline_results["accuracy"],
                "post_exposure_accuracy": self.post_exposure_results["accuracy"],
                "acquisition_gain": ag,
                "transfer_score": ts,
            },
            "baseline": self.baseline_results,
            "post_exposure": self.post_exposure_results,
            "transfer": self.transfer_results,
            "contamination": self.contamination_report,
        }

        return report

    def save_report(self, filepath: Optional[str] = None):
        """
        Save report to JSON file.

        Args:
            filepath: Optional path (default: output/kait_agent_{dsl}_{timestamp}.json)
        """

        report = self.generate_report()

        if filepath is None:
            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)
            filepath = (
                output_dir
                / f"kait_agent_{self.dsl_name}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
            )

        with open(filepath, "w") as f:
            json.dump(report, f, indent=2)

        print(f"💾 Report saved to {filepath}")
        return filepath


def run_kait_experiment_simple(
    dsl_name: str,
    baseline_tasks: List[str],
    exposure_episodes: List[str],
    post_exposure_tasks: List[str],
    transfer_tasks: List[str],
    token_budget: int = 5000,
) -> Dict[str, Any]:
    """
    Run a complete KAIT experiment with simple interface.

    Args:
        dsl_name: DSL to test
        baseline_tasks: Task IDs for baseline
        exposure_episodes: Learning episodes
        post_exposure_tasks: Task IDs for persistence test
        transfer_tasks: Task IDs for transfer test
        token_budget: Token limit for exposure

    Returns:
        Full KAIT report
    """
    agent = KAITAgent(dsl_name)

    # Run phases
    agent.run_baseline(baseline_tasks)
    agent.expose(exposure_episodes, token_budget)
    agent.run_post_exposure(post_exposure_tasks)
    agent.run_transfer(transfer_tasks)

    # Generate and save report
    report = agent.generate_report()
    agent.save_report()

    return report


if __name__ == "__main__":
    # Example: Run KAIT experiment on TinyCalc
    print("🧪 Starting KAIT experiment on TinyCalc...\n")

    report = run_kait_experiment_simple(
        dsl_name="tinycalc",
        baseline_tasks=["001", "002", "003"],
        exposure_episodes=[
            "define 1 flurb = 3 grobbles",
            "define 1 grobble = 2 zepts",
            "convert 10 flurbs to grobbles",
            "convert 5 grobbles to zepts",
            "compute 10 flurbs + 5 grobbles in zepts",
        ],
        post_exposure_tasks=["001", "002", "003", "004"],
        transfer_tasks=["010", "011", "012"],
        token_budget=1000,
    )

    print("\n📈 Final Metrics:")
    print(f"  Baseline Accuracy: {report['metrics']['baseline_accuracy']:.2%}")
    print(
        f"  Post-Exposure Accuracy: {report['metrics']['post_exposure_accuracy']:.2%}"
    )
    print(f"  Acquisition Gain (AG): {report['metrics']['acquisition_gain']:+.2%}")
    print(f"  Transfer Score (TS): {report['metrics']['transfer_score']:.2%}")
