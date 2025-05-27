import React from 'react';
import { useSearchParams } from 'react-router-dom';
import SetPassword from '../components/auth/SetPassword.jsx';

const SetPasswordPage = () => {
  const [params] = useSearchParams();
  const token = params.get('token');
  return <SetPassword token={token} />;
};

export default SetPasswordPage;
