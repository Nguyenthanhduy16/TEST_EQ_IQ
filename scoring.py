from __future__ import annotations

from statistics import pstdev
from typing import Any, Dict, List

AXES = ['T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8']
RISK_AXES = ['R1', 'R2']
ALL_AXES = AXES + RISK_AXES

SCORING_MAP: Dict[str, Dict[str, Dict[str, float]]] = {
    'Q01': {'A': {'T3': 1.5, 'T8': 0.5}, 'B': {'T8': 0.5, 'R2': 0.5}},
    'Q02': {'A': {'T4': 1.0, 'T3': 0.5}, 'B': {'T3': 0.5, 'T4': 0.5}},
    'Q03': {'A': {'T2': 1.0, 'T5': 0.5}, 'B': {'T4': 0.5}},
    'Q04': {'A': {'T4': 1.5}, 'B': {'T4': 0.5, 'R2': 0.5}},
    'Q05': {'A': {'T4': 1.0, 'T1': 0.5}, 'B': {'T7': 0.5, 'R1': 0.5}},
    'Q06': {'A': {'T5': 1.0, 'T6': 0.5}, 'B': {'T3': 0.5}},
    'Q07': {'A': {'T3': 1.5, 'T8': 0.5}, 'B': {'T8': 0.5}},
    'Q08': {'A': {'T5': 1.0, 'T2': 0.5}, 'B': {'T4': 0.5}},
    'Q09': {'A': {'T6': 1.0, 'T1': 0.5}, 'B': {'T6': 0.5}},
    'Q10': {'A': {'T5': 1.0, 'T8': 0.5}, 'B': {'R1': 0.5}},
    'Q11': {'A': {'T7': 1.0, 'T2': 0.5}, 'B': {'T3': 0.5}},
    'Q12': {'A': {'T5': 1.0, 'T6': 0.5}, 'B': {'T3': 0.5}},
    'Q13': {'A': {'T4': 0.5, 'T7': 1.0}, 'B': {'T7': 0.5}},
    'Q14': {'A': {'T5': 1.0, 'T6': 0.5}, 'B': {'T8': 0.5}},
    'Q15': {'A': {'T5': 1.0, 'T6': 0.5}, 'B': {'T8': 0.5}},
    'Q16': {'A': {'T5': 1.0, 'T1': 0.5}, 'B': {'R1': 1.0}},
    'Q17': {'A': {'T2': 1.0, 'T3': 0.5}, 'B': {'T3': 0.5}},
    'Q18': {'A': {'T4': 1.0, 'T3': 0.5, 'T6': 0.5}, 'B': {'T8': 0.5}},
    'Q19': {'A': {'T7': 1.5}, 'B': {'T8': 0.5}},
    'Q20': {'A': {'T3': 1.0, 'T7': 0.5}, 'B': {'T8': 0.5, 'R2': 0.5}},
    'Q21': {'A': {'T1': 1.0, 'T8': 0.5}, 'B': {'R2': 1.0}},
    'Q22': {'A': {'T5': 0.5, 'T1': 0.5, 'T8': 0.5}, 'B': {'R1': 1.0}},
    'Q23': {'A': {'T5': 1.0, 'T6': 0.5}, 'B': {'T7': 1.0, 'T4': 0.5}},
    'Q24': {'A': {'T4': 1.0, 'T7': 0.5}, 'B': {'T8': 0.5}},
    'Q25': {'A': {'T3': 1.0, 'T8': 0.5}, 'B': {'T8': 0.5}},
    'Q26': {'A': {'T3': 0.5, 'T2': 0.5}, 'B': {'T8': 0.5}, 'C': {'T1': 0.5, 'T6': 0.5, 'T5': 0.5}},
    'Q27': {'A': {'T3': 1.0}, 'B': {'T3': 0.5, 'T2': 0.5}, 'C': {'T8': 0.5}},
    'Q28': {'A': {'T5': 1.0, 'T6': 0.5, 'T4': 0.5}, 'B': {'T8': 0.5}, 'C': {'T3': 0.5, 'R2': 0.5}},
    'Q29': {'A': {'T3': 1.0}, 'B': {'T3': 0.5, 'T7': 0.5}, 'C': {'T7': 0.5, 'R2': 0.5}},
    'Q30': {'A': {'T4': 1.0, 'T7': 0.5}, 'B': {'T4': 0.5, 'T7': 0.5}, 'C': {}},
    'Q31': {'A': {'T5': 1.0, 'T6': 0.5}, 'B': {'T3': 0.5}, 'C': {'T4': 0.5, 'T5': 0.5}},
    'Q32': {'A': {'T6': 1.0}, 'B': {'T1': 0.5, 'T5': 0.5}, 'C': {'T6': 0.5, 'T8': 0.5}},
    'Q33': {'A': {'T7': 0.5, 'T3': 0.5}, 'B': {'T8': 0.5}, 'C': {'T7': 1.0, 'T2': 0.5, 'R2': 0.5}},
    'Q34': {'A': {'T6': 0.5, 'T4': 0.5}, 'B': {'T6': 1.0, 'T1': 0.5}, 'C': {'T6': 0.5}},
    'Q35': {'A': {'T3': 0.5}, 'B': {'T7': 0.5, 'T8': 0.5}, 'C': {'T8': 1.0}},
    'Q36': {'A': {'T3': 1.0}, 'B': {}, 'C': {'T3': 0.5}},
    'Q37': {'A': {'T7': 0.5, 'T3': 0.5}, 'B': {'T7': 1.0}, 'C': {'T7': 0.5, 'T8': 0.5}},
    'Q38': {'A': {'T5': 0.5, 'T6': 0.5}, 'B': {'R2': 0.5}, 'C': {'T4': 0.5, 'T6': 0.5}},
    'Q39': {'A': {'T7': 1.0, 'T3': 0.5}, 'B': {'T3': 0.5}, 'C': {'T8': 0.5, 'R2': 0.5}},
    'Q40': {'A': {'T3': 1.0, 'T5': 0.5}, 'B': {'T3': 0.5}, 'C': {'T8': 0.5}},
    'Q41': {'A': {'T3': 1.0, 'T2': 0.5}, 'B': {'T8': 1.0, 'T3': 0.5}, 'C': {'T8': 0.5}, 'D': {}},
    'Q42': {'A': {'T2': 1.0}, 'B': {'T2': 0.5, 'T3': 0.5}, 'C': {'T3': 1.0}, 'D': {'T3': 0.5}},
    'Q43': {'A': {'T2': 0.5, 'T5': 0.5}, 'B': {'T3': 1.0}, 'C': {'T7': 1.0}, 'D': {'T8': 1.0}},
    'Q44': {'A': {'T7': 1.0, 'T2': 0.5}, 'B': {'T5': 0.5, 'T1': 0.5}, 'C': {'T3': 0.5, 'T7': 0.5}, 'D': {'T4': 0.5, 'T7': 0.5}},
    'Q45': {'A': {'T4': 1.0, 'T3': 0.5}, 'B': {'T5': 1.0, 'T6': 0.5}, 'C': {'T3': 0.5}, 'D': {'T4': 0.5, 'T6': 0.5}},
    'Q46': {'A': {'T1': 1.5}, 'B': {'T1': 1.0, 'T6': 0.5}, 'C': {'T7': 1.0, 'R2': 0.5}, 'D': {'T5': 1.0, 'T1': 0.5}},
    'Q47': {'A': {'T5': 1.0, 'T4': 0.5}, 'B': {'T5': 0.5}, 'C': {'R1': 0.5}, 'D': {'T4': 0.5, 'T6': 0.5}},
    'Q48': {'A': {'T7': 0.5, 'T3': 0.5}, 'B': {'T2': 0.5}, 'C': {'T4': 0.5, 'T7': 0.5}, 'D': {'T2': 1.0, 'T7': 0.5}},
    'Q49': {'A': {'T5': 1.0, 'T6': 0.5}, 'B': {'T5': 1.0, 'T7': 0.5}, 'C': {'T2': 0.5, 'T5': 0.5}, 'D': {'T8': 0.5}},
    'Q50': {'A': {'T3': 1.5}, 'B': {'T1': 0.5, 'T5': 0.5, 'T8': 0.5}, 'C': {'T7': 1.0, 'T8': 0.5, 'R2': 0.5}, 'D': {'T8': 1.0}},
}

WEIGHTS = {'T1': 10, 'T2': 10, 'T3': 12, 'T4': 8, 'T5': 12, 'T6': 8, 'T7': 10, 'T8': 15}
RISK_WEIGHTS = {'R1': 7, 'R2': 8}

CONSISTENCY_GROUPS = {
    'commitment': {'axis': 'T3', 'questions': ['Q01', 'Q07', 'Q20', 'Q25', 'Q29', 'Q36', 'Q41', 'Q50']},
    'warmth': {'axis': 'T5', 'questions': ['Q06', 'Q12', 'Q14', 'Q15', 'Q31', 'Q38', 'Q47', 'Q49']},
    'belonging': {'axis': 'T1', 'questions': ['Q09', 'Q21', 'Q32', 'Q34', 'Q46']},
    'initiative': {'axis': 'T2', 'questions': ['Q03', 'Q08', 'Q17', 'Q26', 'Q42', 'Q48']},
    'humility': {'axis': 'T4', 'questions': ['Q02', 'Q04', 'Q18', 'Q24', 'Q28', 'Q30', 'Q45']},
    'growth': {'axis': 'T7', 'questions': ['Q11', 'Q13', 'Q19', 'Q33', 'Q37', 'Q39', 'Q44', 'Q48']},
}

DESIRABLE_SET = {
    'Q01A', 'Q03A', 'Q06A', 'Q10A', 'Q14A', 'Q15A', 'Q16A', 'Q20A', 'Q24A',
    'Q28A', 'Q31A', 'Q40A', 'Q42A', 'Q45B', 'Q46D', 'Q47A', 'Q49B', 'Q50A'
}

# Precomputed maxima for normalization.
MAX_AXIS_SCORES: Dict[str, float] = {axis: 0.0 for axis in ALL_AXES}
for qid, options in SCORING_MAP.items():
    for axis in ALL_AXES:
        MAX_AXIS_SCORES[axis] += max(option_scores.get(axis, 0.0) for option_scores in options.values())


def normalize(value: float, maximum: float) -> float:
    if maximum <= 0:
        return 0.0
    return max(0.0, min(100.0, round(100.0 * value / maximum, 2)))


def _cluster_consistency(answers: Dict[str, str], axis: str, questions: List[str]) -> float:
    values = []
    for qid in questions:
        option = answers.get(qid)
        if not option:
            continue
        option_scores = SCORING_MAP.get(qid, {}).get(option, {})
        max_for_axis = max((opt.get(axis, 0.0) for opt in SCORING_MAP.get(qid, {}).values()), default=0.0)
        value = 0.0 if max_for_axis == 0 else option_scores.get(axis, 0.0) / max_for_axis
        values.append(value)
    if len(values) <= 1:
        return 100.0
    std = pstdev(values)
    return round(100.0 * (1 - min(std / 0.5, 1)), 2)


def calculate_scores(answers: Dict[str, str]) -> Dict[str, Any]:
    raw = {axis: 0.0 for axis in ALL_AXES}
    desirable_count = 0

    for qid, option in answers.items():
        option_scores = SCORING_MAP.get(qid, {}).get(option, {})
        for axis, value in option_scores.items():
            raw[axis] += value
        if f'{qid}{option}' in DESIRABLE_SET:
            desirable_count += 1

    normalized = {axis: normalize(raw[axis], MAX_AXIS_SCORES[axis]) for axis in ALL_AXES}

    # Consistency per cluster
    cluster_scores = {}
    for name, meta in CONSISTENCY_GROUPS.items():
        cluster_scores[name] = _cluster_consistency(answers, meta['axis'], meta['questions'])
    c1 = round(sum(cluster_scores.values()) / len(cluster_scores), 2)

    desirable_rate = desirable_count / len(DESIRABLE_SET)
    axis_values = [normalized[axis] for axis in AXES]
    mean_axes = sum(axis_values) / len(axis_values)
    positive_variance = sum((value - mean_axes) ** 2 for value in axis_values) / len(axis_values)
    positive_variance = round(positive_variance, 2)

    c2 = 100.0 - 60.0 * max(0.0, desirable_rate - 0.65)
    if positive_variance < 80 and desirable_rate > 0.75:
        c2 -= 20.0
    c2 = max(0.0, min(100.0, round(c2, 2)))

    c3 = round(2 * (sum(abs(normalized[axis] - 50) for axis in AXES) / len(AXES)), 2)

    base_fit = round(sum(WEIGHTS[axis] * normalized[axis] for axis in AXES) / sum(WEIGHTS.values()), 2)
    risk_penalty = round(sum(RISK_WEIGHTS[axis] * normalized[axis] for axis in RISK_AXES) / 100.0, 2)
    consistency_penalty = 0.0 if c1 >= 50 else round((50 - c1) * 0.15, 2)
    naturalness_penalty = 0.0 if c2 >= 45 else round((45 - c2) * 0.10, 2)
    mini_test_score = max(0.0, min(100.0, round(base_fit - risk_penalty - consistency_penalty - naturalness_penalty, 2)))

    return {
        'raw': raw,
        'scores': normalized,
        'cluster_consistency': cluster_scores,
        'desirable_rate': round(desirable_rate, 4),
        'positive_variance': positive_variance,
        'C1': c1,
        'C2': c2,
        'C3': c3,
        'base_fit': base_fit,
        'risk_penalty': risk_penalty,
        'consistency_penalty': consistency_penalty,
        'naturalness_penalty': naturalness_penalty,
        'mini_test_score': mini_test_score,
    }
