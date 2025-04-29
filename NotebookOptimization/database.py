import psycopg2
from psycopg2.extras import DictCursor
from datetime import datetime

DB_CONFIG = {
    "dbname": "grouptasker",
    "user": "postgres",
    "password": "123456",
    "host": "localhost"
}


def execute_query(query, params=None, fetch_one=False, fetch_all=False, commit=False):
    """Универсальная функция для выполнения SQL запросов"""
    result = None
    try:
        with psycopg2.connect(**DB_CONFIG) as connection:
            with connection.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute(query, params or ())
                if commit:
                    connection.commit()
                if fetch_one:
                    result = cursor.fetchone()
                elif fetch_all:
                    result = cursor.fetchall()
    except Exception as e:
        print(f"Database error: {e}")
    return result


def create_group(name, code, creator_name, creator_password):
    """Создает новую группу и добавляет создателя"""
    group_id = execute_query(
        "INSERT INTO groups (name, code) VALUES (%s, %s) RETURNING id;",
        (name, code),
        fetch_one=True,
        commit=True
    )
    if group_id:
        execute_query(
            "INSERT INTO users (name, password, group_id) VALUES (%s, %s, %s);",
            (creator_name, creator_password, group_id[0]),
            commit=True
        )
        return group_id[0]
    return None


def check_group_exists(group_code):
    """Проверяет существование группы по коду"""
    return bool(execute_query(
        "SELECT id FROM groups WHERE code = %s;",
        (group_code,),
        fetch_one=True
    ))


def check_user_exists(name, password, group_code):
    """Проверяет существование пользователя в группе"""
    return bool(execute_query(
        """SELECT u.id FROM users u
           JOIN groups g ON u.group_id = g.id
           WHERE u.name = %s AND u.password = %s AND g.code = %s;""",
        (name, password, group_code),
        fetch_one=True
    ))


def add_user_to_group(name, password, group_code):
    """Добавляет пользователя в группу"""
    group_id = execute_query(
        "SELECT id FROM groups WHERE code = %s;",
        (group_code,),
        fetch_one=True
    )
    if group_id:
        try:
            execute_query(
                "INSERT INTO users (name, password, group_id) VALUES (%s, %s, %s);",
                (name, password, group_id[0]),
                commit=True
            )
            return True
        except psycopg2.IntegrityError:
            return False
    return None


def save_note(group_code, text, user_name):
    """Сохраняет заметку в базу данных"""
    group_id = execute_query(
        "SELECT id FROM groups WHERE code = %s;",
        (group_code,),
        fetch_one=True
    )
    if group_id:
        note_id = execute_query(
            "INSERT INTO notes (group_id, text, user_name) VALUES (%s, %s, %s) RETURNING id;",
            (group_id[0], text, user_name),
            fetch_one=True,
            commit=True
        )
        return note_id[0] if note_id else None
    return None


def get_notes(group_code):
    """Получает все заметки группы"""
    return execute_query(
        """SELECT n.id, n.text, n.user_name FROM notes n
           JOIN groups g ON n.group_id = g.id
           WHERE g.code = %s ORDER BY n.created_at DESC;""",
        (group_code,),
        fetch_all=True
    )


def delete_note(note_id):
    """Удаляет заметку по ID"""
    execute_query(
        "DELETE FROM notes WHERE id = %s;",
        (note_id,),
        commit=True
    )


def save_task(group_code, title, description, deadline, user_name):
    """Сохраняет задачу в базу данных"""
    group_id = execute_query(
        "SELECT id FROM groups WHERE code = %s;",
        (group_code,),
        fetch_one=True
    )
    if group_id:
        task_id = execute_query(
            """INSERT INTO tasks (group_id, title, description, deadline, user_name) 
               VALUES (%s, %s, %s, %s, %s) RETURNING id;""",
            (group_id[0], title, description, deadline, user_name),
            fetch_one=True,
            commit=True
        )
        return task_id[0] if task_id else None
    return None


def get_tasks(group_code, user_name):
    """Получает задачи пользователя в группе"""
    return execute_query(
        """SELECT t.id, t.title, t.description, t.deadline, t.user_name 
           FROM tasks t JOIN groups g ON t.group_id = g.id
           WHERE g.code = %s AND t.user_name = %s ORDER BY t.deadline ASC;""",
        (group_code, user_name),
        fetch_all=True
    )


def delete_task(task_id):
    """Удаляет задачу по ID"""
    execute_query(
        "DELETE FROM tasks WHERE id = %s;",
        (task_id,),
        commit=True
    )


def save_message(group_code, user_name, message):
    """Сохраняет сообщение в чат группы"""
    group_id = execute_query(
        "SELECT id FROM groups WHERE code = %s;",
        (group_code,),
        fetch_one=True
    )
    if group_id:
        message_id = execute_query(
            """INSERT INTO group_messages (group_id, user_name, message) 
               VALUES (%s, %s, %s) RETURNING id;""",
            (group_id[0], user_name, message),
            fetch_one=True,
            commit=True
        )
        return message_id[0] if message_id else None
    return None


def get_messages(group_code):
    """Получает все сообщения группы"""
    return execute_query(
        """SELECT m.id, m.user_name, m.message, m.created_at 
           FROM group_messages m JOIN groups g ON m.group_id = g.id
           WHERE g.code = %s ORDER BY m.created_at ASC;""",
        (group_code,),
        fetch_all=True
    )


def delete_message(message_id):
    """Удаляет сообщение по ID"""
    execute_query(
        "DELETE FROM group_messages WHERE id = %s;",
        (message_id,),
        commit=True
    )


def get_group_users(group_code, exclude_user=None):
    """Получает список пользователей группы"""
    query = """SELECT u.name FROM users u
               JOIN groups g ON u.group_id = g.id
               WHERE g.code = %s"""
    params = [group_code]

    if exclude_user:
        query += " AND u.name != %s"
        params.append(exclude_user)

    query += " ORDER BY u.name;"

    result = execute_query(query, params, fetch_all=True)
    return [user[0] for user in result] if result else []


def check_user_exists_in_group(name, group_code):
    """Проверяет существование пользователя в группе"""
    return bool(execute_query(
        """SELECT u.id FROM users u
           JOIN groups g ON u.group_id = g.id
           WHERE u.name = %s AND g.code = %s;""",
        (name, group_code),
        fetch_one=True
    ))


def verify_user_password(name, password, group_code):
    """Проверяет пароль пользователя"""
    return bool(execute_query(
        """SELECT u.id FROM users u
           JOIN groups g ON u.group_id = g.id
           WHERE u.name = %s AND u.password = %s AND g.code = %s;""",
        (name, password, group_code),
        fetch_one=True
    ))


def get_note_author(note_id):
    """Получает автора заметки"""
    result = execute_query(
        "SELECT user_name FROM notes WHERE id = %s;",
        (note_id,),
        fetch_one=True
    )
    return result[0] if result else None


# Добавьте эти функции в ваш database.py

def get_last_message_id(group_code):
    """Возвращает ID последнего сообщения в группе"""
    result = execute_query(
        """SELECT MAX(m.id) as last_id FROM group_messages m
           JOIN groups g ON m.group_id = g.id
           WHERE g.code = %s;""",
        (group_code,),
        fetch_one=True
    )
    return result['last_id'] if result and result['last_id'] else 0

def get_message_count(group_code):
    """Возвращает количество сообщений в группе"""
    result = execute_query(
        """SELECT COUNT(*) as count FROM group_messages m
           JOIN groups g ON m.group_id = g.id
           WHERE g.code = %s;""",
        (group_code,),
        fetch_one=True
    )
    return result['count'] if result else 0

def save_message(group_code, user_name, message):
    """Сохраняет сообщение в чат группы"""
    group_id = execute_query(
        "SELECT id FROM groups WHERE code = %s;",
        (group_code,),
        fetch_one=True
    )
    if group_id:
        message_id = execute_query(
            """INSERT INTO group_messages (group_id, user_name, message) 
               VALUES (%s, %s, %s) RETURNING id;""",
            (group_id[0], user_name, message),
            fetch_one=True,
            commit=True
        )
        return message_id[0] if message_id else None
    return None

def get_messages(group_code, last_message_id=0):
    """Получает все сообщения для группы, начиная с указанного ID"""
    return execute_query(
        """SELECT m.id, m.user_name, m.message, m.created_at 
           FROM group_messages m
           JOIN groups g ON m.group_id = g.id
           WHERE g.code = %s AND m.id > %s
           ORDER BY m.created_at ASC;""",
        (group_code, last_message_id),
        fetch_all=True
    )

def delete_message(message_id):
    """Удаляет сообщение по ID"""
    execute_query(
        "DELETE FROM group_messages WHERE id = %s;",
        (message_id,),
        commit=True
    )


def get_group_users(group_code, exclude_user=None):
    """Получает список пользователей группы, исключая указанного пользователя"""
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

    result = execute_query(query, params, fetch_all=True)
    return [user['name'] for user in result] if result else []


def save_private_message(group_code, sender, receiver, message):
    """Сохраняет личное сообщение в базе данных"""
    group_id = execute_query(
        "SELECT id FROM groups WHERE code = %s;",
        (group_code,),
        fetch_one=True
    )
    if group_id:
        message_id = execute_query(
            """INSERT INTO private_messages (group_id, sender, receiver, message) 
               VALUES (%s, %s, %s, %s) RETURNING id;""",
            (group_id[0], sender, receiver, message),
            fetch_one=True,
            commit=True
        )
        return message_id[0] if message_id else None
    return None


def get_private_messages(group_code, user1, user2):
    """Получает личные сообщения между двумя пользователями"""
    return execute_query(
        """SELECT m.id, m.sender, m.receiver, m.message, m.created_at 
           FROM private_messages m
           JOIN groups g ON m.group_id = g.id
           WHERE g.code = %s AND 
           ((m.sender = %s AND m.receiver = %s) OR (m.sender = %s AND m.receiver = %s))
           ORDER BY m.created_at ASC;""",
        (group_code, user1, user2, user2, user1),
        fetch_all=True
    )


def delete_private_message(message_id):
    """Удаляет личное сообщение по ID"""
    execute_query(
        "DELETE FROM private_messages WHERE id = %s;",
        (message_id,),
        commit=True
    )


def get_private_message_count(group_code, user1, user2):
    """Возвращает количество личных сообщений между пользователями"""
    result = execute_query(
        """SELECT COUNT(*) as count FROM private_messages m
           JOIN groups g ON m.group_id = g.id
           WHERE g.code = %s AND 
           ((m.sender = %s AND m.receiver = %s) OR (m.sender = %s AND m.receiver = %s));""",
        (group_code, user1, user2, user2, user1),
        fetch_one=True
    )
    return result['count'] if result else 0