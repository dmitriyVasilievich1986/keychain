from sqlalchemy.orm import relationship, mapped_column, Mapped
from flask import Flask, request, Response, render_template
from flask_sqlalchemy import SQLAlchemy
from cryptography.fernet import Fernet
from datetime import datetime
from typing import List
import sqlalchemy as sa
from os import environ
import json



app = Flask(__name__)

app.config.from_object("config")
app.static_url_path = app.config["STATIC_URL_PATH"]
app.template_folder = app.config["TEMPLATE_FOLDER"]
app.static_folder = app.config["STATIC_FOLDER"]

db = SQLAlchemy(app)

f = Fernet(app.config["SECRET_KEY"])


class Password(db.Model):
    __tablename__ = "password"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, unique=True, nullable=False)
    created_at = sa.Column(sa.DateTime, nullable=False, default=datetime.now)
    image_url = sa.Column(sa.String(256), nullable=True, default="/static/i/no-photo.png")
    fields: Mapped[List["Field"]] = relationship(cascade="all, delete-orphan")

    def __repr__(self):
        return json.dumps(self.json())

    def json(self):
        fields = sorted(
            [x.json() for x in self.fields], key=lambda x: x["created_at"], reverse=True
        )
        return {
            "id": self.id,
            "fields": fields,
            "name": self.name,
            "image_url": self.image_url,
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

    @property
    def get_value(self):
        return f.decrypt(self.value).decode()

    def check(self, value):
        return self.get_value == value

    def json(self):
        return {
            "name": self.name,
            "value": self.get_value,
            "is_deleted": self.is_deleted,
            "created_at": str(self.created_at.replace(microsecond=0)),
        }


@app.route("/")
def index_view():
    return render_template("index.html")


@app.route("/check_password", methods=["GET"])
def check_password():
    if request.authorization.password != environ["SECRET"]:
        return Response("Forbidden", status=403)
    return Response(
        response=json.dumps(
            {
                "message": "password is correct",
                "token": app.config["TOKEN"],
            }
        ),
        status=200,
    )


@app.route("/api", methods=["GET", "POST"])
def passwords_view():
    if request.authorization.password != app.config["TOKEN"]:
        return Response("Forbidden", status=403)
    if request.method == "POST":
        password = Password(
            name=request.json["name"],
            fields=[Field(name=k, value=v) for k, v in request.json["fields"].items()],
        )
        db.session.add(password)
        db.session.commit()
        return Response(response=repr(password), status=200)
    passwords = db.session.execute(db.select(Password).order_by(Password.created_at)).scalars()
    return Response(response=json.dumps([x.json() for x in passwords]), status=200)


@app.route("/api/<int:pk>", methods=["GET", "PUT"])
def password_view(pk):
    if request.authorization.password != app.config["TOKEN"]:
        return Response("Forbidden", status=403)
    password = db.get_or_404(Password, pk)
    if request.method == "GET":
        return Response(response=repr(password), status=200)
    elif request.method == "PUT":
        password.name = request.json["name"]
        password.image_url = request.json["image_url"]
        new_fields = list()
        names = [x.name for x in password.fields]
        for f in password.fields:
            if f.is_deleted:
                print("0.5. deleted")
                pass
            elif f.name in request.json["fields"] and not f.check(
                request.json["fields"][f.name]
            ):
                new_fields.append(
                    Field(name=f.name, value=request.json["fields"][f.name])
                )
                f.is_deleted = True
                print("1. add new field and set to deleted")
            elif f.name not in request.json["fields"]:
                print("2. set to deleted")
                f.is_deleted = True
            else:
                print("3. nothing changed")
        for k, v in request.json["fields"].items():
            if k not in names:
                print("4. add new field")
                new_fields.append(Field(name=k, value=v))
        for f in new_fields:
            password.fields.append(f)
        db.session.commit()
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
        host=app.config["APP_HOST"],
        port=app.config["APP_PORT"],
    )
