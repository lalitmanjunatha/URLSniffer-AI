import { useNavigate } from 'react-router-dom';
import { HistoryPage as HistoryComp } from '../App';

export default function HistoryPage() {
  const navigate = useNavigate();
  return <HistoryComp setPage={(page) => navigate(`/${page}`)} />;
}