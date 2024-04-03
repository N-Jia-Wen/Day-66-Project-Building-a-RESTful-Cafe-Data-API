from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean
import random

admin_api_key = "any api key"

app = Flask(__name__)


# CREATE DB
class Base(DeclarativeBase):
    pass


# Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
database = SQLAlchemy(model_class=Base)
database.init_app(app)


# Cafe TABLE Configuration
class Cafe(database.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    map_url: Mapped[str] = mapped_column(String(500), nullable=False)
    img_url: Mapped[str] = mapped_column(String(500), nullable=False)
    location: Mapped[str] = mapped_column(String(250), nullable=False)
    seats: Mapped[str] = mapped_column(String(250), nullable=False)
    has_toilet: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_wifi: Mapped[bool] = mapped_column(Boolean, nullable=False)
    has_sockets: Mapped[bool] = mapped_column(Boolean, nullable=False)
    can_take_calls: Mapped[bool] = mapped_column(Boolean, nullable=False)
    coffee_price: Mapped[str] = mapped_column(String(250), nullable=True)


with app.app_context():
    database.create_all()


@app.route("/")
def home():
    return render_template("index.html")


# HTTP GET - Read Record
@app.route("/random", methods=["GET"])
def get_random_cafe():
    all_cafes = database.session.execute(database.select(Cafe)).scalars()
    # Using scalars allows you to treat the object as a list, all() then actually converts the cafe data into a list
    # where we can then use random.choice() on it
    cafes_obj_list = all_cafes.all()
    cafe = random.choice(cafes_obj_list)

    return jsonify(cafe={
            "id": cafe.id,
            "name": cafe.name,
            "map_url": cafe.map_url,
            "img_url": cafe.img_url,
            "location": cafe.location,
            "has_sockets": cafe.has_sockets,
            "has_toilet": cafe.has_toilet,
            "has_wifi": cafe.has_wifi,
            "can_take_calls": cafe.can_take_calls,
            "seats": cafe.seats,
            "coffee_price": cafe.coffee_price
        })


@app.route("/all")
def get_all_cafe():
    all_cafes = database.session.execute(database.select(Cafe)).scalars().all()
    cafes_list = [{
        "id": cafe.id,
        "name": cafe.name,
        "map_url": cafe.map_url,
        "img_url": cafe.img_url,
        "location": cafe.location,
        "has_sockets": cafe.has_sockets,
        "has_toilet": cafe.has_toilet,
        "has_wifi": cafe.has_wifi,
        "can_take_calls": cafe.can_take_calls,
        "seats": cafe.seats,
        "coffee_price": cafe.coffee_price
    }
        for cafe in all_cafes
    ]
    return jsonify(cafes=cafes_list)


@app.route("/search")
def nearby_cafes():
    location = request.args.get("loc")
    if location is None:
        return "<p>Please type in a valid location.</p>"
    else:
        cafes_nearby = database.session.execute(database.select(Cafe)
                                                .where(Cafe.location == location.title())).scalars().all()
        if not cafes_nearby:
            return jsonify(error={
                "Not Found": "Sorry, we don't have a cafe at that location."
            })
        else:
            cafes_list = [{
                "id": cafe.id,
                "name": cafe.name,
                "map_url": cafe.map_url,
                "img_url": cafe.img_url,
                "location": cafe.location,
                "has_sockets": cafe.has_sockets,
                "has_toilet": cafe.has_toilet,
                "has_wifi": cafe.has_wifi,
                "can_take_calls": cafe.can_take_calls,
                "seats": cafe.seats,
                "coffee_price": cafe.coffee_price
            }
                for cafe in cafes_nearby
            ]
            return jsonify(cafes=cafes_list)


# HTTP POST - Create Record
@app.route("/add", methods=["POST"])
def add_cafe():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("loc"),
        has_sockets=bool(request.form.get("sockets")),
        has_toilet=bool(request.form.get("toilet")),
        has_wifi=bool(request.form.get("wifi")),
        can_take_calls=bool(request.form.get("calls")),
        seats=request.form.get("seats"),
        coffee_price=request.form.get("coffee_price")
    )
    database.session.add(new_cafe)
    database.session.commit()
    return jsonify(response={
        "success": "Successfully added the new cafe."
    })


# HTTP PUT/PATCH - Update Record
@app.route("/update-price/<cafe_id>", methods=["PATCH"])
def update_price(cafe_id):
    new_price = request.args.get("new_price")
    cafe_to_update = database.session.execute(database.select(Cafe).where(Cafe.id == cafe_id)).scalar()
    if cafe_to_update is not None:
        cafe_to_update.coffee_price = new_price
        database.session.commit()
        return jsonify(success="Successfully updated the price.")
    else:
        return jsonify(error={
            "Not Found": "Sorry, a cafe with that id was not found in the database."
        }), 404


# HTTP DELETE - Delete Record
@app.route("/report-closed/<cafe_id>", methods=["DELETE"])
def delete_closed_cafe(cafe_id):
    api_key = request.args.get("api-key")
    if api_key == admin_api_key:
        cafe_to_delete = database.session.execute(database.select(Cafe).where(Cafe.id == cafe_id)).scalar()
        if cafe_to_delete is not None:
            database.session.delete(cafe_to_delete)
            database.session.commit()
            return jsonify(success="Successfully deleted records of the cafe.")
        else:
            return jsonify(error={
                "Not Found": "Sorry, a cafe with that id was not found in the database."
            }), 404
    else:
        return jsonify(
            error="Sorry, you are not allowed to perform this action. Make sure you have the right api key."), 403


if __name__ == '__main__':
    app.run()
