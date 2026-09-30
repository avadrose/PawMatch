import os

os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"] = "test-secret-key"

import pytest

from app import app
from models import db, User, Dog


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