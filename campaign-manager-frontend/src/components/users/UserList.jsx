 
import React, { useEffect, useState } from 'react';
import * as userService from '../../services/users';
import UserCard from './UserCard';
import AddUser from './AddUser';

const UserList = () => {
  const [users, setUsers] = useState([]);

  const load = async () => {
    const { data } = await userService.fetchUsers();
    setUsers(data);
  };

  useEffect(() => {
    load();
  }, []);

  const addUser = async (email, isAdmin) => {
    await userService.createUser(email, isAdmin);
    load();
  };

  const deleteUser = async (id) => {
    await userService.deleteUser(id);
    load();
  };

  return (
    <div>
      <AddUser onAdd={addUser} />
      {users.map((u) => (
        <UserCard key={u.id} user={u} onDelete={deleteUser} />
      ))}
    </div>
  );
};

export default UserList;

