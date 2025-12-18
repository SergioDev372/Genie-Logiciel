import { LogOut, User } from 'lucide-react';
import { clearAuthData, getAuthData } from '../../utils/auth';
import './Navbar.css';

const Navbar = ({ onLogout }) => {
  const authData = getAuthData();
  const user = authData?.user;

  const handleLogout = () => {
    clearAuthData();
    if (onLogout) {
      onLogout();
    }
  };

  const getRoleLabel = (role) => {
    switch (role) {
      case 'DE':
        return 'Directeur d\'Établissement';
      case 'FORMATEUR':
        return 'Formateur';
      case 'ETUDIANT':
        return 'Étudiant';
      default:
        return role;
    }
  };

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <h2>Génie Logiciel</h2>
      </div>
      
      <div className="navbar-user">
        <div className="user-info">
          <User size={20} />
          <div className="user-details">
            <span className="user-name">{user?.prenom} {user?.nom}</span>
            <span className="user-role">{getRoleLabel(user?.role)}</span>
          </div>
        </div>
        
        <button 
          className="logout-btn"
          onClick={handleLogout}
          title="Se déconnecter"
        >
          <LogOut size={20} />
        </button>
      </div>
    </nav>
  );
};

export default Navbar;