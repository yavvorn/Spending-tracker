import React, { useEffect, useState } from "react";

export default function App() {
  return (
    <div>
      {" "}
      <Expenses />
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
    <div>
      <h1>Expenses trololo</h1>
      <ul>
        {expenses.map((expense) => (
          <li key={expense.id}>
            {expense.expense}: ${expense.value}
          </li>
        ))}
      </ul>
    </div>
  );
}
