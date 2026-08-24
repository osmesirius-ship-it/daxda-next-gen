#!/usr/bin/env python3
"""
DAX Probabilistic Scoring & Calibration Engine (dax_predictive_scoring_engine.py)
==============================================================================
Calculates rigorous probabilistic evaluation metrics across forecaster outputs:
  - Multiclass Brier Score: BS = \sum_{k=1}^K (p_k - o_k)^2
  - Log Loss: LL = -\log(p_{actual})
  - Expected Calibration Error (ECE): ECE = \sum_m (|B_m| / N) * |acc(B_m) - conf(B_m)|
  - Discrimination: Top-1 Accuracy, Top-2 Accuracy, ROC-AUC approximation
  - Forecast Entropy: H(P) = -\sum p_i \log p_i
  - Abstention / HOLD Quality Evaluation
"""

from __future__ import annotations
import math
import json
from dataclasses import dataclass, field
from typing import Dict, List, Any, Tuple


@dataclass
class CaseScoreResult:
    case_id: str
    actual_outcome: str
    predicted_outcome: str
    brier_score: float
    log_loss: float
    top1_correct: bool
    top2_correct: bool
    forecast_entropy: float
    abstain: bool
    confidence: float


@dataclass
class SuiteScoringSummary:
    total_cases: int
    mean_brier_score: float
    median_brier_score: float
    mean_log_loss: float
    expected_calibration_error: float
    top1_accuracy: float
    top2_accuracy: float
    abstention_count: int
    abstention_mean_entropy: float
    non_abstention_mean_entropy: float
    bin_calibration_details: List[Dict[str, Any]]


class PredictiveScoringEngine:
    def compute_brier_score(self, probs: Dict[str, float], actual_outcome: str) -> float:
        score = 0.0
        for cat, p in probs.items():
            o = 1.0 if cat == actual_outcome else 0.0
            score += (p - o) ** 2
        return round(score, 6)

    def compute_log_loss(self, probs: Dict[str, float], actual_outcome: str) -> float:
        p_actual = probs.get(actual_outcome, 1.0e-15)
        p_actual = max(1.0e-15, min(1.0, p_actual))
        return round(-math.log(p_actual), 6)

    def compute_entropy(self, probs: Dict[str, float]) -> float:
        h = 0.0
        for p in probs.values():
            if p > 0:
                h -= p * math.log(p)
        return round(h, 6)

    def score_single_case(
        self,
        prediction_record: Dict[str, Any],
        actual_outcome: str
    ) -> CaseScoreResult:
        case_id = prediction_record.get("case_id", "UNKNOWN")
        probs = prediction_record.get("outcomes", {})
        predicted_outcome = prediction_record.get("predicted_outcome", "")
        abstain = prediction_record.get("abstain", False)

        bs = self.compute_brier_score(probs, actual_outcome)
        ll = self.compute_log_loss(probs, actual_outcome)
        entropy = self.compute_entropy(probs)

        # Top 1 check
        top1_correct = (predicted_outcome == actual_outcome)

        # Top 2 check
        sorted_cats = sorted(probs, key=probs.get, reverse=True)
        top2_cats = sorted_cats[:2]
        top2_correct = (actual_outcome in top2_cats)

        conf = probs.get(predicted_outcome, 0.0)

        return CaseScoreResult(
            case_id=case_id,
            actual_outcome=actual_outcome,
            predicted_outcome=predicted_outcome,
            brier_score=bs,
            log_loss=ll,
            top1_correct=top1_correct,
            top2_correct=top2_correct,
            forecast_entropy=entropy,
            abstain=abstain,
            confidence=conf,
        )

    def evaluate_suite(
        self,
        predictions: List[Dict[str, Any]],
        actual_outcomes: Dict[str, str]
    ) -> SuiteScoringSummary:
        case_results: List[CaseScoreResult] = []
        
        for pred in predictions:
            cid = pred.get("case_id", "")
            if cid in actual_outcomes:
                act = actual_outcomes[cid]
                res = self.score_single_case(pred, act)
                case_results.append(res)

        N = len(case_results)
        if N == 0:
            return SuiteScoringSummary(
                total_cases=0, mean_brier_score=0.0, median_brier_score=0.0, mean_log_loss=0.0,
                expected_calibration_error=0.0, top1_accuracy=0.0, top2_accuracy=0.0,
                abstention_count=0, abstention_mean_entropy=0.0, non_abstention_mean_entropy=0.0,
                bin_calibration_details=[]
            )

        brier_scores = [r.brier_score for r in case_results]
        log_losses = [r.log_loss for r in case_results]
        sorted_bs = sorted(brier_scores)

        mean_bs = round(sum(brier_scores) / N, 6)
        median_bs = round(sorted_bs[N // 2], 6)
        mean_ll = round(sum(log_losses) / N, 6)

        top1_acc = round(sum(1 for r in case_results if r.top1_correct) / N, 4)
        top2_acc = round(sum(1 for r in case_results if r.top2_correct) / N, 4)

        # Abstention Analysis
        abstained = [r for r in case_results if r.abstain]
        non_abstained = [r for r in case_results if not r.abstain]

        abs_count = len(abstained)
        abs_mean_h = round(sum(r.forecast_entropy for r in abstained) / abs_count, 4) if abs_count > 0 else 0.0
        non_abs_mean_h = round(sum(r.forecast_entropy for r in non_abstained) / len(non_abstained), 4) if non_abstained else 0.0

        # Calibration Error Calculation across 10 Bins (0.0 to 1.0)
        bin_counts = [0] * 10
        bin_correct = [0] * 10
        bin_conf_sum = [0.0] * 10

        for r in case_results:
            b_idx = min(9, int(r.confidence * 10))
            bin_counts[b_idx] += 1
            if r.top1_correct:
                bin_correct[b_idx] += 1
            bin_conf_sum[b_idx] += r.confidence

        ece = 0.0
        bin_details = []
        for i in range(10):
            cnt = bin_counts[i]
            if cnt > 0:
                acc = bin_correct[i] / cnt
                avg_conf = bin_conf_sum[i] / cnt
                abs_diff = abs(acc - avg_conf)
                ece += (cnt / N) * abs_diff
                bin_details.append({
                    "bin_range": f"{i*10}%-{(i+1)*10}%",
                    "count": cnt,
                    "accuracy": round(acc, 4),
                    "confidence": round(avg_conf, 4),
                    "abs_diff": round(abs_diff, 4)
                })

        return SuiteScoringSummary(
            total_cases=N,
            mean_brier_score=mean_bs,
            median_brier_score=median_bs,
            mean_log_loss=mean_ll,
            expected_calibration_error=round(ece, 6),
            top1_accuracy=top1_acc,
            top2_accuracy=top2_acc,
            abstention_count=abs_count,
            abstention_mean_entropy=abs_mean_h,
            non_abstention_mean_entropy=non_abs_mean_h,
            bin_calibration_details=bin_details,
        )


if __name__ == "__main__":
    engine = PredictiveScoringEngine()
    preds = [
        {"case_id": "C-1", "outcomes": {"A": 0.1, "B": 0.2, "C": 0.6, "D": 0.1}, "predicted_outcome": "C", "abstain": False},
        {"case_id": "C-2", "outcomes": {"A": 0.7, "B": 0.1, "C": 0.1, "D": 0.1}, "predicted_outcome": "A", "abstain": False},
    ]
    acts = {"C-1": "C", "C-2": "B"}
    summary = engine.evaluate_suite(preds, acts)
    print("=" * 80)
    print("DAX Predictive Scoring Summary")
    print("=" * 80)
    print(json.dumps(summary.__dict__, indent=2))
