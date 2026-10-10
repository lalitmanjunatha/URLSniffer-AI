import { useNavigate } from 'react-router-dom';
import { Dashboard } from '../App';

export default function DashboardPage() {
  const navigate = useNavigate();
  return <Dashboard setPage={(page) => navigate(`/${page}`)} />;
}