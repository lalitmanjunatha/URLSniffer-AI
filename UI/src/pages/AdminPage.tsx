import { useNavigate } from 'react-router-dom';
import { AdminPage as AdminComp } from '../App';

export default function AdminPage() {
  const navigate = useNavigate();
  return <AdminComp setPage={(page) => navigate(`/${page}`)} />;
}