import sqlite3

from flask import Flask, request, jsonify, redirect
from urllib.parse import urlparse
from hashids import Hashids

# Create the Flask application instance
app = Flask(__name__)

# Hashids encoder — salt must stay the same forever, or old codes break
hashids = Hashids(salt="my-secret-salt", min_length=6)

# Path to the SQLite database file (created automatically)
DB_PATH = "data/urls.db"


def get_db():
    """Open a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # access columns by name
    return conn


def init_db():
    """Create the 'urls' table if it doesn't already exist."""
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS urls (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            original_url TEXT    NOT NULL,
            short_code   TEXT    UNIQUE
        )
    """)
    conn.commit()
    conn.close()


@app.route("/")
def index():
    """Health-check route — confirms the server is alive."""
    return "Server is running"


@app.route("/shorten", methods=["POST"])
def shorten():
    """Accept a JSON body with a 'url' key, validate it, and return a short code."""
    data = request.json
    url = data.get("url")

    # --- validation --------------------------------------------------------
    if not url:
        return jsonify({"error": "Missing 'url' field"}), 400

    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        return jsonify({"error": "URL must start with http:// or https://"}), 400

    if not parsed.netloc:
        return jsonify({"error": "URL is missing a domain (e.g. example.com)"}), 400
    # -----------------------------------------------------------------------

    # --- insert into DB and generate short code ----------------------------
    conn = get_db()

    # Step 1: insert the URL (short_code is NULL for now)
    cursor = conn.execute(
        "INSERT INTO urls (original_url) VALUES (?)",
        (url,)
    )

    # Step 2: SQLite gives us the auto-generated id
    row_id = cursor.lastrowid

    # Step 3: encode that id into a short code
    short_code = hashids.encode(row_id)

    # Step 4: update the same row with the short code
    conn.execute(
        "UPDATE urls SET short_code = ? WHERE id = ?",
        (short_code, row_id)
    )

    conn.commit()
    conn.close()
    # -----------------------------------------------------------------------

    short_url = request.host_url + short_code   # e.g. http://localhost:5000/7vplvZ
    return jsonify({"short_url": short_url})


@app.route("/<short_code>")
def redirect_to_url(short_code):
    """Look up a short code in the DB and redirect to the original URL."""
    conn = get_db()
    row = conn.execute(
        "SELECT original_url FROM urls WHERE short_code = ?",
        (short_code,)
    ).fetchone()
    conn.close()

    if row is None:
        return jsonify({"error": "Short URL not found"}), 404

    return redirect(row["original_url"], code=302)


# Entry point: only runs when you execute this file directly
if __name__ == "__main__":
    init_db()          # create the table before the first request
    app.run(host="0.0.0.0", port=5000, debug=True)
