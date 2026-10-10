import { useNavigate } from 'react-router-dom';
import { SettingsPage as SettingsComp } from '../App';

export default function SettingsPage() {
  const navigate = useNavigate();
  return <SettingsComp setPage={(page) => navigate(`/${page}`)} />;
}