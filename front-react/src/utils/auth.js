// Utilitaires pour la gestion de l'authentification

export const saveAuthData = (token, userData) => {
  localStorage.setItem('authToken', token);
  localStorage.setItem('userData', JSON.stringify(userData));
};

export const getAuthData = () => {
  const token = localStorage.getItem('authToken');
  const userData = localStorage.getItem('userData');
  
  if (token && userData) {
    return {
      token,
      user: JSON.parse(userData)
    };
  }
  
  return null;
};

export const clearAuthData = () => {
  localStorage.removeItem('authToken');
  localStorage.removeItem('userData');
};

export const isAuthenticated = () => {
  return !!localStorage.getItem('authToken');
};

export const getUserRole = () => {
  const authData = getAuthData();
  return authData?.user?.role || null;
};

export const redirectToDashboard = (role) => {
  switch (role) {
    case 'DE':
      return '/dashboard/de';
    case 'FORMATEUR':
      return '/dashboard/formateur';
    case 'ETUDIANT':
      return '/dashboard/etudiant';
    default:
      return '/';
  }
};