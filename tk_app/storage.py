import json
import os
from typing import Any, Dict, List, Optional


DATA_FILE = os.path.join(os.path.dirname(__file__), 'data.json')


def _ensure_data_file() -> None:
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    if not os.path.exists(DATA_FILE):
        _save({
            'users': [],
            'reports': [],
            'session': None,
        })


def _load() -> Dict[str, Any]:
    _ensure_data_file()
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {'users': [], 'reports': [], 'session': None}


def _save(data: Dict[str, Any]) -> None:
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_session() -> Optional[Dict[str, Any]]:
    data = _load()
    return data.get('session')


def set_session(session: Optional[Dict[str, Any]]) -> None:
    data = _load()
    data['session'] = session
    _save(data)


def list_users() -> List[Dict[str, Any]]:
    return _load().get('users', [])


def save_user(user: Dict[str, Any]) -> None:
    data = _load()
    users = data.get('users', [])
    users.append(user)
    data['users'] = users
    _save(data)


def find_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    email_l = email.strip().lower()
    for u in list_users():
        if u.get('email', '').strip().lower() == email_l:
            return u
    return None


def list_reports_by_user(user_id: str) -> List[Dict[str, Any]]:
    data = _load()
    reports = data.get('reports', [])
    return [r for r in reports if r.get('userId') == user_id]


def save_report(report: Dict[str, Any]) -> None:
    data = _load()
    reports = data.get('reports', [])
    reports.append(report)
    data['reports'] = reports
    _save(data)


def get_report(user_id: str, report_id: str) -> Optional[Dict[str, Any]]:
    for r in list_reports_by_user(user_id):
        if str(r.get('id')) == str(report_id):
            return r
    return None


def delete_report(user_id: str, report_id: str) -> bool:
    data = _load()
    reports = data.get('reports', [])
    idx = -1
    for i, r in enumerate(reports):
        if str(r.get('id')) == str(report_id) and r.get('userId') == user_id:
            idx = i
            break
    if idx == -1:
        return False
    reports.pop(idx)
    data['reports'] = reports
    _save(data)
    return True


