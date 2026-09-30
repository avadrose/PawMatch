import os

from dotenv import load_dotenv

from flask import Flask, render_template, redirect, url_for, flash, session, g, request
from flask_bcrypt import Bcrypt

from models import db, User, Dog, Favorite, AdoptionRequest, PlaydateRequest, Message
from forms import RegisterForm, LoginForm, DogForm, DeleteDogForm, FavoriteForm, AdoptionRequestForm, AdoptionDecisionForm, PlaydateRequestForm, PlaydateDecisionForm, MessageForm
from sqlalchemy import or_

load_dotenv()

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]

db.init_app(app)
bcrypt = Bcrypt(app)

@app.before_request
def add_user_to_g():
    """Load the logged-in user before every request."""

    user_id = session.get("user_id")

    if user_id:
        g.user = db.session.get(User, user_id)
    else:
        g.user = None


@app.route("/")
def homepage():
    return render_template("home.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register a new PawMatch user."""

    form = RegisterForm()

    if form.validate_on_submit():

        existing_username = User.query.filter_by(
            username=form.username.data
        ).first()

        if existing_username:
            flash("That username is already taken.", "danger")
            return render_template("register.html", form=form)

        existing_email = User.query.filter_by(
            email=form.email.data
        ).first()

        if existing_email:
            flash("An account already exists with that email.", "danger")
            return render_template("register.html", form=form)

        password_hash = bcrypt.generate_password_hash(
            form.password.data
        ).decode("utf-8")

        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            password_hash=password_hash
        )

        db.session.add(user)
        db.session.commit()

        session["user_id"] = user.id

        flash(
            f"Welcome to PawMatch, {user.first_name}!",
            "success"
        )

        return redirect(url_for("homepage"))

    return render_template("register.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log an existing PawMatch user in."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(
            username=form.username.data
        ).first()

        if user and bcrypt.check_password_hash(
            user.password_hash,
            form.password.data
        ):
            session["user_id"] = user.id

            flash(
                f"Welcome back, {user.first_name}!",
                "success"
            )

            return redirect(url_for("homepage"))

        flash(
            "Invalid username or password.",
            "danger"
        )

    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    """Log the current user out."""

    session.pop("user_id", None)

    flash("You have been logged out.", "success")

    return redirect(url_for("homepage"))


@app.route("/profile")
def profile():
    """Show the current user's profile."""

    if not g.user:
        flash("Please log in to view your profile.", "danger")
        return redirect(url_for("login"))

    return render_template("profile.html")

@app.route("/dogs/add", methods=["GET", "POST"])
def add_dog():
    """Create a new dog belonging to the current user."""

    if not g.user:
        flash("Please log in to add a dog.", "danger")
        return redirect(url_for("login"))

    form = DogForm()

    if form.validate_on_submit():
        dog = Dog(
            owner_id=g.user.id,
            name=form.name.data,
            breed=form.breed.data,
            age=form.age.data,
            size=form.size.data,
            sex=form.sex.data,
            temperament=form.temperament.data,
            description=form.description.data,
            image_url=form.image_url.data,
            is_adoptable=form.is_adoptable.data,
            city=form.city.data,
            state=form.state.data
        )

        db.session.add(dog)
        db.session.commit()

        flash(
            f"{dog.name} was added to your profile!",
            "success"
        )

        return redirect(url_for("profile"))

    return render_template("dog_form.html", form=form)

@app.route("/dogs/<int:dog_id>")
def dog_detail(dog_id):
    """Show details for one dog."""

    dog = db.get_or_404(Dog, dog_id)

    delete_form = DeleteDogForm()
    favorite_form = FavoriteForm()

    is_favorited = False

    if g.user:
        favorite = Favorite.query.filter_by(
            user_id=g.user.id,
            dog_id=dog.id
        ).first()

        is_favorited = favorite is not None

    return render_template(
        "dog_detail.html",
        dog=dog,
        delete_form=delete_form,
        favorite_form=favorite_form,
        is_favorited=is_favorited
    )

@app.route("/dogs/<int:dog_id>/edit", methods=["GET", "POST"])
def edit_dog(dog_id):
    """Edit a dog owned by the current user."""

    if not g.user:
        flash("Please log in to edit a dog.", "danger")
        return redirect(url_for("login"))

    dog = db.get_or_404(Dog, dog_id)

    if dog.owner_id != g.user.id:
        flash("You are not allowed to edit this dog.", "danger")
        return redirect(url_for("dog_detail", dog_id=dog.id))

    form = DogForm(obj=dog)

    if form.validate_on_submit():
        dog.name = form.name.data
        dog.breed = form.breed.data
        dog.age = form.age.data
        dog.size = form.size.data
        dog.sex = form.sex.data
        dog.temperament = form.temperament.data
        dog.description = form.description.data
        dog.image_url = form.image_url.data
        dog.is_adoptable = form.is_adoptable.data
        dog.city = form.city.data
        dog.state = form.state.data

        db.session.commit()

        flash(f"{dog.name}'s profile was updated.", "success")

        return redirect(
            url_for("dog_detail", dog_id=dog.id)
        )

    return render_template(
        "dog_form.html",
        form=form,
        dog=dog
    )

@app.route("/dogs/<int:dog_id>/delete", methods=["POST"])
def delete_dog(dog_id):
    """Delete a dog owned by the current user."""

    if not g.user:
        flash("Please log in to delete a dog.", "danger")
        return redirect(url_for("login"))

    dog = db.get_or_404(Dog, dog_id)

    if dog.owner_id != g.user.id:
        flash("You are not allowed to delete this dog.", "danger")
        return redirect(
            url_for("dog_detail", dog_id=dog.id)
        )

    form = DeleteDogForm()

    if not form.validate_on_submit():
        flash("Unable to delete dog.", "danger")
        return redirect(
            url_for("dog_detail", dog_id=dog.id)
        )

    dog_name = dog.name

    db.session.delete(dog)
    db.session.commit()

    flash(
        f"{dog_name} was deleted.",
        "success"
    )

    return redirect(url_for("profile"))

@app.route("/adopt")
def adoptable_dogs():
    """Show and filter dogs currently available for adoption."""

    query = Dog.query.filter_by(is_adoptable=True)

    breed = request.args.get("breed", "").strip()
    size = request.args.get("size", "").strip()
    sex = request.args.get("sex", "").strip()
    location = request.args.get("location", "").strip()
    temperament = request.args.get("temperament", "").strip()

    if breed:
        query = query.filter(
            Dog.breed.ilike(f"%{breed}%")
        )

    if size:
        query = query.filter(
            Dog.size == size
        )

    if sex:
        query = query.filter(
            Dog.sex == sex
        )

    if location:
        location_search = f"%{location}%"

        query = query.filter(
            or_(
                Dog.city.ilike(location_search),
                Dog.state.ilike(location_search)
            )
        )

    if temperament:
        query = query.filter(
            Dog.temperament.ilike(f"%{temperament}%")
        )

    dogs = query.order_by(
        Dog.created_at.desc()
    ).all()

    return render_template(
        "adoptable_dogs.html",
        dogs=dogs,
        breed=breed,
        size=size,
        sex=sex,
        location=location,
        temperament=temperament
    )


@app.route("/dogs/<int:dog_id>/favorite", methods=["POST"])
def favorite_dog(dog_id):
    """Save an adoptable dog to the current user's favorites."""

    if not g.user:
        flash("Please log in to save dogs.", "danger")
        return redirect(url_for("login"))

    dog = db.get_or_404(Dog, dog_id)

    form = FavoriteForm()

    if not form.validate_on_submit():
        flash("Unable to save dog.", "danger")
        return redirect(
            url_for("dog_detail", dog_id=dog.id)
        )

    if not dog.is_adoptable:
        flash(
            "Only dogs available for adoption can be saved.",
            "danger"
        )
        return redirect(
            url_for("dog_detail", dog_id=dog.id)
        )

    existing_favorite = Favorite.query.filter_by(
        user_id=g.user.id,
        dog_id=dog.id
    ).first()

    if existing_favorite:
        flash(
            f"{dog.name} is already in your favorites.",
            "info"
        )
        return redirect(
            url_for("dog_detail", dog_id=dog.id)
        )

    favorite = Favorite(
        user_id=g.user.id,
        dog_id=dog.id
    )

    db.session.add(favorite)
    db.session.commit()

    flash(
        f"{dog.name} was added to your favorites!",
        "success"
    )

    return redirect(
        url_for("dog_detail", dog_id=dog.id)
    )

@app.route("/dogs/<int:dog_id>/unfavorite", methods=["POST"])
def unfavorite_dog(dog_id):
    """Remove a dog from the current user's favorites."""

    if not g.user:
        flash("Please log in first.", "danger")
        return redirect(url_for("login"))

    dog = db.get_or_404(Dog, dog_id)

    form = FavoriteForm()

    if not form.validate_on_submit():
        flash("Unable to remove favorite.", "danger")
        return redirect(
            url_for("dog_detail", dog_id=dog.id)
        )

    favorite = Favorite.query.filter_by(
        user_id=g.user.id,
        dog_id=dog.id
    ).first()

    if favorite:
        db.session.delete(favorite)
        db.session.commit()

        flash(
            f"{dog.name} was removed from your favorites.",
            "success"
        )

    return redirect(
        url_for("dog_detail", dog_id=dog.id)
    )

@app.route("/favorites")
def favorites():
    """Show the current user's saved dogs."""

    if not g.user:
        flash("Please log in to view your favorites.", "danger")
        return redirect(url_for("login"))

    favorites = Favorite.query.filter_by(
        user_id=g.user.id
    ).order_by(
        Favorite.created_at.desc()
    ).all()

    return render_template(
        "favorites.html",
        favorites=favorites
    )


@app.route("/dogs/<int:dog_id>/adopt", methods=["GET", "POST"])
def request_adoption(dog_id):
    """Submit an adoption request for an adoptable dog."""

    if not g.user:
        flash(
            "Please log in to submit an adoption request.",
            "danger"
        )
        return redirect(url_for("login"))

    dog = db.get_or_404(Dog, dog_id)

    if not dog.is_adoptable:
        flash(
            "This dog is not currently available for adoption.",
            "danger"
        )
        return redirect(
            url_for("dog_detail", dog_id=dog.id)
        )

    if dog.owner_id == g.user.id:
        flash(
            "You cannot submit an adoption request for your own dog.",
            "danger"
        )
        return redirect(
            url_for("dog_detail", dog_id=dog.id)
        )

    existing_request = AdoptionRequest.query.filter(
        AdoptionRequest.user_id == g.user.id,
        AdoptionRequest.dog_id == dog.id,
        AdoptionRequest.status.in_(["pending", "approved"])
    ).first()

    if existing_request:
        flash(
            "You already have an active adoption request for this dog.",
            "info"
        )
        return redirect(
            url_for("dog_detail", dog_id=dog.id)
        )

    form = AdoptionRequestForm()

    if form.validate_on_submit():

        adoption_request = AdoptionRequest(
            user_id=g.user.id,
            dog_id=dog.id,
            message=form.message.data
        )

        db.session.add(adoption_request)
        db.session.commit()

        flash(
            f"Your adoption request for {dog.name} was sent!",
            "success"
        )

        return redirect(
            url_for("my_adoption_requests")
        )

    return render_template(
        "adoption_request.html",
        form=form,
        dog=dog
    )


@app.route("/adoption-requests")
def my_adoption_requests():
    """Show adoption requests submitted by the logged-in user."""

    if not g.user:
        flash(
            "Please log in to view your adoption requests.",
            "danger"
        )
        return redirect(url_for("login"))

    adoption_requests = (
        AdoptionRequest.query
        .filter(AdoptionRequest.user_id == g.user.id)
        .order_by(AdoptionRequest.created_at.desc())
        .all()
    )

    return render_template(
        "my_adoption_requests.html",
        adoption_requests=adoption_requests
    )


@app.route("/adoption-requests/incoming")
def incoming_adoption_requests():
    """Show adoption requests for dogs owned by the current user."""

    if not g.user:
        flash(
            "Please log in to view incoming adoption requests.",
            "danger"
        )
        return redirect(url_for("login"))

    adoption_requests = (
        AdoptionRequest.query
        .join(Dog)
        .filter(Dog.owner_id == g.user.id)
        .order_by(AdoptionRequest.created_at.desc())
        .all()
    )

    decision_form = AdoptionDecisionForm()

    return render_template(
        "incoming_adoption_requests.html",
        adoption_requests=adoption_requests,
        decision_form=decision_form
    )


@app.route(
    "/adoption-requests/<int:request_id>/approve",
    methods=["POST"]
)
def approve_adoption_request(request_id):
    """Approve an adoption request."""

    if not g.user:
        flash("Please log in first.", "danger")
        return redirect(url_for("login"))

    adoption_request = db.get_or_404(
        AdoptionRequest,
        request_id
    )

    if adoption_request.dog.owner_id != g.user.id:
        flash(
            "You are not allowed to manage this adoption request.",
            "danger"
        )
        return redirect(url_for("homepage"))

    form = AdoptionDecisionForm()

    if not form.validate_on_submit():
        flash("Unable to update request.", "danger")
        return redirect(
            url_for("incoming_adoption_requests")
        )

    adoption_request.status = "approved"

    db.session.commit()

    flash(
        f"{adoption_request.user.username}'s request "
        f"for {adoption_request.dog.name} was approved.",
        "success"
    )

    return redirect(
        url_for("incoming_adoption_requests")
    )


@app.route(
    "/adoption-requests/<int:request_id>/decline",
    methods=["POST"]
)
def decline_adoption_request(request_id):
    """Decline an adoption request."""

    if not g.user:
        flash("Please log in first.", "danger")
        return redirect(url_for("login"))

    adoption_request = db.get_or_404(
        AdoptionRequest,
        request_id
    )

    if adoption_request.dog.owner_id != g.user.id:
        flash(
            "You are not allowed to manage this adoption request.",
            "danger"
        )
        return redirect(url_for("homepage"))

    form = AdoptionDecisionForm()

    if not form.validate_on_submit():
        flash("Unable to update request.", "danger")
        return redirect(
            url_for("incoming_adoption_requests")
        )

    adoption_request.status = "declined"

    db.session.commit()

    flash(
        f"{adoption_request.user.username}'s request "
        f"for {adoption_request.dog.name} was declined.",
        "success"
    )

    return redirect(
        url_for("incoming_adoption_requests")
    )

@app.route(
    "/dogs/<int:dog_id>/playdate",
    methods=["GET", "POST"]
)
def request_playdate(dog_id):
    """Request a playdate with another user's dog."""

    if not g.user:
        flash(
            "Please log in to request a playdate.",
            "danger"
        )
        return redirect(url_for("login"))

    recipient_dog = db.get_or_404(Dog, dog_id)

    if recipient_dog.owner_id == g.user.id:
        flash(
            "You cannot request a playdate with your own dog.",
            "danger"
        )
        return redirect(
            url_for("dog_detail", dog_id=recipient_dog.id)
        )

    user_dogs = Dog.query.filter_by(
        owner_id=g.user.id
    ).all()

    if not user_dogs:
        flash(
            "You need to add one of your dogs before requesting a playdate.",
            "danger"
        )
        return redirect(url_for("profile"))

    form = PlaydateRequestForm()

    form.requester_dog_id.choices = [
        (dog.id, dog.name)
        for dog in user_dogs
    ]

    if form.validate_on_submit():

        requester_dog = db.session.get(
            Dog,
            form.requester_dog_id.data
        )

        if (
            not requester_dog
            or requester_dog.owner_id != g.user.id
        ):
            flash(
                "That dog does not belong to your account.",
                "danger"
            )
            return redirect(
                url_for(
                    "dog_detail",
                    dog_id=recipient_dog.id
                )
            )

        playdate_request = PlaydateRequest(
            requester_dog_id=requester_dog.id,
            recipient_dog_id=recipient_dog.id,
            date=form.date.data,
            time=form.time.data,
            location=form.location.data,
            message=form.message.data
        )

        db.session.add(playdate_request)
        db.session.commit()

        flash(
            f"Playdate request sent to "
            f"{recipient_dog.name}'s owner!",
            "success"
        )

        return redirect(
            url_for("dog_detail", dog_id=recipient_dog.id)
        )

    return render_template(
        "playdate_request.html",
        form=form,
        recipient_dog=recipient_dog
    )


@app.route("/playdates/incoming")
def incoming_playdates():
    """Show playdate requests sent to the current user's dogs."""

    if not g.user:
        flash(
            "Please log in to view playdate requests.",
            "danger"
        )
        return redirect(url_for("login"))

    playdate_requests = (
        PlaydateRequest.query
        .filter(
            PlaydateRequest.recipient_dog.has(
                owner_id=g.user.id
            )
        )
        .order_by(
            PlaydateRequest.created_at.desc()
        )
        .all()
    )

    decision_form = PlaydateDecisionForm()

    return render_template(
        "incoming_playdates.html",
        playdate_requests=playdate_requests,
        decision_form=decision_form
    )


@app.route(
    "/playdates/<int:request_id>/accept",
    methods=["POST"]
)
def accept_playdate(request_id):
    """Accept an incoming playdate request."""

    if not g.user:
        flash("Please log in first.", "danger")
        return redirect(url_for("login"))

    playdate = db.get_or_404(
        PlaydateRequest,
        request_id
    )

    if playdate.recipient_dog.owner_id != g.user.id:
        flash(
            "You are not allowed to manage this playdate request.",
            "danger"
        )
        return redirect(url_for("homepage"))

    form = PlaydateDecisionForm()

    if not form.validate_on_submit():
        flash(
            "Unable to update the playdate request.",
            "danger"
        )
        return redirect(url_for("incoming_playdates"))

    playdate.status = "accepted"

    db.session.commit()

    flash(
        f"Playdate with {playdate.requester_dog.name} accepted!",
        "success"
    )

    return redirect(url_for("incoming_playdates"))


@app.route(
    "/playdates/<int:request_id>/decline",
    methods=["POST"]
)
def decline_playdate(request_id):
    """Decline an incoming playdate request."""

    if not g.user:
        flash("Please log in first.", "danger")
        return redirect(url_for("login"))

    playdate = db.get_or_404(
        PlaydateRequest,
        request_id
    )

    if playdate.recipient_dog.owner_id != g.user.id:
        flash(
            "You are not allowed to manage this playdate request.",
            "danger"
        )
        return redirect(url_for("homepage"))

    form = PlaydateDecisionForm()

    if not form.validate_on_submit():
        flash(
            "Unable to update the playdate request.",
            "danger"
        )
        return redirect(url_for("incoming_playdates"))

    playdate.status = "declined"

    db.session.commit()

    flash(
        f"Playdate request from {playdate.requester_dog.name} declined.",
        "success"
    )

    return redirect(url_for("incoming_playdates"))


@app.route("/playdates")
def my_playdates():
    """Show playdate requests sent by the current user's dogs."""

    if not g.user:
        flash(
            "Please log in to view your playdates.",
            "danger"
        )
        return redirect(url_for("login"))

    playdate_requests = (
        PlaydateRequest.query
        .filter(
            PlaydateRequest.requester_dog.has(
                owner_id=g.user.id
            )
        )
        .order_by(
            PlaydateRequest.created_at.desc()
        )
        .all()
    )

    return render_template(
        "my_playdates.html",
        playdate_requests=playdate_requests
    )


@app.route("/messages/new/<int:user_id>", methods=["GET", "POST"])
def send_message(user_id):
    """Send a private message to another PawMatch user."""

    if not g.user:
        flash("Please log in to send messages.", "danger")
        return redirect(url_for("login"))

    recipient = db.get_or_404(User, user_id)

    if recipient.id == g.user.id:
        flash("You cannot message yourself.", "danger")
        return redirect(url_for("profile"))

    form = MessageForm()

    if form.validate_on_submit():
        message = Message(
            sender_id=g.user.id,
            recipient_id=recipient.id,
            body=form.body.data
        )

        db.session.add(message)
        db.session.commit()

        flash(
            f"Message sent to {recipient.username}!",
            "success"
        )

        return redirect(url_for("messages"))

    return render_template(
        "send_message.html",
        form=form,
        recipient=recipient
    )

@app.route("/messages")
def messages():
    """Show messages received by the current user."""

    if not g.user:
        flash("Please log in to view your messages.", "danger")
        return redirect(url_for("login"))

    received_messages = (
        Message.query
        .filter_by(recipient_id=g.user.id)
        .order_by(Message.created_at.desc())
        .all()
    )

    return render_template(
        "messages.html",
        messages=received_messages
    )

if __name__ == "__main__":
    app.run(debug=True)