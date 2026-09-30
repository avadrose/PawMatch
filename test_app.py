import os

os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"] = "test-secret-key"

import pytest

from app import app
from models import db, User, Dog, Shelter, Favorite, AdoptionRequest, PlaydateRequest, Message


@pytest.fixture
def client():
    """Create a fresh test database for each test."""

    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False

    with app.app_context():
        db.drop_all()
        db.create_all()

        yield app.test_client()

        db.session.remove()
        db.drop_all()

def test_homepage(client):
    """Homepage loads successfully."""

    response = client.get("/")

    assert response.status_code == 200
    assert b"PawMatch" in response.data

def test_register_user(client):
    """A new user can register."""

    response = client.post(
        "/register",
        data={
            "username": "testuser",
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "password": "password123",
            "confirm_password": "password123",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    with app.app_context():
        user = User.query.filter_by(
            username="testuser"
        ).first()

        assert user is not None
        assert user.email == "test@example.com"
        assert user.password_hash != "password123"


def test_register_user(client):
    """A new user can register."""

    response = client.post(
        "/register",
        data={
            "username": "testuser",
            "email": "test@example.com",
            "first_name": "Test",
            "last_name": "User",
            "password": "password123",
            "confirm_password": "password123",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    with app.app_context():
        user = User.query.filter_by(
            username="testuser"
        ).first()

        assert user is not None
        assert user.email == "test@example.com"
        assert user.password_hash != "password123"


def create_test_user(
    username="testuser",
    email="test@example.com",
    password="password123"
):
    """Create a test user."""

    from app import bcrypt

    user = User(
        username=username,
        email=email,
        first_name="Test",
        last_name="User",
        password_hash=bcrypt.generate_password_hash(
            password
        ).decode("utf-8")
    )

    db.session.add(user)
    db.session.commit()

    return user


def test_login_user(client):
    """A registered user can log in."""

    with app.app_context():
        create_test_user()

    response = client.post(
        "/login",
        data={
            "username": "testuser",
            "password": "password123",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Welcome back" in response.data


def test_login_wrong_password(client):
    """Login fails with an incorrect password."""

    with app.app_context():
        create_test_user()

    response = client.post(
        "/login",
        data={
            "username": "testuser",
            "password": "wrongpassword",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200
    assert b"Invalid username or password" in response.data


def test_profile_requires_login(client):
    """Logged-out users cannot access the profile page."""

    response = client.get(
        "/profile",
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"Please log in" in response.data


def test_logged_in_user_can_add_dog(client):
    """Logged-in user can create a dog."""

    with app.app_context():
        user = create_test_user()
        user_id = user.id

    with client.session_transaction() as session:
        session["user_id"] = user_id

    response = client.post(
        "/dogs/add",
        data={
            "name": "Buddy",
            "breed": "Labrador",
            "age": 3,
            "size": "Large",
            "sex": "Male",
            "temperament": "Friendly",
            "description": "A happy dog",
            "image_url": "",
            "city": "Columbus",
            "state": "Ohio",
            "is_adoptable": "y",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    with app.app_context():
        dog = Dog.query.filter_by(name="Buddy").first()

        assert dog is not None
        assert dog.owner_id == user_id


def test_user_cannot_edit_another_users_dog(client):
    """A user cannot edit a dog owned by someone else."""

    with app.app_context():
        owner = create_test_user(
            username="owner",
            email="owner@example.com"
        )

        other_user = create_test_user(
            username="otheruser",
            email="other@example.com"
        )

        dog = Dog(
            name="Buddy",
            owner_id=owner.id
        )

        db.session.add(dog)
        db.session.commit()

        dog_id = dog.id
        other_user_id = other_user.id

    with client.session_transaction() as session:
        session["user_id"] = other_user_id

    response = client.get(
        f"/dogs/{dog_id}/edit",
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b"not allowed to edit this dog" in response.data


def test_register_shelter_account(client):
    """A shelter account should create both a user and shelter profile."""

    response = client.post(
        "/register",
        data={
            "username": "happytails",
            "email": "shelter@example.com",
            "first_name": "Jamie",
            "last_name": "Smith",
            "password": "password123",
            "confirm_password": "password123",
            "account_type": "shelter",
            "shelter_name": "Happy Tails Rescue",
            "shelter_phone": "6145551234",
            "shelter_website": "https://example.com",
            "shelter_address": "123 Main Street",
            "shelter_city": "Columbus",
            "shelter_state": "OH",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    user = User.query.filter_by(
        username="happytails"
    ).first()

    assert user is not None
    assert user.account_type == "shelter"

    shelter = Shelter.query.filter_by(
        user_id=user.id
    ).first()

    assert shelter is not None
    assert shelter.name == "Happy Tails Rescue"
    assert shelter.city == "Columbus"
    assert shelter.state == "OH"

def test_logged_in_user_can_favorite_adoptable_dog(client):
    """A logged-in user should be able to favorite an adoptable dog."""

    owner = User(
        username="owner",
        email="owner@example.com",
        first_name="Dog",
        last_name="Owner",
        password_hash="hashed-password",
        account_type="individual",
    )

    adopter = User(
        username="adopter",
        email="adopter@example.com",
        first_name="Future",
        last_name="Adopter",
        password_hash="hashed-password",
        account_type="individual",
    )

    db.session.add_all([owner, adopter])
    db.session.flush()

    dog = Dog(
        owner_id=owner.id,
        name="Buddy",
        breed="Golden Retriever",
        age=3,
        size="Large",
        sex="Male",
        temperament="Friendly",
        description="A very friendly dog.",
        is_adoptable=True,
        city="Columbus",
        state="OH",
    )

    db.session.add(dog)
    db.session.commit()

    with client.session_transaction() as session:
        session["user_id"] = adopter.id

    response = client.post(
        f"/dogs/{dog.id}/favorite",
        follow_redirects=True,
    )

    assert response.status_code == 200

    favorite = Favorite.query.filter_by(
        user_id=adopter.id,
        dog_id=dog.id,
    ).first()

    assert favorite is not None


def test_user_can_submit_adoption_request(client):
    """A user should be able to request adoption of another user's dog."""

    owner = User(
        username="dogowner",
        email="dogowner@example.com",
        first_name="Dog",
        last_name="Owner",
        password_hash="hashed-password",
        account_type="individual",
    )

    adopter = User(
        username="applicant",
        email="applicant@example.com",
        first_name="Test",
        last_name="Applicant",
        password_hash="hashed-password",
        account_type="individual",
    )

    db.session.add_all([owner, adopter])
    db.session.flush()

    dog = Dog(
        owner_id=owner.id,
        name="Luna",
        breed="Husky",
        age=2,
        size="Large",
        sex="Female",
        temperament="Playful",
        description="Energetic and friendly.",
        is_adoptable=True,
        city="Columbus",
        state="OH",
    )

    db.session.add(dog)
    db.session.commit()

    with client.session_transaction() as session:
        session["user_id"] = adopter.id

    response = client.post(
        f"/dogs/{dog.id}/adopt",
        data={
            "message": "I would love to give Luna a forever home."
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    adoption_request = AdoptionRequest.query.filter_by(
        user_id=adopter.id,
        dog_id=dog.id,
    ).first()

    assert adoption_request is not None
    assert adoption_request.status == "pending"
    assert (
        adoption_request.message
        == "I would love to give Luna a forever home."
    )


def test_user_can_submit_adoption_request(client):
    """A user should be able to request adoption of another user's dog."""

    owner = User(
        username="dogowner",
        email="dogowner@example.com",
        first_name="Dog",
        last_name="Owner",
        password_hash="hashed-password",
        account_type="individual",
    )

    adopter = User(
        username="applicant",
        email="applicant@example.com",
        first_name="Test",
        last_name="Applicant",
        password_hash="hashed-password",
        account_type="individual",
    )

    db.session.add_all([owner, adopter])
    db.session.flush()

    dog = Dog(
        owner_id=owner.id,
        name="Luna",
        breed="Husky",
        age=2,
        size="Large",
        sex="Female",
        temperament="Playful",
        description="Energetic and friendly.",
        is_adoptable=True,
        city="Columbus",
        state="OH",
    )

    db.session.add(dog)
    db.session.commit()

    with client.session_transaction() as session:
        session["user_id"] = adopter.id

    response = client.post(
        f"/dogs/{dog.id}/adopt",
        data={
            "message": "I would love to give Luna a forever home."
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    adoption_request = AdoptionRequest.query.filter_by(
        user_id=adopter.id,
        dog_id=dog.id,
    ).first()

    assert adoption_request is not None
    assert adoption_request.status == "pending"
    assert (
        adoption_request.message
        == "I would love to give Luna a forever home."
    )


def test_user_can_request_playdate(client):
    """A user should be able to request a playdate with another user's dog."""

    requester = User(
        username="requester",
        email="requester@example.com",
        first_name="Playdate",
        last_name="Requester",
        password_hash="hashed-password",
        account_type="individual",
    )

    recipient = User(
        username="recipient",
        email="recipient@example.com",
        first_name="Playdate",
        last_name="Recipient",
        password_hash="hashed-password",
        account_type="individual",
    )

    db.session.add_all([requester, recipient])
    db.session.flush()

    requester_dog = Dog(
        owner_id=requester.id,
        name="Remi",
        breed="Husky",
        age=4,
        size="Large",
        sex="Male",
        temperament="Playful",
        description="Loves other dogs.",
        is_adoptable=False,
        city="Columbus",
        state="OH",
    )

    recipient_dog = Dog(
        owner_id=recipient.id,
        name="Nami",
        breed="Husky",
        age=3,
        size="Large",
        sex="Female",
        temperament="Friendly",
        description="Enjoys playdates.",
        is_adoptable=False,
        city="Columbus",
        state="OH",
    )

    db.session.add_all([
        requester_dog,
        recipient_dog,
    ])
    db.session.commit()

    with client.session_transaction() as session:
        session["user_id"] = requester.id

    response = client.post(
        f"/dogs/{recipient_dog.id}/playdate",
        data={
            "requester_dog_id": requester_dog.id,
            "date": "2026-10-10",
            "time": "14:00",
            "location": "Goodale Park",
            "message": "Would Nami like to play?",
        },
        follow_redirects=True,
    )

    assert response.status_code == 200

    playdate = PlaydateRequest.query.filter_by(
        requester_dog_id=requester_dog.id,
        recipient_dog_id=recipient_dog.id,
    ).first()

    assert playdate is not None
    assert playdate.status == "pending"
    assert playdate.location == "Goodale Park"
    assert playdate.message == "Would Nami like to play?"