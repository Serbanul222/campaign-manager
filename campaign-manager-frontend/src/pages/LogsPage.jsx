// pages/LogsPage.jsx - Updated logs page using new components
import React from 'react';
import ActivityLogViewer from '../components/logs/ActivityLogViewer';

const LogsPage = () => {
  return (
    <div className="min-h-screen">
      <ActivityLogViewer />
    </div>
  );
};

export default LogsPage;
