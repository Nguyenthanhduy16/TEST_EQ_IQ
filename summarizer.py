from __future__ import annotations

from typing import Dict, List

AXIS_LABELS = {
    'T1': 'có xu hướng gắn bó và thấy giá trị trong nhịp chung',
    'T2': 'có phản xạ chủ động và không quá phụ thuộc vào phân công',
    'T3': 'có tín hiệu giữ lời và giữ nhịp tương đối tốt',
    'T4': 'khá mở với góp ý và có xu hướng tự xem lại mình',
    'T5': 'có sự chú ý tới người khác và xu hướng hỗ trợ tương đối tự nhiên',
    'T6': 'khá dễ bắt nhịp và sống cùng người khác',
    'T7': 'có động lực phát triển dài hạn tương đối rõ',
    'T8': 'có xu hướng cân bằng giữa nhịp cá nhân và nhịp chung',
}

RISK_LABELS = {
    'T3': 'Độ bền cam kết và khả năng giữ nhịp dài chưa chắc.',
    'T1': 'Cảm giác thuộc về tập thể chưa thật rõ.',
    'T5': 'Độ nhạy với người khác chưa nổi bật.',
    'T6': 'Có thể cần thêm thời gian để hòa nhịp với môi trường mới.',
    'R1': 'Cần kiểm tra xem động lực tham gia có quá thiên về lợi ích ngắn hạn hay không.',
    'R2': 'Cần làm rõ khả năng đồng hành khi nhịp cá nhân thay đổi.',
}


def quick_summary(scores: Dict[str, float], flags: Dict[str, bool]) -> str:
    lines = []
    if scores['T1'] >= 65 and scores['T5'] >= 65 and scores['T6'] >= 60:
        lines.append('Ứng viên có xu hướng hòa nhịp tốt với môi trường người-người, khá chú ý tới người khác và dễ sống trong tập thể gắn kết.')
    elif scores['T7'] >= 70:
        lines.append('Ứng viên có động lực phát triển bản thân khá rõ, có xu hướng học thêm và đi đường dài.')
    else:
        lines.append('Hồ sơ cho thấy ứng viên có một số tín hiệu phù hợp nhưng cần nhìn trong ngữ cảnh thực tế hơn là chỉ dựa vào điểm tổng.')

    if scores['T3'] < 55:
        lines.append('Độ đều nhịp và khả năng giữ cam kết khi lịch cá nhân tăng tải chưa thật nổi bật.')
    elif scores['T3'] >= 65:
        lines.append('Khả năng giữ lời và giữ nhịp tương đối tốt là một điểm cộng rõ.')

    if scores['R2'] >= 55 or scores['T1'] < 50:
        lines.append('Cần kiểm tra thêm điều gì thật sự khiến ứng viên muốn ở lại với một tập thể trong thời gian dài.')
    elif flags.get('flag_image_management'):
        lines.append('Nên kiểm tra bằng ví dụ thật vì mẫu trả lời có xu hướng hơi đẹp và tròn.')
    return ' '.join(lines[:3])


def top_strengths(scores: Dict[str, float]) -> List[str]:
    top_axes = sorted([a for a in scores if a.startswith('T')], key=lambda a: scores[a], reverse=True)[:3]
    return [AXIS_LABELS[a] for a in top_axes]


def top_risks(scores: Dict[str, float]) -> List[str]:
    items = []
    low_axes = sorted(['T1', 'T3', 'T5', 'T6'], key=lambda a: scores[a])[:2]
    for axis in low_axes:
        items.append(RISK_LABELS[axis])
    if scores['R1'] >= 55:
        items.append(RISK_LABELS['R1'])
    if scores['R2'] >= 55:
        items.append(RISK_LABELS['R2'])
    deduped = []
    for item in items:
        if item not in deduped:
            deduped.append(item)
    return deduped[:3]


def interview_focus(scores: Dict[str, float], flags: Dict[str, bool]) -> str:
    if flags.get('flag_image_management'):
        return 'Cần hỏi bằng ví dụ thật và tình huống cụ thể để kiểm tra độ chân thực của câu trả lời.'
    if scores['T3'] < 55:
        return 'Tập trung kiểm tra cách ứng viên giữ lời, giữ nhịp và xử lý khi không còn hứng thú như ban đầu.'
    if scores['R2'] >= 55:
        return 'Tập trung làm rõ điều gì khiến ứng viên thật sự muốn gắn bó lâu với một tập thể.'
    if scores['R1'] >= 55:
        return 'Cần kiểm tra động lực tham gia và cách ứng viên nhìn nhận giá trị chung so với lợi ích trực tiếp.'
    if scores['T5'] >= 65 and scores['T2'] < 50:
        return 'Cần phân biệt xem ứng viên thiên về hỗ trợ phía sau hay có khả năng tự vào việc khi chưa ai gọi tên.'
    return 'Nên dùng phỏng vấn để xác minh thêm độ bền cam kết, động lực tham gia và cách ứng viên vận hành trong tình huống thật.'


def suggested_questions(scores: Dict[str, float], flags: Dict[str, bool]) -> List[str]:
    qs = []
    if scores['T3'] < 55:
        qs.extend([
            'Kể một lần bạn đã nhận lời một việc hoặc một lời hẹn rồi sau đó không còn hứng như ban đầu, bạn xử lý thế nào?',
            'Khi lịch cá nhân dày lên, bạn giữ những cam kết đã có bằng cách nào?',
        ])
    if scores['R2'] >= 55 or scores['T1'] < 50:
        qs.extend([
            'Trong một nhóm người hay một cộng đồng, điều gì thật sự khiến bạn muốn ở lại lâu?',
            'Có trải nghiệm nào trước đây khiến bạn thấy mình hợp hoặc không hợp với một tập thể không?',
        ])
    if scores['R1'] >= 55:
        qs.extend([
            'Nếu một môi trường không cho bạn lợi ích rõ ngay, điều gì vẫn có thể khiến bạn tiếp tục đồng hành?',
            'Bạn thường cân nhắc điều gì giữa việc có ích cho mình và việc có ích cho tập thể?',
        ])
    if scores['T5'] < 50 or scores['T6'] < 50:
        qs.extend([
            'Khi thấy một người chậm nhịp hoặc hơi đứng ngoài, bạn thường phản ứng thực tế thế nào?',
            'Bạn thấy mình hợp hơn với việc chủ động kết nối hay chờ đúng ngữ cảnh mới mở lời?',
        ])
    if flags.get('flag_image_management'):
        qs.extend([
            'Kể một lần gần đây bạn đã cư xử chưa khéo hoặc không giữ được điều mình định giữ.',
            'Kể một tình huống bạn đã chọn ưu tiên bản thân hơn một việc chung, và vì sao.',
        ])
    if not qs:
        qs.extend([
            'Điều gì ở một môi trường chung khiến bạn muốn gắn bó lâu hơn mức bình thường?',
            'Bạn đã từng giữ một cam kết kéo dài nào tốt chưa? Vì sao lần đó bạn làm được?',
            'Khi có bất đồng nhỏ với người khác, bạn thường xử lý ra sao?',
        ])
    deduped = []
    for q in qs:
        if q not in deduped:
            deduped.append(q)
    return deduped[:4]
