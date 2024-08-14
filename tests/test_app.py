import sys

from spending_tracker.app import app
import pytest

def test_home_route():
    response = app.test_client().get("/")
    assert response.status_code == 200


def test_get_expense_existing():
    expense_id = 2
    response = app.test_client().get(f"/expenses/{expense_id}")
    assert response.status_code == 200
    assert response.json == {"Food": 50}


def test_get_expense_non_existent():
    expense_id = sys.maxsize
    response = app.test_client().get(f"/expenses/{expense_id}")
    assert response.status_code == 404
    assert response.json == {"error": "Expense doesn't exist"}


def test_create_expense_happy_path():
    expense_data = {
        "expense": "Test Expense",
        "value": 69
    }
    response = app.test_client().post("/expenses", json=expense_data)
    assert response.status_code == 201
    assert response.json == {}


def test_create_expense_unsuccessful():
    bad_response = app.test_client().post("/expenses", json={})
    assert bad_response.status_code == 500
    assert bad_response.json == {"error": "Failed to create expense"}


def test_update_expense_happy_path():
    """
    QQ: I can't think of a way to make this work. The test would need an expense ID, so it must exist in the DB.
    I don't know the previously created Test_Expense's ID, so I can't build the test itself around it.
    Not entirely sure how to go about this. Initial idea was to do a sql query by name and value to extract
    the test_expense and update it from there. Another option I thought of is we could change the POST function in
    app.py to return an ID. The ID of the tests will be known and can be used in the POST tests and DELETE tests.
    """
    expense_data = {
        "id": 1,
        "expense": "Updated Expense",
        "value": 99
    }
    response = app.test_client().put("/update", json=expense_data)
    assert response.status_code == 204


def test_update_expense_unsuccessful():
    expense_data = {
        "id": sys.maxsize,
        "expense": "Nonexistent Expense",
        "value": 0
    }
    response = app.test_client().put("/update", json=expense_data)
    assert response.status_code == 404
    assert response.json == {"error": "Expense doesn't exist"}


def test_delete_expense_happy_path():
    """Same issue as the update situation. I'm not sure how to extract the ID of an existing expense within the DB"""
    expense_data = {
        "expense": "kur v guza",
        "value": 100
    }
    response = app.test_client().delete(f"/delete/{expense_data}")
    assert response.status_code == 200


def test_delete_expense_failure():
    non_existent_id = sys.maxsize
    response = app.test_client().delete(f"/delete/{non_existent_id}")
    assert response.status_code == 404
    assert response.json == {"error": "Cannot retrieve expense"}