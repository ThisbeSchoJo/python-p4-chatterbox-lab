from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

# returns an array of all messages as JSON, ordered by created_at in ascending order
@app.route('/messages', methods=["GET", "POST"])
def messages():
    if request.method == 'GET':
        # GET
        # returns an array of all messages as JSON, ordered by created_at in ascending order
        messages = Message.query.order_by(Message.created_at.asc()).all()
        response_body = jsonify([message.to_dict() for message in messages])
        return make_response(response_body, 200)
    elif request.method == 'POST':
        # POST
        # creates a new message with a body and username from params, and returns the newly created post as JSON
        data = request.get_json()

        new_message = Message(
            body = data.get('body'),
            username = data.get('username'),
        )
        db.session.add(new_message)
        db.session.commit()

        return make_response(jsonify(new_message.to_dict()), 201)

@app.route('/messages/<int:id>', methods=["PATCH", "DELETE"])
def messages_by_id(id):
    message = Message.query.filter_by(id=id).first()

    if not message:
        return make_response(jsonify({"error": "Message not found"}), 404)

    if request.method == "PATCH":
        data = request.get_json()

        # Ensure 'body' is present in the request
        if "body" not in data:
            return make_response(jsonify({"error": "Missing 'body' field"}), 400)

        message.body = data["body"]
        db.session.commit()

        return make_response(jsonify(message.to_dict()), 200)

    elif request.method == "DELETE":
        db.session.delete(message)
        db.session.commit()
        return make_response(jsonify({"message": "Message successfully deleted"}), 200)

if __name__ == '__main__':
    app.run(port=5555)
