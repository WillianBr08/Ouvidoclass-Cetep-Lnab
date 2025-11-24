from typing import Any, Dict, List, Optional
from datetime import datetime
import db


def list_users() -> List[Dict[str, Any]]:
    """Lista todos os usuários (não usado frequentemente, mas mantido para compatibilidade)"""
    # Esta função não é mais necessária, mas mantida para compatibilidade
    return []


def find_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    """Busca usuário por email no banco de dados"""
    return db.get_user_by_email(email)


def find_user_by_email_or_matricula(login: str) -> Optional[Dict[str, Any]]:
    """Busca usuário por email ou matrícula no banco de dados"""
    return db.get_user_by_email_or_matricula(login)


def save_user(user: Dict[str, Any]) -> None:
    """Salva usuário no banco de dados"""
    if 'createdAt' not in user:
        user['createdAt'] = datetime.now().isoformat()
    db.insert_user(user)


def create_session(token: str, public_user: Dict[str, Any]) -> None:
    """Cria sessão no banco de dados"""
    db.create_session(token, public_user['id'])


def get_session_user(token: Optional[str]) -> Optional[Dict[str, Any]]:
    """Obtém usuário da sessão do banco de dados"""
    return db.get_session_user(token)


def destroy_session(token: Optional[str]) -> None:
    """Destrói sessão no banco de dados"""
    db.destroy_session(token)


def list_reports_by_user(user_id: str) -> List[Dict[str, Any]]:
    """Lista relatórios do usuário do banco de dados"""
    return db.get_reports_by_user(user_id)


def save_report(report: Dict[str, Any]) -> None:
    """Salva relatório no banco de dados"""
    db.insert_report(report)


def get_report(user_id: str, report_id: str) -> Optional[Dict[str, Any]]:
    """Obtém relatório específico do banco de dados"""
    r = db.get_report(report_id)
    if r and r.get('userId') == user_id:
        return r
    return None


def delete_report(user_id: str, report_id: str) -> bool:
    """Deleta relatório do banco de dados"""
    r = db.get_report(report_id)
    if r and r.get('userId') == user_id:
        return db.delete_report(report_id)
    return False


