from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    """PawMatch user account."""

    __tablename__ = "users"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(30),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.Text,
        nullable=False
    )

    email = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    first_name = db.Column(
        db.String(50),
        nullable=False
    )

    last_name = db.Column(
        db.String(50),
        nullable=False
    )

    bio = db.Column(
        db.Text
    )

    city = db.Column(
        db.String(100)
    )

    state = db.Column(
        db.String(50)
    )

    profile_image_url = db.Column(
        db.Text
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now()
    )

    dogs = db.relationship(
        "Dog",
        backref="owner",
        cascade="all, delete-orphan"
    )

    favorites = db.relationship(
        "Favorite",
        backref="user",
        cascade="all, delete-orphan"
    )

    adoption_requests = db.relationship(
        "AdoptionRequest",
        backref="user",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User {self.username}>"


class Shelter(db.Model):
    """Animal shelter or rescue organization."""

    __tablename__ = "shelters"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(150),
        nullable=False
    )

    email = db.Column(
        db.String(100)
    )

    phone = db.Column(
        db.String(30)
    )

    website_url = db.Column(
        db.Text
    )

    address = db.Column(
        db.Text
    )

    city = db.Column(
        db.String(100)
    )

    state = db.Column(
        db.String(50)
    )

    dogs = db.relationship(
        "Dog",
        backref="shelter"
    )

    def __repr__(self):
        return f"<Shelter {self.name}>"

class Dog(db.Model):
    """Dog profile for either a user-owned or adoptable dog."""

    __tablename__ = "dogs"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    owner_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True
    )

    shelter_id = db.Column(
        db.Integer,
        db.ForeignKey("shelters.id"),
        nullable=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    breed = db.Column(
        db.String(100)
    )

    age = db.Column(
        db.Integer
    )

    size = db.Column(
        db.String(30)
    )

    sex = db.Column(
        db.String(20)
    )

    temperament = db.Column(
        db.Text
    )

    description = db.Column(
        db.Text
    )

    image_url = db.Column(
        db.Text
    )

    is_adoptable = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    city = db.Column(
        db.String(100)
    )

    state = db.Column(
        db.String(50)
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now()
    )

    favorites = db.relationship(
        "Favorite",
        backref="dog",
        cascade="all, delete-orphan"
    )

    adoption_requests = db.relationship(
        "AdoptionRequest",
        backref="dog",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Dog {self.name}>"


class Favorite(db.Model):
    """A user's saved/favorited dog."""

    __tablename__ = "favorites"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    dog_id = db.Column(
        db.Integer,
        db.ForeignKey("dogs.id"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now()
    )

    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "dog_id",
            name="unique_user_dog_favorite"
        ),
    )

    def __repr__(self):
        return f"<Favorite user={self.user_id} dog={self.dog_id}>"


class AdoptionRequest(db.Model):
    """Request from a user to adopt an adoptable dog."""

    __tablename__ = "adoption_requests"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    dog_id = db.Column(
        db.Integer,
        db.ForeignKey("dogs.id"),
        nullable=False
    )

    message = db.Column(
        db.Text
    )

    status = db.Column(
        db.String(30),
        nullable=False,
        default="pending"
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now()
    )

    __table_args__ = (
        db.CheckConstraint(
            "status IN ('pending', 'approved', 'declined', 'cancelled')",
            name="valid_adoption_status"
        ),
    )

    def __repr__(self):
        return (
            f"<AdoptionRequest user={self.user_id} "
            f"dog={self.dog_id} status={self.status}>"
        )

class PlaydateRequest(db.Model):
    """Request for two PawMatch dogs to have a playdate."""

    __tablename__ = "playdate_requests"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    requester_dog_id = db.Column(
        db.Integer,
        db.ForeignKey("dogs.id"),
        nullable=False
    )

    recipient_dog_id = db.Column(
        db.Integer,
        db.ForeignKey("dogs.id"),
        nullable=False
    )

    date = db.Column(
        db.Date
    )

    time = db.Column(
        db.Time
    )

    location = db.Column(
        db.String(200)
    )

    message = db.Column(
        db.Text
    )

    status = db.Column(
        db.String(30),
        nullable=False,
        default="pending"
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now()
    )

    requester_dog = db.relationship(
        "Dog",
        foreign_keys=[requester_dog_id],
        backref="sent_playdate_requests"
    )

    recipient_dog = db.relationship(
        "Dog",
        foreign_keys=[recipient_dog_id],
        backref="received_playdate_requests"
    )

    __table_args__ = (
        db.CheckConstraint(
            "status IN ('pending', 'accepted', 'declined', 'cancelled', 'completed')",
            name="valid_playdate_status"
        ),
        db.CheckConstraint(
            "requester_dog_id <> recipient_dog_id",
            name="different_playdate_dogs"
        ),
    )

    def __repr__(self):
        return (
            f"<PlaydateRequest "
            f"{self.requester_dog_id} -> {self.recipient_dog_id} "
            f"status={self.status}>"
        )


class Message(db.Model):
    """Private message sent from one PawMatch user to another."""

    __tablename__ = "messages"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    sender_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    recipient_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    body = db.Column(
        db.Text,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now()
    )

    is_read = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    sender = db.relationship(
        "User",
        foreign_keys=[sender_id],
        backref="sent_messages"
    )

    recipient = db.relationship(
        "User",
        foreign_keys=[recipient_id],
        backref="received_messages"
    )

    __table_args__ = (
        db.CheckConstraint(
            "sender_id <> recipient_id",
            name="different_message_users"
        ),
    )

    def __repr__(self):
        return (
            f"<Message "
            f"{self.sender_id} -> {self.recipient_id}>"
        )


class Review(db.Model):
    """Review one PawMatch user leaves for another."""

    __tablename__ = "reviews"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    reviewer_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    reviewed_user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    playdate_request_id = db.Column(
        db.Integer,
        db.ForeignKey("playdate_requests.id"),
        nullable=True
    )

    rating = db.Column(
        db.Integer,
        nullable=False
    )

    comment = db.Column(
        db.Text
    )

    created_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=db.func.now()
    )

    reviewer = db.relationship(
        "User",
        foreign_keys=[reviewer_id],
        backref="reviews_written"
    )

    reviewed_user = db.relationship(
        "User",
        foreign_keys=[reviewed_user_id],
        backref="reviews_received"
    )

    playdate_request = db.relationship(
        "PlaydateRequest",
        backref="reviews"
    )

    __table_args__ = (
        db.CheckConstraint(
            "rating >= 1 AND rating <= 5",
            name="valid_review_rating"
        ),
        db.CheckConstraint(
            "reviewer_id <> reviewed_user_id",
            name="different_review_users"
        ),
    )

    def __repr__(self):
        return (
            f"<Review reviewer={self.reviewer_id} "
            f"reviewed={self.reviewed_user_id} "
            f"rating={self.rating}>"
        )