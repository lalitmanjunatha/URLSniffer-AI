import { useNavigate } from 'react-router-dom';
import { ReportsPage as ReportsComp } from '../App';

export default function ReportsPage() {
  const navigate = useNavigate();
  return <ReportsComp setPage={(page) => navigate(`/${page}`)} />;
}