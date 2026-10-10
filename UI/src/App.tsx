import React from 'react';

type WithSetPage = { setPage?: (page: string) => void };

const App = () => {
  return (
    <div>
      <h1>URL Sniffer App</h1>
      {/* The actual UI would be here */}
    </div>
  );
};

export const Landing = () => <div>Landing</div>;
export const Dashboard = ({ setPage }: WithSetPage) => <div>Dashboard</div>;
export const Scanner = ({ setPage }: WithSetPage) => <div>Scanner</div>;
export const Scanning = () => <div>Scanning</div>;
export const ResultPage = ({ setPage }: WithSetPage) => <div>ResultPage</div>;
export const HistoryPage = ({ setPage }: WithSetPage) => <div>HistoryPage</div>;
export const AnalyticsPage = ({ setPage }: WithSetPage) => <div>AnalyticsPage</div>;
export const ReportsPage = ({ setPage }: WithSetPage) => <div>ReportsPage</div>;
export const SettingsPage = ({ setPage }: WithSetPage) => <div>SettingsPage</div>;
export const NotificationsPage = ({ setPage }: WithSetPage) => <div>NotificationsPage</div>;
export const AdminPage = ({ setPage }: WithSetPage) => <div>AdminPage</div>;
export const ModelsPage = ({ setPage }: WithSetPage) => <div>ModelsPage</div>;
export const GenericAdmin = ({ setPage }: WithSetPage) => <div>GenericAdmin</div>;

export default App;