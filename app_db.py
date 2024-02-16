from flask import Flask, request, jsonify, abort, g
from werkzeug.exceptions import HTTPException
from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).parent
DATABASE = BASE_DIR / "test.db"

app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


# Обработка ошибок и возврат сообщения в виде JSON
@app.errorhandler(HTTPException)
def handle_exception(e):
    return jsonify({"message": e.description}), e.code


# Сериализация list --> str
@app.route("/quotes")
def get_all_quotes():
    conn = get_db()
    cursor = conn.cursor()
    select_quotes = "SELECT * FROM quotes"
    cursor.execute(select_quotes)
    quotes_db = cursor.fetchall()
    keys = ["id", "author", "text"]
    # Тоже самое через генератор списков
    # quotes = [dict(zip(keys, quote_db)) for quote_db in quotes_db]
    quotes = []
    for quote_db in quotes_db:
        quote = dict(zip(keys, quote_db))
        quotes.append(quote)
    return jsonify(quotes)

# /quotes/1
# /quotes/3
# /quotes/5
# /quotes/6
@app.route("/quotes/<int:quote_id>")
def get_quote_by_id(quote_id):
    cursor = get_db().cursor()
    select_quote_by_id = f"SELECT * FROM quotes WHERE id={quote_id}"
    cursor.execute(select_quote_by_id)
    quote_db = cursor.fetchone()  # Результат либо None либо кортеж со значенями, а не список!    
    keys = ["id", "author", "text"]
    if quote_db is None:
        abort(404, f"Quote with id={quote_id} not found")
    quote = dict(zip(keys, quote_db))
    return jsonify(quote)


@app.route("/quotes", methods=['POST'])
def create_quote():
    new_quote = request.json
    conn = get_db()
    cursor = conn.cursor()
    create_quote = "INSERT INTO quotes (author, text) VALUES (?, ?)"
    cursor.execute(create_quote, (new_quote['author'],new_quote['text']))
    conn.commit()
    new_quote_id = cursor.lastrowid
    new_quote['id'] = new_quote_id
    return jsonify(new_quote), 201


@app.route("/quotes", methods=['POST'])
def create_quote():
    new_quote = request.json
    conn = get_db()
    cursor = conn.cursor()
    create_quote = "INSERT INTO quotes (author, text) VALUES (?, ?)"
    cursor.execute(create_quote, (new_quote['author'], new_quote['text']))
    conn.commit()
    new_quote_id = cursor.lastrowid
    new_quote['id'] = new_quote_id
    return jsonify(new_quote), 201


@app.route("/quotes/<int:quote_id>", methods=["PUT"])
def edit_quote(quote_id):
    new_quote = request.json
    conn = get_db()
    cursor = conn.cursor()
    update_quote = "UPDATE quotes SET author=?, text=? WHERE id=?"
    cursor.execute(
        update_quote, (new_quote['author'], new_quote['text'], quote_id))
    conn.commit()
    if cursor.rowcount > 0:
        new_quote['id'] = quote_id
        return jsonify(new_quote), 200
    abort(404, f"Quote with id={quote_id} not found")



if __name__ == "__main__":
   app.run(debug=True)