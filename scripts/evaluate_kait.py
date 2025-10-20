"""
KAIT Protocol Evaluation - Knowledge Acquisition & Inter-task Transfer

Calculates metrics for measuring LLM knowledge acquisition:
- AG (Acquisition Gain): Δ accuracy from baseline → post-exposure
- TS (Transfer Score): Accuracy on novel compositional tasks
- R(Δt): Retention after time delay
- Sample Efficiency: AG per 1k exposure tokens
- Stability-Plasticity Index: Prior skills retained vs new skills gained
- Prequential Regret: Online learning performance
"""

from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import json
from pathlib import Path


class KAITEvaluator:
    """
    Evaluator for KAIT protocol metrics.

    Tracks performance across three phases:
    1. Baseline (B): Zero-shot and few-shot performance
    2. Exposure (E): Learning stream with limited tokens
    3. Post-exposure (P): Persistence and transfer tests
    """

    def __init__(self, experiment_id: str, config: Dict[str, Any]):
        """
        Initialize KAIT evaluator.

        Args:
            experiment_id: Unique identifier for this experiment
            config: Configuration dict with:
                - dsl: DSL name
                - agent_model: LLM model identifier
                - exposure_tokens: Token budget for exposure phase
                - tasks: Task definitions
        """
        self.experiment_id = experiment_id
        self.config = config
        self.results: Dict[str, Any] = {
            "baseline": {},
            "exposure": {},
            "post_exposure": {},
            "transfer": {},
            "retention": {},
        }

    def calculate_acquisition_gain(
        self, baseline_accuracy: float, post_exposure_accuracy: float
    ) -> float:
        """
        AG = Δ accuracy from B→P on T_persist

        Args:
            baseline_accuracy: Accuracy before exposure
            post_exposure_accuracy: Accuracy after exposure on same tasks

        Returns:
            Acquisition gain (absolute improvement)
        """
        return post_exposure_accuracy - baseline_accuracy

    def calculate_transfer_score(self, transfer_results: Dict[str, Any]) -> float:
        """
        TS: Accuracy on novel compositional transfer tasks.

        Args:
            transfer_results: Results from transfer task evaluation

        Returns:
            Transfer accuracy
        """
        return transfer_results.get("accuracy", 0.0)

    def calculate_retention(self, t0_accuracy: float, t_delta_accuracy: float) -> float:
        """
        R(Δt): Retention after time delay.

        Args:
            t0_accuracy: Accuracy immediately after exposure
            t_delta_accuracy: Accuracy after delay period

        Returns:
            Retention ratio (1.0 = perfect retention)
        """
        if t0_accuracy == 0:
            return 0.0
        return t_delta_accuracy / t0_accuracy

    def calculate_sample_efficiency(
        self, acquisition_gain: float, exposure_tokens: int
    ) -> float:
        """
        Sample efficiency: AG per 1k exposure tokens.

        Args:
            acquisition_gain: Acquisition gain (AG)
            exposure_tokens: Number of tokens in exposure stream

        Returns:
            AG per 1000 tokens
        """
        if exposure_tokens == 0:
            return 0.0
        return acquisition_gain / (exposure_tokens / 1000)

    def calculate_compute_efficiency(
        self, acquisition_gain: float, tflops: float
    ) -> float:
        """
        Compute efficiency: AG per TFLOP.

        Args:
            acquisition_gain: Acquisition gain
            tflops: Compute used during exposure (in TFLOP)

        Returns:
            AG per TFLOP
        """
        if tflops == 0:
            return 0.0
        return acquisition_gain / tflops

    def stability_plasticity_index(
        self, prior_skills_retained: float, new_skills_gained: float
    ) -> Dict[str, float]:
        """
        Stability-plasticity trade-off.

        Args:
            prior_skills_retained: Fraction of previously mastered skills still correct
            new_skills_gained: Fraction of new skills acquired

        Returns:
            Dict with stability, plasticity, and ratio
        """
        ratio = (
            prior_skills_retained / new_skills_gained
            if new_skills_gained > 0
            else float("inf")
        )

        return {
            "stability": prior_skills_retained,
            "plasticity": new_skills_gained,
            "ratio": ratio,
            "balanced": abs(prior_skills_retained - new_skills_gained) < 0.1,
        }

    def prequential_regret(self, online_accuracies: List[float]) -> Dict[str, float]:
        """
        Prequential/dynamic regret during learning stream.

        Measures how quickly competence rises online.

        Args:
            online_accuracies: Accuracy at each step in exposure stream

        Returns:
            Dict with total regret, average regret, and final accuracy
        """
        if not online_accuracies:
            return {"total_regret": 0.0, "avg_regret": 0.0, "final_accuracy": 0.0}

        ideal_accuracies = [1.0] * len(online_accuracies)
        regrets = [
            ideal - actual for ideal, actual in zip(ideal_accuracies, online_accuracies)
        ]

        return {
            "total_regret": sum(regrets),
            "avg_regret": sum(regrets) / len(regrets),
            "final_accuracy": online_accuracies[-1] if online_accuracies else 0.0,
            "learning_curve": online_accuracies,
        }

    def store_phase_results(self, phase: str, results: Dict[str, Any]) -> None:
        """Store results for a phase."""
        self.results[phase] = results

    def generate_report(self) -> Dict[str, Any]:
        """
        Generate full KAIT evaluation report.

        Returns:
            Comprehensive report with all metrics
        """
        # Extract key values
        baseline_acc = self.results["baseline"].get("accuracy", 0.0)
        post_exposure_acc = self.results["post_exposure"].get("accuracy", 0.0)
        transfer_acc = self.results["transfer"].get("accuracy", 0.0)

        ag = self.calculate_acquisition_gain(baseline_acc, post_exposure_acc)
        ts = transfer_acc

        # Retention (if available)
        retention_24h = None
        if "retention_24h" in self.results:
            retention_24h = self.calculate_retention(
                post_exposure_acc, self.results["retention_24h"].get("accuracy", 0.0)
            )

        # Sample efficiency
        exposure_tokens = self.config.get("exposure_tokens", 0)
        sample_eff = self.calculate_sample_efficiency(ag, exposure_tokens)

        # Stability-plasticity
        sp_index = None
        if "prior_skills" in self.results and "new_skills" in self.results:
            sp_index = self.stability_plasticity_index(
                self.results["prior_skills"].get("retained", 0.0),
                self.results["new_skills"].get("gained", 0.0),
            )

        # Regret
        online_accs = self.results["exposure"].get("online_accuracies", [])
        regret = self.prequential_regret(online_accs)

        report = {
            "experiment_id": self.experiment_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "config": self.config,
            "metrics": {
                "AG": ag,
                "TS": ts,
                "R_24h": retention_24h,
                "sample_efficiency": sample_eff,
                "stability_plasticity": sp_index,
                "regret": regret,
            },
            "phase_results": {
                "baseline": self.results["baseline"],
                "post_exposure": self.results["post_exposure"],
                "transfer": self.results["transfer"],
            },
        }

        return report

    def save_report(self, output_path: Optional[Path] = None) -> Path:
        """
        Save report to JSON file.

        Args:
            output_path: Path to save report (default: output/kait_report_{id}.json)

        Returns:
            Path where report was saved
        """
        if output_path is None:
            output_dir = Path("output")
            output_dir.mkdir(exist_ok=True)
            output_path = output_dir / f"kait_report_{self.experiment_id}.json"

        report = self.generate_report()

        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)

        return output_path


def run_kait_experiment(
    dsl_name: str,
    agent_model: str,
    baseline_tasks: List[str],
    exposure_episodes: List[str],
    transfer_tasks: List[str],
    exposure_tokens: int,
) -> Dict[str, Any]:
    """
    Run a complete KAIT experiment.

    Args:
        dsl_name: DSL to test
        agent_model: LLM model identifier
        baseline_tasks: Task IDs for baseline evaluation
        exposure_episodes: Learning episodes for exposure phase
        transfer_tasks: Novel tasks for transfer testing
        exposure_tokens: Token budget for exposure

    Returns:
        Full KAIT report
    """
    config = {
        "dsl": dsl_name,
        "agent_model": agent_model,
        "exposure_tokens": exposure_tokens,
        "baseline_tasks": baseline_tasks,
        "transfer_tasks": transfer_tasks,
    }

    evaluator = KAITEvaluator(
        experiment_id=f"{dsl_name}_{agent_model}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
        config=config,
    )

    # NOTE: Actual task execution would happen here
    # For now, this is a framework for running experiments

    print(f"🧪 KAIT Experiment: {dsl_name} with {agent_model}")
    print(f"📊 Baseline tasks: {len(baseline_tasks)}")
    print(f"🎓 Exposure episodes: {len(exposure_episodes)}")
    print(f"🔄 Transfer tasks: {len(transfer_tasks)}")
    print(f"💾 Token budget: {exposure_tokens}")

    # Placeholder results
    evaluator.store_phase_results("baseline", {"accuracy": 0.0})
    evaluator.store_phase_results("post_exposure", {"accuracy": 0.0})
    evaluator.store_phase_results("transfer", {"accuracy": 0.0})
    evaluator.store_phase_results("exposure", {"online_accuracies": []})

    report = evaluator.generate_report()
    report_path = evaluator.save_report()

    print(f"✅ Report saved to {report_path}")

    return report


if __name__ == "__main__":
    # Example usage
    report = run_kait_experiment(
        dsl_name="tinycalc",
        agent_model="claude-sonnet-4",
        baseline_tasks=["001", "002", "003"],
        exposure_episodes=["episode_1", "episode_2"],
        transfer_tasks=["010", "011", "012"],
        exposure_tokens=5000,
    )

    print("\n📈 Metrics Summary:")
    print(f"  AG (Acquisition Gain): {report['metrics']['AG']:.3f}")
    print(f"  TS (Transfer Score): {report['metrics']['TS']:.3f}")
    print(f"  Sample Efficiency: {report['metrics']['sample_efficiency']:.3f}")
