"""Консольний TCP-сервер. Запуск: python server.py."""

import json
import math
import socket
import threading
import unicodedata

HOST = "127.0.0.1"
PORT = 5000
MAX_MESSAGE = 4096
MAX_CLIENTS = 20
positions = {}
clients = {}        
lock = threading.Lock()


def encode(message):
    return (json.dumps(message, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")


def send_locked(connection, message):
    try:
        connection.sendall(encode(message))
        return True
    except OSError:
        return False


def remove_locked(name):
    connection = clients.pop(name, None)
    positions.pop(name, None)
    if connection is not None:
        try:
            connection.shutdown(socket.SHUT_RDWR)
        except OSError:
            pass
        connection.close()
        return True
    return False


def broadcast_locked(message, exclude=None):
    """Викликається лише під lock; невдалі адресати теж залишають чат."""
    pending = [(message, exclude)]
    while pending:
        current, excluded = pending.pop(0)
        failed = []
        for name, connection in list(clients.items()):
            if name != excluded and not send_locked(connection, current):
                failed.append(name)
        for name in failed:
            if remove_locked(name):
                pending.append(({"type": "leave", "name": name}, None))


def reject_constant(value):
    raise ValueError("Недопустиме JSON-число")


def read_messages(connection):
    """Повертає (об'єкт, помилка, закрити), враховуючи межі рядків."""
    buffer = b""
    while True:
        chunk = connection.recv(4096)
        if not chunk:
            return
        buffer += chunk
        while b"\n" in buffer:
            line, buffer = buffer.split(b"\n", 1)
            if len(line) + 1 > MAX_MESSAGE:
                yield None, "Повідомлення перевищує 4096 байтів.", True
                return
            try:
                text = line.decode("utf-8")
            except UnicodeDecodeError:
                yield None, "Повідомлення має бути у UTF-8.", True
                return
            try:
                message = json.loads(text, parse_constant=reject_constant)
            except (ValueError, RecursionError):
                yield None, "Некоректний JSON.", False
                continue
            yield message, None, False
        if len(buffer) >= MAX_MESSAGE:
            yield None, "Повідомлення перевищує 4096 байтів.", True
            return


def hello_name(message):
    if not isinstance(message, dict) or message.get("type") != "hello":
        raise ValueError("Першим повідомленням має бути hello.")
    name = message.get("name")
    if not isinstance(name, str):
        raise ValueError("Ім'я має бути рядком.")
    if any(unicodedata.category(char) in ("Cc", "Zl", "Zp", "Cs") for char in name):
        raise ValueError("Ім'я не може містити керувальні символи.")
    name = name.strip()
    if not 1 <= len(name) <= 24:
        raise ValueError("Ім'я має містити від 1 до 24 символів.")
    return name


def validate(message, name):
    if not isinstance(message, dict):
        raise ValueError("Повідомлення має бути JSON-об'єктом.")
    kind = message.get("type")
    if kind not in ("position", "chat"):
        raise ValueError("Невідомий тип повідомлення.")
    if message.get("name") != name:
        raise ValueError("Ім'я має збігатися із зареєстрованим.")
    if kind == "position":
        for key in ("x", "y"):
            value = message.get(key)
            if type(value) not in (int, float) or not -10000 <= value <= 10000 or not math.isfinite(value):
                raise ValueError("Координати мають бути скінченними числами від -10000 до 10000.")
        return {"type": kind, "name": name, "x": message["x"], "y": message["y"]}
    text = message.get("text")
    if not isinstance(text, str) or not text.strip() or len(text) > 500:
        raise ValueError("Текст має бути непорожнім рядком до 500 символів.")
    return {"type": kind, "name": name, "text": text}


def handle_client(connection):
    name = None
    try:
        for message, error, fatal in read_messages(connection):
            if name is None:
                try:
                    if error:
                        raise ValueError(error)
                    candidate = hello_name(message)
                    with lock:
                        if candidate in clients:
                            raise ValueError("Це ім'я вже зайняте.")
                        if len(clients) >= MAX_CLIENTS:
                            raise ValueError("Чат заповнений: максимум 20 учасників.")
                        name = candidate
                        clients[name] = connection
                        positions[name] = (0.0, 0.0)
                        welcome = {"type": "welcome", "name": name, "positions": dict(positions)}
                        if not send_locked(connection, welcome):
                            remove_locked(name)
                            return
                        broadcast_locked({"type": "position", "name": name, "x": 0.0, "y": 0.0}, name)
                except ValueError as problem:
                    with lock:
                        send_locked(connection, {"type": "error", "message": str(problem)})
                    return
                continue
            try:
                if error:
                    raise ValueError(error)
                outgoing = validate(message, name)
                with lock:
                    if clients.get(name) is not connection:
                        return
                    if outgoing["type"] == "position":
                        positions[name] = (outgoing["x"], outgoing["y"])
                    broadcast_locked(outgoing, name)
            except ValueError as problem:
                with lock:
                    sent = send_locked(connection, {"type": "error", "message": str(problem)})
                if fatal or not sent:
                    return
    except OSError:
        pass
    finally:
        with lock:
            if name is not None and clients.get(name) is connection:
                remove_locked(name)
                broadcast_locked({"type": "leave", "name": name})
        connection.close()


def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind((HOST, PORT))
        listener.listen()
        print(f"Сервер слухає {HOST}:{PORT}")
        try:
            while True:
                connection, _ = listener.accept()
                threading.Thread(target=handle_client, args=(connection,), daemon=True).start()
        except KeyboardInterrupt:
            print("\nСервер зупинено.")
        finally:
            with lock:
                for name in list(clients):
                    remove_locked(name)


if __name__ == "__main__":
    main()
