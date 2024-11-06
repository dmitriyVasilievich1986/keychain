from flask import Flask, request, Response, render_template
from cryptography.fernet import Fernet
from os import environ
import json



class PasswordApp(Flask):
    fernet: Fernet

    def init_fernet(self):
        self.fernet = Fernet(self.config["SECRET_KEY"])

app = PasswordApp(__name__)

app.config.from_object("config")
app.static_url_path = app.config["STATIC_URL_PATH"]
app.template_folder = app.config["TEMPLATE_FOLDER"]
app.static_folder = app.config["STATIC_FOLDER"]
app.init_fernet()


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

from database.db import db
from database.models import Password, Field


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
