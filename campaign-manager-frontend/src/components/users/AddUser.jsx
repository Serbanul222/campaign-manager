 
import React, { useState } from 'react';

const AddUser = ({ onAdd }) => {
  const [email, setEmail] = useState('');
  const [isAdmin, setIsAdmin] = useState(false);

  const submit = (e) => {
    e.preventDefault();
    if (!email) return;
    onAdd(email, isAdmin);
    setEmail('');
    setIsAdmin(false);
  };

  return (
    <form onSubmit={submit} className="mb-4">
      <input
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email"
        className="border p-1 mr-2"
      />
      <label className="mr-2">
        <input
          type="checkbox"
          checked={isAdmin}
          onChange={() => setIsAdmin((v) => !v)}
        />
        Admin
      </label>
      <button type="submit">Add</button>
    </form>
  );
};

export default AddUser;

