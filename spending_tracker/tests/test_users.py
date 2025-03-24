import pytest  # for the fixture
from unittest.mock import Mock, patch
from spending_tracker.app import app
from spending_tracker.helpers import generate_password_hash

from spending_tracker.tests import jwt_generator


@pytest.fixture
def auth_headers():
    token = jwt_generator.generate_mock_jwt()
    headers = {"Authorization": f"Bearer {token}"}
    return headers


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

# needs updating
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

# needs updating
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


def test_update_user_valid_data(mocker, auth_headers):
    from spending_tracker.routes import users # tuk si pomognah s chatgpt

    client = app.test_client()

    mock_user = Mock()
    mock_user.id = 1
    mock_user.username = "original_username"
    mock_user.email = "original_email@gmail.com"
    mock_user.password = "hashed_old_password"

    query_mock = Mock()
    filter_by_mock = Mock()
    first_mock = Mock(return_value=mock_user)
    filter_by_mock.first = first_mock
    query_mock.filter_by = Mock(return_value=filter_by_mock)

    user_class_mock = mocker.patch.object(users, 'User')
    user_class_mock.query = query_mock

    mocker.patch.object(users, 'email_validator', return_value=True)
    mocker.patch.object(users, 'password_validator', return_value=True)
    mocker.patch.object(users, 'check_password_hash', return_value=False)

    mocker.patch.object(users, 'generate_password_hash', return_value="hashed_new_password")

    db_session_mock = Mock()
    mocker.patch.object(users, 'db').session = db_session_mock

    response_data = {
        "username": "updated_user",
        "email": "updated_user@gmail.com",
        "password": "UpdatedPassword123!"
    }

    response = client.patch("/users", json=response_data, headers=auth_headers)

    assert response.status_code == 200

    assert mock_user.username == "updated_user"
    assert mock_user.email == "updated_user@gmail.com"
    assert mock_user.password == "hashed_new_password"

    db_session_mock.commit.assert_called_once()


@patch('spending_tracker.models.db.session')
def test_update_user_invalid_email(mock_db_session, auth_headers):
    client = app.test_client()

    with patch('spending_tracker.models.User.query') as mock_query:
        mock_user = Mock()
        mock_user.id = 1
        mock_user.username = "original_username"
        mock_user.email = "original_email@gmail.com"

        mock_query.filter_by.return_value.first.return_value = mock_user

        response_data = {
            "username": "updated_user",
            "email": "something.com",  # Invalid email (missing '@')
            "password": "UpdatedPassword123!"
        }

        response = client.patch("/users", json=response_data, headers=auth_headers)

        assert response.status_code == 400
        assert response.get_json() == {"error": "Invalid email address provided."}

        mock_db_session.commit.assert_not_called()


@patch('spending_tracker.models.db.session')
def test_update_user_invalid_password(mock_db_session, auth_headers):
    client = app.test_client()

    with patch('spending_tracker.models.User.query') as mock_query:
        mock_user = Mock()
        mock_user.id = 1
        mock_user.username = "original_username"
        mock_user.email = "original_email@gmail.com"

        mock_query.filter_by.return_value.first.return_value = mock_user

        response_data = {
            "username": "updated_user",
            "email": "updated_user@gmail.com",
            "password": "short"  # Invalid password (too short)
        }

        response = client.patch("/users", json=response_data, headers=auth_headers)

        assert response.status_code == 400
        assert response.get_json() == {
            "error": "Password must contain at least one uppercase letter, one number, and one special character."
        }

        mock_db_session.commit.assert_not_called()


@patch('spending_tracker.models.db.session')
def test_delete_user_success(mock_db_session, auth_headers):
    client = app.test_client()

    with patch('spending_tracker.models.User.query') as mock_query:
        mock_user = Mock()
        mock_user.id = 1
        mock_user.username = "testuser"

        mock_query.filter_by.return_value.first.return_value = mock_user
        response = client.delete("/users", headers=auth_headers)

        assert response.status_code == 204

        mock_db_session.delete.assert_called_once_with(mock_user)
        mock_db_session.commit.assert_called_once()