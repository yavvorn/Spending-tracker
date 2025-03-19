import pytest  # for the fixture
from unittest.mock import Mock, patch
from spending_tracker.app import app
from spending_tracker.tests import jwt_generator


@pytest.fixture
def auth_headers():
    token = jwt_generator.generate_mock_jwt()
    headers = {"Authorization": f"Bearer {token}"}
    return headers

#ok
def test_create_user_happy_path(mocker):
    client = app.test_client()
    response_data = {
        "username": "test_user",
        "email": "test_user@gmail.com",
        "password": "TestPassword2134!"
    }

    user_mock = Mock()
    user_class_mock = Mock(return_value=user_mock)
    mocker.patch('spending_tracker.routes.auth.User', new=user_class_mock)

    db_session_mock = Mock()
    mocker.patch('spending_tracker.routes.auth.db.session', new=db_session_mock)

    email_validator_mock = Mock(return_value=True)
    mocker.patch('spending_tracker.routes.auth.email_validator', new=email_validator_mock)

    password_validator_mock = Mock(return_value=True)
    mocker.patch('spending_tracker.routes.auth.password_validator', new=password_validator_mock)

    password_hash_mock = Mock(return_value="hashed_password")
    mocker.patch('spending_tracker.routes.auth.generate_password_hash', new=password_hash_mock)

    response = client.post("/register", json=response_data)

    assert response.status_code == 201

    user_class_mock.assert_called_once_with(
        username="test_user",
        email="test_user@gmail.com",
        password="hashed_password"
    )

    db_session_mock.add.assert_called_once_with(user_mock)
    db_session_mock.commit.assert_called_once()

    email_validator_mock.assert_called_once_with("test_user@gmail.com")
    password_validator_mock.assert_called_once_with("TestPassword2134!")
    password_hash_mock.assert_called_once_with("TestPassword2134!")

#ok
def test_create_user_invalid_email_path():
    client = app.test_client()
    response_data = {
        "username": "test_user",
        "email": "plainaddress",
        "password": "TestPassword2134!"
    }
    response = client.post("/register", json=response_data)
    assert response.status_code == 400
    assert response.get_json() == {"error": "Invalid email address provided."}

#ok
def test_create_user_invalid_password_path():
    client = app.test_client()
    response_data = {
        "username": "test_user",
        "email": "test_user@gmail.com",
        "password": "TestPassword1234"
    }
    response = client.post("/register", json=response_data)
    assert response.status_code == 400
    assert response.get_json() == {
        "error": "Password must contain at least one uppercase letter, one number, and one special character."
    }

# JWT required


def test_update_user_valid_data(auth_headers):  # user_id = 1
    client = app.test_client()

    response_data = {
        "username": "updated_user",
        "email": "updated_user@gmail.com",
        "password": "UpdatedPassword123!"
    }

    response = client.put(f"/users", json=response_data, headers=auth_headers)
    assert response.status_code == 204


def test_update_user_invalid_email(auth_headers):  # user_id = 1
    client = app.test_client()

    response_data = {
        "username": "updated_user",
        "email": "something.com",  # Invalid email (missing '@')
        "password": "UpdatedPassword123!"
    }

    response = client.put(f"/users", json=response_data, headers=auth_headers)
    assert response.status_code == 400
    assert response.get_json() == {"error": "Invalid email address provided."}


def test_update_user_invalid_password(auth_headers):  # user_id = 1
    client = app.test_client()

    response_data = {
        "username": "updated_user",
        "email": "updated_user@gmail.com",
        "password": "short"  # Invalid password (too short)
    }

    response = client.put(f"/users", json=response_data, headers=auth_headers)

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "Password must contain at least one uppercase letter, one number, and one special character."
    }


def test_delete_user_success(auth_headers):  # user_id = 1
    client = app.test_client()

    response = client.delete(f"/users", headers=auth_headers)
    assert response.status_code == 200
    assert response.get_json() == {}
