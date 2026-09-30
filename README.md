# 🐾 PawMatch

PawMatch is a full-stack dog adoption and social networking application built with Python, Flask, PostgreSQL, SQLAlchemy, Jinja, Bootstrap, and JavaScript.

The platform connects adopters, dog owners, shelters, and rescues in one place. Users can browse adoptable dogs, save favorites, submit adoption requests, create dog profiles, arrange playdates, send private messages, and manage their PawMatch account.

---

## Features

### User Accounts

- Register as an Individual / Dog Owner
- Register as a Shelter / Rescue
- Secure password hashing with Flask-Bcrypt
- Login and logout
- Session-based authentication
- Protected routes and ownership authorization

### Dog Profiles

- Create dog profiles
- View detailed dog profiles
- Edit owned or managed dogs
- Delete owned or managed dogs
- Add dog images using image URLs
- Mark dogs as available for adoption

### Shelter & Rescue Accounts

Shelter and rescue accounts can:

- Create an organization profile
- Add adoptable dogs
- Manage shelter listings
- Receive adoption requests
- Approve or decline adoption requests
- Communicate with PawMatch users

### Adoption

Users can:

- Browse adoptable dogs
- Search and filter dogs by:
  - Breed
  - Size
  - Sex
  - Location
  - Temperament
- Save dogs to Favorites
- Submit adoption requests
- View the status of adoption requests

Dog owners and shelters can:

- View incoming adoption requests
- Read applicant messages
- Approve or decline requests

### Playdates

Individual dog owners can:

- Request playdates with another user's dog
- Choose which of their dogs will attend
- Select a date, time, and location
- Include a message
- View sent playdate requests
- Accept or decline incoming playdate requests

### Messaging

- Send private messages to other PawMatch users
- Contact individual dog owners
- Contact shelters and rescues
- View received messages
- Reply to messages

### Favorites

- Save adoptable dogs
- View saved dogs
- Remove dogs from Favorites

---

## Technology Stack

### Backend

- Python
- Flask
- Flask-SQLAlchemy
- PostgreSQL
- Flask-Bcrypt
- Flask-WTF
- Flask-Migrate
- Alembic

### Frontend

- HTML
- CSS
- JavaScript
- Jinja
- Bootstrap 5

### Testing

- Pytest
- Flask test client
- SQLite test database

---

## Database

PawMatch uses PostgreSQL with relational models for:

- Users
- Dogs
- Shelters / Rescues
- Favorites
- Adoption Requests
- Playdate Requests
- Messages
- Reviews

Relationships include:

- One user can own multiple dogs
- One shelter can manage multiple dogs
- Users can favorite multiple dogs
- Users can submit adoption requests
- Dogs can send and receive playdate requests
- Users can send and receive private messages

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/avadrose/PawMatch.git
cd PawMatch