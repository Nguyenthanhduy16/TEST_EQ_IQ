from __future__ import annotations

import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from flask import Flask, flash, g, redirect, render_template, request, session, url_for, Response

from question_data import QUESTIONS, DIMENSIONS
from scoring import calculate_scores
from rules import evaluate
from summarizer import interview_focus, quick_summary, suggested_questions, top_risks, top_strengths

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.environ.get('DB_PATH', str(BASE_DIR / 'data.sqlite3')))
SECRET_KEY = os.environ.get('SECRET_KEY', 'change-me-dev-secret')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY


def get_db() -> sqlite3.Connection:
    if 'db' not in g:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        g.db = conn
    return g.db


@app.teardown_appcontext
def close_db(error: Exception | None) -> None:
    conn = g.pop('db', None)
    if conn is not None:
        conn.close()


def init_db() -> None:
    db = get_db()
    db.execute(
        '''
        CREATE TABLE IF NOT EXISTS submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            candidate_name TEXT NOT NULL,
            student_id TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            department TEXT NOT NULL,
            answers_json TEXT NOT NULL,
            result_json TEXT NOT NULL,
            reviewer_note TEXT DEFAULT '',
            review_status TEXT DEFAULT 'Chưa xem',
            final_interview_decision TEXT DEFAULT ''
        )
        '''
    )
    db.commit()


with app.app_context():
    init_db()


def serialize_result(answers: Dict[str, str]) -> Dict[str, Any]:
    score_result = calculate_scores(answers)
    eval_result = evaluate(score_result)
    strengths = top_strengths(score_result['scores'])
    risks = top_risks(score_result['scores'])
    focus = interview_focus(score_result['scores'], eval_result['flags'])
    questions = suggested_questions(score_result['scores'], eval_result['flags'])
    result = {
        **score_result,
        **eval_result,
        'quick_summary': quick_summary(score_result['scores'], eval_result['flags']),
        'top_strengths': strengths,
        'top_risks': risks,
        'interview_focus': focus,
        'suggested_questions': questions,
    }
    return result


def require_admin() -> bool:
    return bool(session.get('is_admin'))


@app.route('/')
def index():
    db = get_db()
    total = db.execute('SELECT COUNT(*) AS c FROM submissions').fetchone()['c']
    return render_template('index.html', total=total)


@app.route('/apply', methods=['GET', 'POST'])
def apply():
    if request.method == 'POST':
        form = request.form
        candidate_name = form.get('candidate_name', '').strip()
        student_id = form.get('student_id', '').strip()
        email = form.get('email', '').strip()
        phone = form.get('phone', '').strip()
        department = form.get('department', '').strip()

        missing_info = [label for label, value in {
            'Họ và tên': candidate_name,
            'MSSV': student_id,
            'Email': email,
            'Số điện thoại': phone,
            'Viện/Ngành hoặc Lớp': department,
        }.items() if not value]

        answers: Dict[str, str] = {}
        missing_questions = []
        for q in QUESTIONS:
            value = form.get(q['id'], '').strip()
            if not value:
                missing_questions.append(q['id'])
            else:
                answers[q['id']] = value

        if missing_info or missing_questions:
            if missing_info:
                flash('Thiếu thông tin: ' + ', '.join(missing_info), 'error')
            if missing_questions:
                flash('Thiếu câu trả lời: ' + ', '.join(missing_questions[:8]) + ('...' if len(missing_questions) > 8 else ''), 'error')
            return render_template('apply.html', questions=QUESTIONS, values=form)

        result = serialize_result(answers)
        db = get_db()
        db.execute(
            '''
            INSERT INTO submissions (
                created_at, candidate_name, student_id, email, phone, department,
                answers_json, result_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''',
            (
                datetime.now().isoformat(timespec='seconds'),
                candidate_name,
                student_id,
                email,
                phone,
                department,
                json.dumps(answers, ensure_ascii=False),
                json.dumps(result, ensure_ascii=False),
            )
        )
        db.commit()
        return render_template('submit_success.html')

    return render_template('apply.html', questions=QUESTIONS, values={})


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password', '')
        if password == ADMIN_PASSWORD:
            session['is_admin'] = True
            return redirect(url_for('admin_dashboard'))
        flash('Sai mật khẩu quản trị.', 'error')
    return render_template('login.html')


@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/admin')
def admin_dashboard():
    if not require_admin():
        return redirect(url_for('admin_login'))

    fit = request.args.get('fit', '').strip()
    priority = request.args.get('priority', '').strip()
    q = request.args.get('q', '').strip()

    sql = 'SELECT * FROM submissions'
    conditions = []
    params = []
    if fit:
        conditions.append("json_extract(result_json, '$.fit_level') = ?")
        params.append(fit)
    if priority:
        conditions.append("json_extract(result_json, '$.interview_priority') = ?")
        params.append(priority)
    if q:
        conditions.append('(candidate_name LIKE ? OR student_id LIKE ? OR email LIKE ?)')
        params.extend([f'%{q}%', f'%{q}%', f'%{q}%'])
    if conditions:
        sql += ' WHERE ' + ' AND '.join(conditions)
    sql += " ORDER BY json_extract(result_json, '$.mini_test_score') DESC, id DESC"

    rows = get_db().execute(sql, params).fetchall()
    candidates = []
    for row in rows:
        result = json.loads(row['result_json'])
        candidates.append({
            'id': row['id'],
            'created_at': row['created_at'],
            'candidate_name': row['candidate_name'],
            'student_id': row['student_id'],
            'email': row['email'],
            'department': row['department'],
            'review_status': row['review_status'],
            'fit_level': result['fit_level'],
            'interview_priority': result['interview_priority'],
            'candidate_profile': result['candidate_profile'],
            'mini_test_score': result['mini_test_score'],
            'confidence_level': result['confidence_level'],
            'quick_summary': result['quick_summary'],
        })
    return render_template('admin_dashboard.html', candidates=candidates, fit=fit, priority=priority, q=q)


@app.route('/admin/candidate/<int:candidate_id>', methods=['GET', 'POST'])
def admin_candidate(candidate_id: int):
    if not require_admin():
        return redirect(url_for('admin_login'))
    db = get_db()
    row = db.execute('SELECT * FROM submissions WHERE id = ?', (candidate_id,)).fetchone()
    if row is None:
        return 'Không tìm thấy ứng viên', 404

    if request.method == 'POST':
        reviewer_note = request.form.get('reviewer_note', '').strip()
        review_status = request.form.get('review_status', 'Chưa xem').strip()
        final_interview_decision = request.form.get('final_interview_decision', '').strip()
        db.execute(
            'UPDATE submissions SET reviewer_note = ?, review_status = ?, final_interview_decision = ? WHERE id = ?',
            (reviewer_note, review_status, final_interview_decision, candidate_id)
        )
        db.commit()
        flash('Đã lưu ghi chú.', 'success')
        return redirect(url_for('admin_candidate', candidate_id=candidate_id))

    answers = json.loads(row['answers_json'])
    result = json.loads(row['result_json'])
    return render_template(
        'candidate_detail.html',
        row=row,
        answers=answers,
        result=result,
        questions=QUESTIONS,
        dimensions=DIMENSIONS,
    )


@app.route('/admin/export.csv')
def export_csv():
    if not require_admin():
        return redirect(url_for('admin_login'))

    db = get_db()
    rows = db.execute('SELECT * FROM submissions ORDER BY id DESC').fetchall()

    def generate():
        headers = [
            'id', 'created_at', 'candidate_name', 'student_id', 'email', 'phone', 'department',
            'mini_test_score', 'fit_level', 'confidence_level', 'interview_priority', 'candidate_profile',
            'quick_summary', 'review_status', 'final_interview_decision'
        ]
        yield ','.join(headers) + '\n'
        for row in rows:
            result = json.loads(row['result_json'])
            fields = [
                str(row['id']),
                row['created_at'],
                row['candidate_name'],
                row['student_id'],
                row['email'],
                row['phone'],
                row['department'],
                str(result['mini_test_score']),
                result['fit_level'],
                result['confidence_level'],
                result['interview_priority'],
                result['candidate_profile'],
                result['quick_summary'].replace(',', ';'),
                row['review_status'],
                row['final_interview_decision'],
            ]
            yield ','.join('"' + str(item).replace('"', '""') + '"' for item in fields) + '\n'

    return Response(generate(), mimetype='text/csv', headers={'Content-Disposition': 'attachment; filename=candidates.csv'})


if __name__ == '__main__':
    with app.app_context():
        init_db()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
