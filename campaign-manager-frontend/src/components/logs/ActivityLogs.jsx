 
import React, { useEffect, useState } from 'react';
import * as logService from '../../services/logs';
import LogEntry from './LogEntry';
import LogsFilter from './LogsFilter';

const ActivityLogs = () => {
  const [logs, setLogs] = useState([]);

  const load = async () => {
    const { data } = await logService.fetchLogs();
    setLogs(data);
  };

  useEffect(() => {
    load();
  }, []);

  return (
    <div>
      <LogsFilter onRefresh={load} />
      <table>
        <thead>
          <tr>
            <th>Time</th>
            <th>User</th>
            <th>Action</th>
            <th>IP</th>
          </tr>
        </thead>
        <tbody>
          {logs.map((log) => (
            <LogEntry key={log.id} log={log} />
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default ActivityLogs;

