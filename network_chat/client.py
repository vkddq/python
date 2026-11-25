"""Консольний клієнт: python client.py [ім'я]."""

import json
import math
import queue
import socket
import sys
import threading

HOST = "127.0.0.1"
PORT = 5000
MAX_MESSAGE = 4096


def send(connection, message):
    data = (json.dumps(message, ensure_ascii=False, allow_nan=False) + "\n").encode("utf-8")
    if len(data) > MAX_MESSAGE:
        raise ValueError("Повідомлення перевищує 4096 байтів.")
    connection.sendall(data)


def read_keyboard(events, ready, stopped):
    ready.wait()
    while not stopped.is_set():
        try:
            line = input()
        except EOFError:
            events.put(("input", "/quit"))
            return
        events.put(("input", line))
        if line == "/quit":
            return


def receive(connection, events):
    buffer = b""
    try:
        while True:
            chunk = connection.recv(4096)
            if not chunk:
                break
            buffer += chunk
            while b"\n" in buffer:
                line, buffer = buffer.split(b"\n", 1)
                if len(line) + 1 > MAX_MESSAGE:
                    raise ValueError("Завелике повідомлення сервера.")
                message = json.loads(line.decode("utf-8"))
                if not isinstance(message, dict):
                    raise ValueError("Некоректне повідомлення сервера.")
                events.put(("message", message))
            if len(buffer) >= MAX_MESSAGE:
                raise ValueError("Завелике повідомлення сервера.")
    except (OSError, ValueError, UnicodeError, RecursionError):
        pass
    finally:
        events.put(("disconnected", None))


def command(line, name):
    if line.startswith("/move"):
        parts = line.split()
        if len(parts) != 3 or parts[0] != "/move":
            raise ValueError("Використання: /move 12.5 33.8")
        try:
            x, y = float(parts[1]), float(parts[2])
        except ValueError:
            raise ValueError("Координати мають бути числами.") from None
        if not all(math.isfinite(value) and -10000 <= value <= 10000 for value in (x, y)):
            raise ValueError("Координати мають бути від -10000 до 10000.")
        return {"type": "position", "name": name, "x": x, "y": y}
    if not line.strip() or len(line) > 500:
        raise ValueError("Введіть непорожній текст до 500 символів.")
    return {"type": "chat", "name": name, "text": line}


def show(message, positions):
    kind = message.get("type")
    if kind == "position":
        positions[message["name"]] = (message["x"], message["y"])
        print(f"{message['name']}: позиція ({message['x']}, {message['y']})")
    elif kind == "chat":
        print(f"{message['name']}: {message['text']}")
    elif kind == "leave":
        positions.pop(message["name"], None)
        print(f"{message['name']} залишив/залишила чат.")
    elif kind == "error":
        print(f"Помилка: {message.get('message', '')}")


def main():
    try:
        name = (sys.argv[1] if len(sys.argv) > 1 else input("Ваше ім'я: ")).strip()
    except (EOFError, KeyboardInterrupt):
        return
    events = queue.Queue()
    ready = threading.Event()
    stopped = threading.Event()
    positions = {}
    try:
        with socket.create_connection((HOST, PORT)) as connection:
            send(connection, {"type": "hello", "name": name})
            threading.Thread(target=receive, args=(connection, events), daemon=True).start()
            threading.Thread(target=read_keyboard, args=(events, ready, stopped), daemon=True).start()
            registered = False
            try:
                while True:
                    event, value = events.get()
                    if event == "disconnected":
                        print("Зв'язок із сервером втрачено.")
                        break
                    if event == "message":
                        if value.get("type") == "welcome":
                            name = value["name"]
                            positions.update(value["positions"])
                            registered = True
                            print(f"Вітаємо, {name}! Учасники: {positions}")
                            print("Введіть текст, /move x y або /quit.")
                            ready.set()
                        else:
                            show(value, positions)
                        continue
                    if value == "/quit":
                        break
                    if registered:
                        try:
                            message = command(value, name)
                            send(connection, message)
                            show(message, positions)
                        except ValueError as problem:
                            print(f"Помилка: {problem}")
            finally:
                stopped.set()
                try:
                    connection.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass
    except OSError as problem:
        print(f"Не вдалося підтримати зв'язок із сервером: {problem}")
    except ValueError as problem:
        print(f"Помилка: {problem}")
    except KeyboardInterrupt:
        print("\nРоботу завершено.")
    finally:
        stopped.set()


if __name__ == "__main__":
    main()
