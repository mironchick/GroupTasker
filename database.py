import psycopg2
from psycopg2.extras import DictCursor

# Подключение к базе данных
DB_NAME = "grouptasker"
DB_USER = "postgres"
DB_PASSWORD = "123456"
DB_HOST = "localhost"


def get_connection():
    """Создает и возвращает соединение с базой данных."""
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST
    )


def create_group(name, code, creator_name, creator_password):
    """Создает новую группу в базе данных и добавляет создателя в таблицу пользователей."""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO groups (name, code) VALUES (%s, %s) RETURNING id;", (name, code))
            group_id = cursor.fetchone()[0]

            # Добавляем создателя группы в users
            cursor.execute("INSERT INTO users (name, password, group_id) VALUES (%s, %s, %s);",
                           (creator_name, creator_password, group_id))

            conn.commit()
            return group_id


def check_group_exists(group_code):
    """Проверяет, существует ли группа с данным кодом."""
    with get_connection() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute("SELECT id FROM groups WHERE code = %s;", (group_code,))
            group = cursor.fetchone()
            return group is not None


def check_user_exists(name, password, group_code):
    """Проверяет, существует ли пользователь в группе."""
    with get_connection() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute("""
                SELECT u.id FROM users u
                JOIN groups g ON u.group_id = g.id
                WHERE u.name = %s AND u.password = %s AND g.code = %s;
            """, (name, password, group_code))
            user = cursor.fetchone()
            return user is not None


def add_user_to_group(name, password, group_code):
    """Добавляет пользователя в группу, если код группы существует."""
    with get_connection() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            # Получаем ID группы
            cursor.execute("SELECT id FROM groups WHERE code = %s;", (group_code,))
            group = cursor.fetchone()

            if not group:
                return None

            group_id = group["id"]
            cursor.execute("INSERT INTO users (name, password, group_id) VALUES (%s, %s, %s);",
                           (name, password, group_id))
            conn.commit()
            return True


def save_note(group_code, text):
    """Сохраняет заметку в базу данных и возвращает её ID."""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            # Получаем ID группы по коду
            cursor.execute("SELECT id FROM groups WHERE code = %s;", (group_code,))
            group_id = cursor.fetchone()[0]

            cursor.execute("INSERT INTO notes (group_id, text) VALUES (%s, %s) RETURNING id;",
                           (group_id, text))
            note_id = cursor.fetchone()[0]
            conn.commit()
            return note_id


def get_notes(group_code):
    """Получает все заметки для группы."""
    with get_connection() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute("""
                SELECT n.id, n.text FROM notes n
                JOIN groups g ON n.group_id = g.id
                WHERE g.code = %s
                ORDER BY n.created_at DESC;
            """, (group_code,))
            return [(note['id'], note['text']) for note in cursor.fetchall()]


def delete_note(note_id):
    """Удаляет заметку по ID."""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM notes WHERE id = %s;", (note_id,))
            conn.commit()


def get_group_code(group_id):
    """Получает код группы по ID."""
    with get_connection() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute("SELECT code FROM groups WHERE id = %s;", (group_id,))
            group = cursor.fetchone()
            return group['code'] if group else None
