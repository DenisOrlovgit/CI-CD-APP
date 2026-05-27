from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
import time

app = Flask(__name__)
CORS(app)

def get_connection():
    return psycopg2.connect(
        host="db-service",
        database="votesdb",
        user="user",
        password="password"
    )

def init_db():
    while True:
        try:
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS votes (
                    id SERIAL PRIMARY KEY,
                    option_name TEXT NOT NULL
                )
            """)

            conn.commit()
            conn.close()
            break

        except Exception as e:
            print("Waiting for DB...")
            print(e)
            time.sleep(3)

@app.route("/api/vote", methods=["POST"])
def vote():
    data = request.json

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO votes (option_name) VALUES (%s)",
        (data["option"],)
    )

    conn.commit()
    conn.close()


    return jsonify({"message": "Vote saved!"})

@app.route("/api/results")
def results():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT option_name, COUNT(*)
        FROM votes
        GROUP BY option_name
    """)

    rows = cursor.fetchall()

    conn.close()

    return jsonify(dict(rows))


init_db()

app.run(host="0.0.0.0", port=5000)