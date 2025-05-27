 
import React from 'react';

const LogEntry = ({ log }) => (
  <tr>
    <td>{log.created_at}</td>
    <td>{log.user_id}</td>
    <td>{log.action}</td>
    <td>{log.ip_address}</td>
  </tr>
);

export default LogEntry;

