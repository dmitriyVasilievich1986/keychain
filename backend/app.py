from sqlalchemy.orm import relationship, mapped_column, Mapped
from flask import Flask, request, Response, render_template
from flask_sqlalchemy import SQLAlchemy
from cryptography.fernet import Fernet
from dotenv import load_dotenv
from datetime import datetime
from pathlib import Path
from typing import List
import sqlalchemy as sa
from os import environ
import json


BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "passwords.sqlite"

app = Flask(
    import_name=__name__,
    static_url_path="/static",
    template_folder=BASE_DIR / "templates",
    static_folder=BASE_DIR.parent / "static",
)
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_PATH}"
db = SQLAlchemy(app)

load_dotenv()
SECRET_KEY = environ["SECRET_KEY"]
f = Fernet(SECRET_KEY)


class Password(db.Model):
    __tablename__ = "password"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, unique=True, nullable=False)
    created_at = sa.Column(sa.DateTime, nullable=False, default=datetime.now)
    fields: Mapped[List["Field"]] = relationship(cascade="all, delete-orphan")

    def __repr__(self):
        return json.dumps(self.json())

    def json(self):
        return {
            "id": self.id,
            "name": self.name,
            "fields": [x.json() for x in self.fields],
        }


class Field(db.Model):
    __tablename__ = "field"

    name = sa.Column(sa.String, nullable=False)
    value = sa.Column(sa.BINARY, nullable=False)
    id = sa.Column(sa.Integer, primary_key=True)
    is_deleted = sa.Column(sa.Boolean, default=False)
    password_id = mapped_column(sa.ForeignKey("password.id"))
    created_at = sa.Column(sa.DateTime, nullable=False, default=datetime.now)

    def __init__(self, value: str, *args, **kwargs: dict):
        super().__init__(value=f.encrypt(str(value).encode()), **kwargs)

    def __repr__(self):
        return json.dumps(self.json())

    def json(self):
        return {
            "name": self.name,
            "value": f.decrypt(self.value).decode(),
            "created_at": str(self.created_at.replace(microsecond=0)),
        }


@app.route("/")
def index_view():
    return render_template("index.html")


@app.route("/api", methods=["GET", "POST"])
def passwords_view():
    if request.method == "POST":
        password = Password(
            name=request.json["name"],
            fields=[Field(name=k, value=v) for k, v in request.json["fields"].items()],
        )
        db.session.add(password)
        db.session.commit()
        return Response(response=repr(password), status=200)
    passwords = db.session.execute(db.select(Password)).scalars()
    return Response(response=json.dumps([x.json() for x in passwords]), status=200)


@app.route("/api/<int:pk>", methods=["GET", "DELETE"])
def password_view(pk):
    password = db.get_or_404(Password, pk)
    if request.method == "GET":
        return Response(response=repr(password), status=200)
    elif request.method == "DELETE":
        db.session.delete(password)
        db.session.commit()
        return Response(
            response=json.dumps({"message": "Password deleted successfuly"}),
            status=200,
        )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port="3000",
        debug=True,
    )
