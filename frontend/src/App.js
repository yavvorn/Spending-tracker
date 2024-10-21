import React, { useEffect, useState } from "react";

export default function App() {
  return (
    <div className="app">
      <Logo />
      <Expenses />
      <Message />
    </div>
  );
}

function Expenses() {
  const [expenses, setExpenses] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://127.0.0.1:5000/expenses")
      .then((response) => response.json())
      .then((data) => {
        setExpenses(data);
        setLoading(false);
      })
      .catch((error) => console.error("Error fetching expenses:", error));
  }, []);

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="list">
      <ul>
        {expenses.map((expense) => (
          <Expense expense={expense} key={expense.id} />
        ))}
      </ul>
    </div>
  );
}

function Logo() {
  return <h1>Expenses trololo</h1>;
}

function Expense({ expense }) {
  return (
    <li>
      <span>
        {expense.expense} {expense.value}
      </span>
    </li>
  );
}

function Message() {
  return (
    <footer className="message">
      <em>You're a musty crusty spender</em>
    </footer>
  );
}
