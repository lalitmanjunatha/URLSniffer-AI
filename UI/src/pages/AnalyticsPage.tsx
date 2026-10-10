import { useNavigate } from 'react-router-dom';
import { AnalyticsPage as AnalyticsComp } from '../App';

export default function AnalyticsPage() {
  const navigate = useNavigate();
  return <AnalyticsComp setPage={(page) => navigate(`/${page}`)} />;
}