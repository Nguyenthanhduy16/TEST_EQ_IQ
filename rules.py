from __future__ import annotations

from typing import Any, Dict

from scoring import AXES


def generate_flags(scores: Dict[str, float], clusters: Dict[str, float], c2: float) -> Dict[str, bool]:
    flags = {
        'flag_low_commitment': scores['T3'] < 45 or (scores['T3'] < 55 and clusters['commitment'] < 45),
        'flag_high_individualism': scores['T1'] < 45 and scores['T5'] < 50 and scores['R2'] >= 55,
        'flag_image_management': c2 < 45,
        'flag_unclear_profile': False,  # computed later once C4 exists
        'flag_need_deep_interview': False,  # computed later
        'flag_low_social_warmth': scores['T5'] < 45 and scores['T6'] < 45,
        'flag_low_reliability': scores['T3'] < 45 or (scores['T3'] < 55 and clusters['commitment'] < 45),
    }
    return flags


def compute_c4(c1: float, c2: float, flags: Dict[str, bool]) -> float:
    major_flags = [
        flags['flag_high_individualism'],
        flags['flag_image_management'],
        flags['flag_low_reliability'],
    ]
    minor_flags = [
        flags['flag_low_commitment'],
        flags['flag_low_social_warmth'],
    ]
    flags_penalty = 15 * sum(1 for f in major_flags if f) + 8 * sum(1 for f in minor_flags if f)
    c4 = 0.4 * c1 + 0.3 * c2 + 0.3 * (100 - min(flags_penalty, 100))
    return round(max(0.0, min(100.0, c4)), 2)


def finalize_flags(scores: Dict[str, float], c1: float, c4: float, flags: Dict[str, bool]) -> Dict[str, bool]:
    updated = dict(flags)
    top_two = sorted((scores[axis] for axis in AXES), reverse=True)[:2]
    updated['flag_unclear_profile'] = c4 < 45 or c1 < 45 or (top_two[0] < 65 and top_two[1] < 62)
    updated['flag_need_deep_interview'] = (
        updated['flag_high_individualism']
        or updated['flag_image_management']
        or updated['flag_low_reliability']
        or scores['R1'] >= 60
        or scores['R2'] >= 60
        or c4 < 55
    )
    return updated


def fit_level(mini_test_score: float, scores: Dict[str, float], c4: float, flags: Dict[str, bool]) -> str:
    major_count = sum(1 for key in ['flag_high_individualism', 'flag_image_management', 'flag_low_reliability'] if flags[key])
    if (
        mini_test_score >= 78
        and scores['T1'] >= 60
        and scores['T3'] >= 60
        and scores['T5'] >= 60
        and scores['R1'] < 45
        and scores['R2'] < 45
        and c4 >= 60
    ):
        return 'Rất phù hợp'
    if mini_test_score >= 66 and scores['R1'] < 55 and scores['R2'] < 55 and major_count <= 1:
        return 'Phù hợp'
    if mini_test_score >= 45 and (scores['R1'] >= 55 or scores['R2'] >= 55 or flags['flag_image_management'] or sum(flags.values()) >= 2):
        return 'Rủi ro cao, cần phỏng vấn sâu'
    if mini_test_score < 45 or (scores['T3'] < 40 and scores['T1'] < 40 and scores['T5'] < 45):
        return 'Chưa phù hợp hiện tại'
    return 'Tạm phù hợp, cần kiểm chứng'


def candidate_profile(scores: Dict[str, float]) -> str:
    if scores['T1'] >= 65 and scores['T3'] >= 65 and scores['T5'] >= 65 and scores['R1'] < 40 and scores['R2'] < 40:
        return 'Đồng hành bền vững'
    if scores['T2'] >= 70 and scores['T3'] >= 65 and scores['T7'] >= 70 and scores['T4'] >= 50:
        return 'Hạt giống nòng cốt'
    if scores['T5'] >= 70 and scores['T6'] >= 70 and scores['T3'] < 60:
        return 'Ấm áp, dễ hòa nhập'
    if scores['T7'] >= 75 and (scores['T1'] < 55 or scores['T8'] < 55 or scores['R2'] >= 50):
        return 'Phát triển mạnh nhưng cần giữ nhịp tập thể'
    if scores['T5'] >= 60 and scores['T3'] < 55:
        return 'Tử tế nhưng độ bền cam kết chưa chắc'
    if scores['R2'] >= 65 and scores['T1'] < 50:
        return 'Khó đồng hành dài hạn'
    return 'Cân bằng, cần xác minh thêm'


def confidence_level(c4: float) -> str:
    if c4 >= 75:
        return 'Cao'
    if c4 >= 55:
        return 'Vừa'
    return 'Thấp'


def interview_priority(fit: str, c4: float, profile: str, flags: Dict[str, bool]) -> str:
    if fit == 'Rất phù hợp' or (fit == 'Phù hợp' and c4 >= 70 and not (flags['flag_high_individualism'] or flags['flag_image_management'] or flags['flag_low_reliability'])):
        return 'Ưu tiên tuyển'
    if flags['flag_need_deep_interview'] or profile in {
        'Phát triển mạnh nhưng cần giữ nhịp tập thể',
        'Tử tế nhưng độ bền cam kết chưa chắc',
        'Khó đồng hành dài hạn',
    } or flags['flag_image_management']:
        return 'Ưu tiên kiểm chứng'
    if fit == 'Chưa phù hợp hiện tại':
        return 'Không ưu tiên'
    return 'Phỏng vấn thường'


def evaluate(result: Dict[str, Any]) -> Dict[str, Any]:
    scores = result['scores']
    clusters = result['cluster_consistency']
    flags = generate_flags(scores, clusters, result['C2'])
    c4 = compute_c4(result['C1'], result['C2'], flags)
    flags = finalize_flags(scores, result['C1'], c4, flags)
    fit = fit_level(result['mini_test_score'], scores, c4, flags)
    profile = candidate_profile(scores)
    confidence = confidence_level(c4)
    priority = interview_priority(fit, c4, profile, flags)
    return {
        'C4': c4,
        'flags': flags,
        'fit_level': fit,
        'candidate_profile': profile,
        'confidence_level': confidence,
        'interview_priority': priority,
    }
