import os
import sqlite3
from typing import Any, Dict, List, Optional


DB_PATH = os.path.join(os.path.dirname(__file__), 'app.db')


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _column_exists(conn: sqlite3.Connection, table: str, column: str) -> bool:
    """Verifica se uma coluna existe em uma tabela"""
    cursor = conn.execute(f"PRAGMA table_info({table})")
    columns = [row[1] for row in cursor.fetchall()]
    return column in columns


def init_db() -> None:
    with get_conn() as conn:
        # Tabela de usuários
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
              id TEXT PRIMARY KEY,
              name TEXT NOT NULL,
              email TEXT NOT NULL UNIQUE,
              password_hash TEXT NOT NULL,
              created_at TEXT NOT NULL
            )
            """
        )
        # Adicionar coluna matricula se não existir (migração)
        if not _column_exists(conn, 'users', 'matricula'):
            try:
                # SQLite não permite adicionar UNIQUE diretamente, então adicionamos sem e criamos índice
                conn.execute("ALTER TABLE users ADD COLUMN matricula TEXT")
                # Criar índice único para valores não nulos
                conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_matricula ON users(matricula) WHERE matricula IS NOT NULL AND matricula != ''")
            except sqlite3.OperationalError:
                pass
        conn.commit()
        # Tabela de relatórios/manifestações
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS reports (
              id TEXT PRIMARY KEY,
              user_id TEXT NOT NULL,
              tipo TEXT NOT NULL,
              titulo TEXT NOT NULL,
              mensagem TEXT NOT NULL,
              turma TEXT,
              aluno_nome TEXT,
              anonimo INTEGER NOT NULL DEFAULT 0,
              created_at TEXT NOT NULL,
              FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """
        )
        # Tabela de respostas do administrador
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS responses (
              id TEXT PRIMARY KEY,
              report_id TEXT NOT NULL,
              admin_message TEXT NOT NULL,
              created_at TEXT NOT NULL,
              FOREIGN KEY (report_id) REFERENCES reports(id)
            )
            """
        )
        # Tabela de sessões
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
              token TEXT PRIMARY KEY,
              user_id TEXT NOT NULL,
              created_at TEXT NOT NULL,
              FOREIGN KEY (user_id) REFERENCES users(id)
            )
            """
        )
        conn.commit()


def insert_report(r: Dict[str, Any]) -> None:
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO reports (id, user_id, tipo, titulo, mensagem, turma, aluno_nome, anonimo, created_at)
            VALUES (?,?,?,?,?,?,?,?,?)
            """,
            (
                r['id'], r['userId'], r['tipo'], r['titulo'], r['mensagem'],
                r.get('turma') or '', r.get('alunoNome') or '', 1 if r.get('anonimo') else 0, r['createdAt']
            ),
        )
        conn.commit()


def get_reports_by_user(user_id: str) -> List[Dict[str, Any]]:
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT id, user_id as userId, tipo, titulo, mensagem, turma, aluno_nome as alunoNome, anonimo, created_at as createdAt FROM reports WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,),
        )
        results = []
        for row in cur.fetchall():
            r = dict(row)
            r['anonimo'] = bool(r['anonimo'])  # Converter int para bool
            results.append(r)
        return results


def get_report(report_id: str) -> Optional[Dict[str, Any]]:
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT id, user_id as userId, tipo, titulo, mensagem, turma, aluno_nome as alunoNome, anonimo, created_at as createdAt FROM reports WHERE id = ?",
            (report_id,),
        )
        row = cur.fetchone()
        if not row:
            return None
        result = dict(row)
        result['anonimo'] = bool(result['anonimo'])  # Converter int para bool
        return result


def delete_report(report_id: str) -> bool:
    with get_conn() as conn:
        cur = conn.execute("DELETE FROM reports WHERE id = ?", (report_id,))
        conn.commit()
        return cur.rowcount > 0


def get_all_reports() -> List[Dict[str, Any]]:
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT id, user_id as userId, tipo, titulo, mensagem, turma, aluno_nome as alunoNome, anonimo, created_at as createdAt FROM reports ORDER BY created_at DESC"
        )
        results = []
        for row in cur.fetchall():
            r = dict(row)
            r['anonimo'] = bool(r['anonimo'])  # Converter int para bool
            results.append(r)
        return results


# Funções para usuários
def insert_user(user: Dict[str, Any]) -> None:
    with get_conn() as conn:
        # Garantir que a coluna matricula existe
        if not _column_exists(conn, 'users', 'matricula'):
            try:
                # SQLite não permite adicionar UNIQUE diretamente, então adicionamos sem e criamos índice
                conn.execute("ALTER TABLE users ADD COLUMN matricula TEXT")
                # Criar índice único para valores não nulos
                conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_matricula ON users(matricula) WHERE matricula IS NOT NULL AND matricula != ''")
                conn.commit()
            except sqlite3.OperationalError:
                pass
        
        # Verificar se coluna existe para decidir qual query usar
        has_matricula = _column_exists(conn, 'users', 'matricula')
        
        if has_matricula:
            conn.execute(
                """
                INSERT INTO users (id, name, email, matricula, password_hash, created_at)
                VALUES (?,?,?,?,?,?)
                """,
                (
                    user['id'], 
                    user['name'], 
                    user['email'], 
                    user.get('matricula', '') or None, 
                    user['passwordHash'], 
                    user.get('createdAt', '')
                )
            )
        else:
            conn.execute(
                """
                INSERT INTO users (id, name, email, password_hash, created_at)
                VALUES (?,?,?,?,?)
                """,
                (
                    user['id'], 
                    user['name'], 
                    user['email'], 
                    user['passwordHash'], 
                    user.get('createdAt', '')
                )
            )
        conn.commit()


def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    with get_conn() as conn:
        # Verificar se coluna matricula existe
        has_matricula = _column_exists(conn, 'users', 'matricula')
        if has_matricula:
            cur = conn.execute(
                "SELECT id, name, email, matricula, password_hash as passwordHash FROM users WHERE LOWER(email) = LOWER(?)",
                (email.strip(),)
            )
        else:
            cur = conn.execute(
                "SELECT id, name, email, password_hash as passwordHash FROM users WHERE LOWER(email) = LOWER(?)",
                (email.strip(),)
            )
        row = cur.fetchone()
        if not row:
            return None
        result = dict(row)
        if not has_matricula:
            result['matricula'] = None
        return result


def get_user_by_matricula(matricula: str) -> Optional[Dict[str, Any]]:
    with get_conn() as conn:
        if not _column_exists(conn, 'users', 'matricula'):
            return None
        cur = conn.execute(
            "SELECT id, name, email, matricula, password_hash as passwordHash FROM users WHERE matricula = ?",
            (matricula.strip(),)
        )
        row = cur.fetchone()
        return dict(row) if row else None


def get_user_by_email_or_matricula(login: str) -> Optional[Dict[str, Any]]:
    """Busca usuário por email ou matrícula"""
    login = login.strip()
    if not login:
        return None
    
    with get_conn() as conn:
        has_matricula = _column_exists(conn, 'users', 'matricula')
        
        # Tenta primeiro por email
        if has_matricula:
            cur = conn.execute(
                "SELECT id, name, email, matricula, password_hash as passwordHash FROM users WHERE LOWER(email) = LOWER(?)",
                (login,)
            )
        else:
            cur = conn.execute(
                "SELECT id, name, email, password_hash as passwordHash FROM users WHERE LOWER(email) = LOWER(?)",
                (login,)
            )
        row = cur.fetchone()
        if row:
            result = dict(row)
            if not has_matricula:
                result['matricula'] = None
            return result
        
        # Se não encontrou e tem coluna matricula, tenta por matrícula
        if has_matricula:
            cur = conn.execute(
                "SELECT id, name, email, matricula, password_hash as passwordHash FROM users WHERE matricula = ?",
                (login,)
            )
            row = cur.fetchone()
            return dict(row) if row else None
        
        return None


def get_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    with get_conn() as conn:
        has_matricula = _column_exists(conn, 'users', 'matricula')
        if has_matricula:
            cur = conn.execute(
                "SELECT id, name, email, matricula FROM users WHERE id = ?",
                (user_id,)
            )
        else:
            cur = conn.execute(
                "SELECT id, name, email FROM users WHERE id = ?",
                (user_id,)
            )
        row = cur.fetchone()
        if not row:
            return None
        result = dict(row)
        if not has_matricula:
            result['matricula'] = None
        return result


# Funções para sessões
def create_session(token: str, user_id: str) -> None:
    from datetime import datetime
    with get_conn() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO sessions (token, user_id, created_at)
            VALUES (?,?,?)
            """,
            (token, user_id, datetime.now().isoformat())
        )
        conn.commit()


def get_session_user(token: Optional[str]) -> Optional[Dict[str, Any]]:
    if not token:
        return None
    with get_conn() as conn:
        cur = conn.execute(
            """
            SELECT u.id, u.name, u.email 
            FROM sessions s
            JOIN users u ON s.user_id = u.id
            WHERE s.token = ?
            """,
            (token,)
        )
        row = cur.fetchone()
        return dict(row) if row else None


def destroy_session(token: Optional[str]) -> None:
    if not token:
        return
    with get_conn() as conn:
        conn.execute("DELETE FROM sessions WHERE token = ?", (token,))
        conn.commit()


# Funções para respostas
def insert_response(response: Dict[str, Any]) -> None:
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO responses (id, report_id, admin_message, created_at)
            VALUES (?,?,?,?)
            """,
            (response['id'], response['report_id'], response['admin_message'], response['created_at'])
        )
        conn.commit()


def get_response_by_report(report_id: str) -> Optional[Dict[str, Any]]:
    with get_conn() as conn:
        cur = conn.execute(
            "SELECT id, report_id, admin_message, created_at FROM responses WHERE report_id = ?",
            (report_id,)
        )
        row = cur.fetchone()
        return dict(row) if row else None


def get_report_with_response(report_id: str) -> Optional[Dict[str, Any]]:
    with get_conn() as conn:
        cur = conn.execute(
            """
            SELECT r.id, r.user_id as userId, r.tipo, r.titulo, r.mensagem, 
                   r.turma, r.aluno_nome as alunoNome, r.anonimo, r.created_at as createdAt,
                   resp.id as response_id, resp.admin_message, resp.created_at as response_created_at
            FROM reports r
            LEFT JOIN responses resp ON r.id = resp.report_id
            WHERE r.id = ?
            """,
            (report_id,)
        )
        row = cur.fetchone()
        if not row:
            return None
        result = dict(row)
        result['anonimo'] = bool(result['anonimo'])  # Converter int para bool
        if result.get('response_id'):
            result['response'] = {
                'id': result['response_id'],
                'admin_message': result['admin_message'],
                'created_at': result['response_created_at']
            }
        return result


