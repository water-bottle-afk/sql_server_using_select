# sql\_server\_using\_select

A TCP server-client project managing a **planet exploration database**, with full CRUD capabilities and protocol-based communication.

---

## 📜 Overview

This project demonstrates a **custom-built server** in Python that interfaces with an SQLite3 database to manage information about planets and archival records. The server handles multiple client connections using `select`, and communicates using a custom protocol (`PROTO`) built on top of raw TCP sockets.

Clients can send various requests (e.g., insert new planets, retrieve data, update popularity, etc.) and get JSON responses. The system also highlights a known SQL injection vulnerability used for educational purposes.

---

## 🚀 Features

* ✅ **Custom TCP protocol** (`PROTO`) with size-prefixed messaging
* ✅ **Multi-client handling** using `select` (non-blocking I/O)
* ✅ **SQLite3 ORM layer** for database queries (Nadav\_ORM)
* ✅ **Full CRUD operations** (Create, Read, Update, Delete)
* ✅ **JSON-based request/response format**
* ✅ **Input validation** with centralized field-wise checks
* ✅ **Debug mode toggle** from CLI
* ❗ **Educational SQL injection vulnerability** in one specific query

---

## ⚠️ Demonstrated SQL Injection

> ⚠️ **Option 4** is intentionally left unsafe to show how SQL injection works in practice:

Example input:

```python
explorer = "yossi'--"
galaxy = "Andromeda"
```

Result: returns all planets discovered by `yossi` in **all** galaxies due to comment-based SQL injection.

---

## 📆 Technologies Used

| Component        | Technology                |
| ---------------- | ------------------------- |
| Database         | SQLite3                   |
| Backend Language | Python 3                  |
| Networking       | TCP Sockets with `select` |
| Protocol Layer   | Custom wrapper: `PROTO`   |
| Serialization    | JSON                      |

---

## 🧪 Suggested Advanced Improvements

### 🔐 Security

* ✅ Use **parameterized queries** to prevent SQL injection
* ⛔ Sanitize and validate all client input

### 📚 Code Quality
* ✅ Follow **PEP8** style guide

## 📁 Project Structure Example

```
sql_server_using_select/
│
├── SQL_ORM.py
├── server.py
├── client.py
├── tcp_by_size.py

├── README.md
```

---

## 🧠 Educational Value

This project is a solid learning experience in:

* Socket programming and networking
* Basic database interaction (SQLite)
* SQL injection awareness
* Protocol design and stateful servers
* Data validation and error handling

---

## How to Run?

```cmd
python server.py
# Follow instructions for debug mode
```

# Then run a client
# in another tab
```cmd
python client.py
```

---

## 🧑‍💻 Author

Created by **water-bottle-afk**
© 2025 — for educational and development purposes.

---

