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


def save_note(group_code, text, user_name):
    """Сохраняет заметку в базу данных и возвращает её ID."""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            # Получаем ID группы по коду
            cursor.execute("SELECT id FROM groups WHERE code = %s;", (group_code,))
            group_id = cursor.fetchone()[0]

            cursor.execute("INSERT INTO notes (group_id, text, user_name) VALUES (%s, %s, %s) RETURNING id;",
                           (group_id, text, user_name))
            note_id = cursor.fetchone()[0]
            conn.commit()
            return note_id


def get_notes(group_code):
    """Получает все заметки для группы."""
    with get_connection() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute("""
                SELECT n.id, n.text, n.user_name FROM notes n
                JOIN groups g ON n.group_id = g.id
                WHERE g.code = %s
                ORDER BY n.created_at DESC;
            """, (group_code,))
            return [(note['id'], note['text'], note['user_name']) for note in cursor.fetchall()]


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


def delete_group(group_code):
    """Удаляет группу по коду."""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM groups WHERE code = %s;", (group_code,))
            conn.commit()


def save_task(group_code, title, description, deadline, user_name):
    """Сохраняет задачу в базу данных и возвращает её ID."""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            # Получаем ID группы по коду
            cursor.execute("SELECT id FROM groups WHERE code = %s;", (group_code,))
            group_id = cursor.fetchone()[0]

            cursor.execute("""
                INSERT INTO tasks (group_id, title, description, deadline, user_name) 
                VALUES (%s, %s, %s, %s, %s) RETURNING id;
            """, (group_id, title, description, deadline, user_name))
            task_id = cursor.fetchone()[0]
            conn.commit()
            return task_id


def get_tasks(group_code, user_name):
    """Получает все задачи для группы и пользователя."""
    with get_connection() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute("""
                SELECT t.id, t.title, t.description, t.deadline, t.user_name FROM tasks t
                JOIN groups g ON t.group_id = g.id
                WHERE g.code = %s AND t.user_name = %s
                ORDER BY t.deadline ASC;
            """, (group_code, user_name))
            return [(task['id'], task['title'], task['description'],
                    task['deadline'], task['user_name']) for task in cursor.fetchall()]


def delete_task(task_id):
    """Удаляет задачу по ID."""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM tasks WHERE id = %s;", (task_id,))
            conn.commit()


def save_message(group_code, user_name, message):
    """Сохраняет сообщение в чате."""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            # Получаем ID группы по коду
            cursor.execute("SELECT id FROM groups WHERE code = %s;", (group_code,))
            group_id = cursor.fetchone()[0]

            cursor.execute("""
                INSERT INTO group_messages (group_id, user_name, message) 
                VALUES (%s, %s, %s) RETURNING id;
            """, (group_id, user_name, message))
            message_id = cursor.fetchone()[0]
            conn.commit()
            return message_id


def get_messages(group_code, last_message_id=0):
    """Получает все сообщения для группы, начиная с указанного ID."""
    with get_connection() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute("""
                SELECT m.id, m.user_name, m.message, m.created_at FROM group_messages m
                JOIN groups g ON m.group_id = g.id
                WHERE g.code = %s AND m.id > %s
                ORDER BY m.created_at ASC;
            """, (group_code, last_message_id))
            return [(msg['id'], msg['user_name'], msg['message'],
                    msg['created_at']) for msg in cursor.fetchall()]


def delete_message(message_id):
    """Удаляет сообщение по ID."""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM group_messages WHERE id = %s;", (message_id,))
            conn.commit()


def get_last_message_id(group_code):
    """Возвращает ID последнего сообщения в группе."""
    with get_connection() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute("""
                SELECT MAX(m.id) as last_id FROM group_messages m
                JOIN groups g ON m.group_id = g.id
                WHERE g.code = %s;
            """, (group_code,))
            result = cursor.fetchone()
            return result['last_id'] if result['last_id'] else 0


def get_message_count(group_code):
    """Возвращает количество сообщений в группе"""
    with get_connection() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute("""
                SELECT COUNT(*) as count FROM group_messages m
                JOIN groups g ON m.group_id = g.id
                WHERE g.code = %s;
            """, (group_code,))
            result = cursor.fetchone()
            return result['count'] if result else 0


def get_group_users(group_code, exclude_user=None):
    """Получает список пользователей группы, исключая указанного пользователя"""
    with get_connection() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            query = """
                SELECT u.name FROM users u
                JOIN groups g ON u.group_id = g.id
                WHERE g.code = %s
            """
            params = [group_code]

            if exclude_user:
                query += " AND u.name != %s"
                params.append(exclude_user)

            query += " ORDER BY u.name;"

            cursor.execute(query, params)
            return [user['name'] for user in cursor.fetchall()]


def save_private_message(group_code, sender, receiver, message):
    """Сохраняет личное сообщение в базе данных."""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            # Получаем ID группы по коду
            cursor.execute("SELECT id FROM groups WHERE code = %s;", (group_code,))
            group_id = cursor.fetchone()[0]

            cursor.execute("""
                INSERT INTO private_messages (group_id, sender, receiver, message) 
                VALUES (%s, %s, %s, %s) RETURNING id;
            """, (group_id, sender, receiver, message))
            message_id = cursor.fetchone()[0]
            conn.commit()
            return message_id


def get_private_messages(group_code, user1, user2):
    """Получает личные сообщения между двумя пользователями."""
    with get_connection() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute("""
                SELECT m.id, m.sender, m.receiver, m.message, m.created_at 
                FROM private_messages m
                JOIN groups g ON m.group_id = g.id
                WHERE g.code = %s AND 
                ((m.sender = %s AND m.receiver = %s) OR (m.sender = %s AND m.receiver = %s))
                ORDER BY m.created_at ASC;
            """, (group_code, user1, user2, user2, user1))
            return [(msg['id'], msg['sender'], msg['receiver'],
                     msg['message'], msg['created_at']) for msg in cursor.fetchall()]


def delete_private_message(message_id):
    """Удаляет личное сообщение по ID."""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM private_messages WHERE id = %s;", (message_id,))
            conn.commit()


def get_private_message_count(group_code, user1, user2):
    """Возвращает количество личных сообщений между пользователями."""
    with get_connection() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute("""
                SELECT COUNT(*) as count FROM private_messages m
                JOIN groups g ON m.group_id = g.id
                WHERE g.code = %s AND 
                ((m.sender = %s AND m.receiver = %s) OR (m.sender = %s AND m.receiver = %s));
            """, (group_code, user1, user2, user2, user1))
            result = cursor.fetchone()
            return result['count'] if result else 0


def check_user_exists_in_group(name, group_code):
    """Проверяет, существует ли пользователь с таким именем в группе, без проверки пароля."""
    with get_connection() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute("""
                SELECT u.id FROM users u
                JOIN groups g ON u.group_id = g.id
                WHERE u.name = %s AND g.code = %s;
            """, (name, group_code))
            user = cursor.fetchone()
            return user is not None


def verify_user_password(name, password, group_code):
    """Проверяет, соответствует ли пароль пользователю в группе."""
    with get_connection() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute("""
                SELECT u.id FROM users u
                JOIN groups g ON u.group_id = g.id
                WHERE u.name = %s AND u.password = %s AND g.code = %s;
            """, (name, password, group_code))
            user = cursor.fetchone()
            return user is not None