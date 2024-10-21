import sys

import pytest
from unittest.mock import Mock
from spending_tracker.app import app


def test_home_route(mocker):
    response_data = [(13, "Food", 150)]
    query_executor_mock = Mock(return_value=response_data)
    mocker.patch('spending_tracker.app.query_executor', new=query_executor_mock)
    response = app.test_client().get("/expenses")
    expected_response = [{"id": 13, "expense": "Food", "value": 150}]
    assert response.status_code == 200
    assert response.json == expected_response


def test_get_expense_happy_path(mocker):
    response_data = [(7, "Food", 75)]
    query_executor_mock = Mock(return_value=response_data)
    mocker.patch('spending_tracker.app.query_executor', new=query_executor_mock)
    response = app.test_client().get("/expenses/7")
    expected_response = {"id": 7, "expense": "Food", "value": 75.0}
    assert response.status_code == 200
    assert response.json == expected_response


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


def test_create_expense_failure():
    new_expense_data = {"expense": "Food", "value": -100}
    response = app.test_client().post("/expenses", json=new_expense_data)
    assert response.status_code == 400
    assert response.json == {"error": "Invalid payload"}

def test_update_expense_happy_path(mocker):
    update_expense_data = {"id": 123, "expense": "Groceries", "value": 150}
    query_executor_mock = Mock(return_value=True)  # Simulating a successful update
    mocker.patch('spending_tracker.app.query_executor', new=query_executor_mock)
    response = app.test_client().put(f"/expenses/{update_expense_data['id']}", json=update_expense_data)
    assert response.status_code == 204


def test_update_expense_unsuccessful():
    update_expense_data = {"id": 123, "expense": {"Groceries": "milk"}, "value": 150}
    response = app.test_client().put(f"/expenses/{update_expense_data['id']}", json=update_expense_data)
    assert response.status_code == 400
    assert response.json == {"error": "Invalid payload"}


def test_delete_expense_happy_path(mocker):
    expense_to_add_and_delete = {"id": 123, "expense": "Groceries", "value": 150}
    query_executor_mock = Mock(return_value=None)
    mocker.patch('spending_tracker.app.query_executor', new=query_executor_mock)
    response = app.test_client().delete(f"/expenses/{expense_to_add_and_delete['id']}")
    assert response.status_code == 200
    assert response.json == {}


def test_delete_expense_unsuccessful(mocker):
    query_executor_mock = Mock(side_effect=Exception("Expense not found."))
    mocker.patch('spending_tracker.app.query_executor', new=query_executor_mock)
    expense_to_delete = sys.maxsize
    response = app.test_client().delete(f"/expenses/{expense_to_delete}")
    assert response.status_code == 404
    assert response.json == {"error": "Expense not found."}
