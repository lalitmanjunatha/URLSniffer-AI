import { useNavigate } from 'react-router-dom';
import { ResultPage } from '../App';

export default function ScanResultPage() {
  const navigate = useNavigate();
  return <ResultPage setPage={(page) => navigate(`/${page}`)} />;
}