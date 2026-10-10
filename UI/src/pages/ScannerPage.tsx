import { useNavigate } from 'react-router-dom';
import { Scanner } from '../App';

export default function ScannerPage() {
  const navigate = useNavigate();
  return <Scanner setPage={(page) => navigate(`/${page}`)} />;
}