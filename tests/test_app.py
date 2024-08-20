import pytest
from unittest.mock import Mock
from spending_tracker.app import app


def test_home_route():
    response = app.test_client().get("/")
    assert response.status_code == 200


def test_get_expense_happy_path(mocker):
    response_data = {"Food": 50}
    query_executor_mock = Mock(return_value=response_data)
    mocker.patch('spending_tracker.app.query_executor', new=query_executor_mock)
    response = app.test_client().get("/expenses/99")
    assert response.status_code == 200
    assert response.json == response_data


def test_get_expense_non_existent(mocker):
    query_executor_mock = Mock(return_value=None)
    mocker.patch('spending_tracker.app.query_executor', new=query_executor_mock)
    response = app.test_client().get("/expenses/99")
    assert response.status_code == 404
    assert response.json == {"error": "Expense doesn't exist"}


def test_create_expense_happy_path(mocker):
    new_expense_data = {"expense": "Food", "value": 100}
    query_executor_mock = Mock()  # simple mock as it doesn't return an id
    mocker.patch('spending_tracker.app.query_executor', new=query_executor_mock)
    response = app.test_client().post("/expenses", json=new_expense_data)
    assert response.status_code == 201
    assert response.json == {}


def test_create_expense_failure(mocker):
    new_expense_data = {"expense": "Food", "value": 100}
    query_executor_mock = Mock(side_effect=Exception("Database error"))
    mocker.patch('spending_tracker.app.query_executor', new=query_executor_mock)
    response = app.test_client().post("/expenses", json=new_expense_data)
    assert response.status_code == 400
    assert response.json == {"error": "Failed to create expense"}


def test_update_expense_happy_path(mocker):
    update_expense_data = {"id": 123, "expense": "Groceries", "value": 150}
    query_executor_mock = Mock(return_value=True)  # Simulating a successful update
    mocker.patch('spending_tracker.app.query_executor', new=query_executor_mock)
    response = app.test_client().put("/update", json=update_expense_data)
    assert response.status_code == 204


def test_update_expense_unsuccessful(mocker):
    update_expense_data = {"id": 123, "expense": "Groceries", "value": 150}
    query_executor_mock = Mock(return_value=None)
    mocker.patch('spending_tracker.app.query_executor', new=query_executor_mock)
    response = app.test_client().put("/update", json=update_expense_data)
    assert response.status_code == 404
    assert response.json == {"error": "Expense doesn't exist"}


def test_delete_expense_happy_path(mocker):
    query_executor_mock = Mock(return_value=None)
    mocker.patch('spending_tracker.app.query_executor', new=query_executor_mock)
    response = app.test_client().delete("/delete/123")
    assert response.status_code == 200
    assert response.json == {}


def test_delete_expense_unsuccessful(mocker):
    query_executor_mock = Mock(side_effect=Exception("Expense not found."))
    mocker.patch('spending_tracker.app.query_executor', new=query_executor_mock)
    response = app.test_client().delete("/delete/123")
    assert response.status_code == 404
    assert response.json == {"error": "Expense not found."}
