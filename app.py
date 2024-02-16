from flask import Flask, request, jsonify, abort
from pathlib import Path
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

BASE_DIR = Path(__file__).parent
app = Flask(__name__)


app.config['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{BASE_DIR / 'quotes.db'}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class QuoteModel(db.Model):
    __tablename__ = "quotes"
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(32), unique=False, nullable=False)
    text = db.Column(db.String(255), unique=False)
    rating = db.Column(db.Integer, nullable=False)

    def __init__(self, author, text, rating=1):
        self.author = author
        self.text = text
        self.rating = rating

    def __repr__(self):
        return f'Quote({self.author}, {self.text}, {self.rating})'

    def to_dict(self):
        return {
            "id": self.id,
            "author": self.author,
            "text": self.text,
            "rating": self.rating
        }


@app.route("/quotes")
def get_all_quotes():
    """ Сериализация list[quotes] --> list[dict] --> str(JSON)"""
    quotes = QuoteModel.query.all()
    quotes_as_dict = []
    for quote in quotes:
        quotes_as_dict.append(quote.to_dict())
    return jsonify(quotes_as_dict), 200


@app.route("/quotes/<int:quote_id>")
def get_quote_by_id(quote_id):
    quote = QuoteModel.query.get(quote_id)
    if quote is None:
        abort(404, f"Quote with id={quote_id} not found")
    return jsonify(quote.to_dict()), 200


@app.post("/quotes")
def create_quote():
    quote_data = request.json
    quote = QuoteModel(**quote_data)
    db.session.add(quote)
    db.session.commit()
    return jsonify(quote.to_dict()), 200


@app.put('/quotes/<int:quote_id>')
def edit_quote(quote_id):
    new_quote = request.json
    quote = QuoteModel.query.get(quote_id)
    if quote is None:
        abort(404, f"Quote with id={quote_id} not found")
    # if new_quote.get('author'):
    #     quote.author = new_quote['author']
    # if new_quote.get('text'):
    #     quote.text = new_quote['text']
    for key, value in new_quote.items():
        setattr(quote, key, value)
    db.session.commit()
    return jsonify(quote.to_dict()), 200


@app.route("/quotes/<int:quote_id>", methods=["DELETE"])
def delete_quote(quote_id):
    quote = QuoteModel.query.get(quote_id)
    if quote is None:
        abort(404, f"Quote with id={quote_id} not found")
    db.session.delete(quote)
    db.session.commit()
    return jsonify({"message": f"Quote with id={quote_id} has deleted"}), 200


@app.route("/quotes/filter")
def get_quotes_by_filter():
    # kwargs = request.args
    # quotes = QuoteModel.query.filter_by(**kwargs).all()
    # result = [quote.to_dict() for quote in quotes]
    # return jsonify(result)
    return jsonify([q.to_dict() for q in QuoteModel.query.filter_by(**request.args).all()])


if __name__ == "__main__":
    app.run(debug=True)