import json
from pathlib import Path

from flask import Blueprint, Response, current_app, request
from flask_appbuilder import IndexView

from keychain.database.db import db
from keychain.database.models import Field, Password

base_view = Blueprint(
    "base_view", __name__, template_folder=Path(__file__).parent / "templates"
)


class KeychainIndexView(IndexView):
    index_template = "index.html"


@base_view.route("/check_password", methods=["GET"])
def check_password():
    if request.authorization.password != current_app.config["PASSWORD"]:
        return Response("Forbidden", status=403)
    return Response(
        response=json.dumps(
            {
                "message": "password is correct",
                "token": current_app.config["TOKEN"],
            }
        ),
        status=200,
    )


@base_view.route("/api", methods=["GET", "POST"])
def passwords_view():
    if request.authorization.password != current_app.config["TOKEN"]:
        return Response("Forbidden", status=403)
    if request.method == "POST":
        password = Password(
            name=request.json["name"],
            fields=[Field(name=k, value=v) for k, v in request.json["fields"].items()],
        )
        db.session.add(password)
        db.session.commit()
        return Response(response=repr(password), status=200)
    passwords = db.session.execute(
        db.select(Password).order_by(Password.created_at)
    ).scalars()
    return Response(
        response=json.dumps([x.json() for x in passwords]),
        status=200,
    )


@base_view.route("/api/<int:pk>", methods=["GET", "PUT"])
def password_view(pk):
    if request.authorization.password != current_app.config["TOKEN"]:
        return Response("Forbidden", status=403)
    password = db.get_or_404(Password, pk)
    if request.method == "GET":
        return Response(response=repr(password), status=200)
    if request.method == "PUT":
        password.name = request.json["name"]
        password.image_url = request.json["image_url"]
        new_fields = []
        names = [x.name for x in password.fields]
        for f in password.fields:
            if f.is_deleted:
                print("0.5. deleted")
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
    if request.method == "DELETE":
        db.session.delete(password)
        db.session.commit()
        return Response(
            response=json.dumps({"message": "Password deleted successfuly"}),
            status=200,
        )
