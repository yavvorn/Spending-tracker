import sys
from unittest.mock import Mock, patch
from spending_tracker.app import app
from spending_tracker.extensions import bcrypt
from spending_tracker.validators import email_validator


def test_create_user_happy_path(mocker):
    client = app.test_client()
    response_data = {
        "username": "test_user",
        "email": "test_user@gmail.com",
        "password": "TestPassword2134!"
    }

    query_executor_mock = Mock()
    mocker.patch('spending_tracker.routes.users.query_executor', new=query_executor_mock)

    email_validator_mock = Mock(return_value=True)
    mocker.patch('spending_tracker.routes.users.email_validator', new=email_validator_mock)

    password_validator_mock = Mock(return_value=True)
    mocker.patch('spending_tracker.routes.users.password_validator', new=password_validator_mock)

    password_hash_mock = Mock(return_value="hashed_password")
    mocker.patch('spending_tracker.routes.users.password_hash', new=password_hash_mock)

    response = client.post("/users", json=response_data)

    assert response.status_code == 201
    query_executor_mock.assert_called_once_with(
        "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
        ("test_user", "test_user@gmail.com", "hashed_password"),
        get_result=False
    )
    email_validator_mock.assert_called_once_with("test_user@gmail.com")
    password_validator_mock.assert_called_once_with("TestPassword2134!")
    password_hash_mock.assert_called_once_with("TestPassword2134!", bcrypt)


def test_create_user_invalid_email_path():
    client = app.test_client()
    response_data = {
        "username": "test_user",
        "email": "plainaddress",
        "password": "TestPassword2134!"
    }
    response = client.post("/users", json=response_data)
    assert response.status_code == 400
    assert response.get_json() == {"error": "Invalid email address provided."}


def test_create_user_invalid_password_path():
    client = app.test_client()
    response_data = {
        "username": "test_user",
        "email": "test_user@gmail.com",
        "password": "TestPassword1234"
    }
    response = client.post("/users", json=response_data)
    assert response.status_code == 400
    assert response.get_json() == {
        "error": "Password must contain at least one uppercase letter, one number, and one special character."
    }


def test_update_user_valid_data():
    client = app.test_client()
    response_data = {
        "username": "updated_user",
        "email": "updated_user@gmail.com",
        "password": "UpdatedPassword123!"
    }
    user_id = 1
    response = client.put(f"/users/{user_id}", json=response_data)
    assert response.status_code == 204


def test_update_user_invalid_email():
    client = app.test_client()

    response_data = {
        "username": "updated_user",
        "email": "something.com",  # Invalid email (missing '@')
        "password": "UpdatedPassword123!"
    }

    user_id = 1  # Assuming a user with ID 1 exists for the test
    response = client.put(f"/users/{user_id}", json=response_data)
    assert response.status_code == 400
    assert response.get_json() == {"error": "Invalid email address provided."}


def test_update_user_invalid_password():
    client = app.test_client()

    response_data = {
        "username": "updated_user",
        "email": "updated_user@gmail.com",
        "password": "short"  # Invalid password (too short)
    }

    user_id = 1
    response = client.put(f"/users/{user_id}", json=response_data)

    assert response.status_code == 400
    assert response.get_json() == {
        "error": "Password must contain at least one uppercase letter, one number, and one special character."
    }


def test_delete_user_success():
    client = app.test_client()
    user_id = 1
    response = client.delete(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.get_json() == {}


def test_delete_user_not_found():
    client = app.test_client()
    user_id = sys.maxsize
    with patch('spending_tracker.routes.users.query_executor') as mock_query_executor:
        mock_query_executor.side_effect = Exception("User not found.")
        response = client.delete(f"/users/{user_id}")
        assert response.status_code == 404
        assert response.get_json() == {"error": "User not found."}

