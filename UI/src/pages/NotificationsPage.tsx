import { useNavigate } from 'react-router-dom';
import { NotificationsPage as NotificationsComp } from '../App';

export default function NotificationsPage() {
  const navigate = useNavigate();
  return <NotificationsComp setPage={(page) => navigate(`/${page}`)} />;
}