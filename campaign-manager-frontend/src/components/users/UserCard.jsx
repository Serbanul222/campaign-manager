 
import React from 'react';

const UserCard = ({ user, onDelete }) => (
  <div className="border p-2 mb-2 flex justify-between">
    <span>{user.email}</span>
    <button onClick={() => onDelete(user.id)}>Delete</button>
  </div>
);

export default UserCard;

