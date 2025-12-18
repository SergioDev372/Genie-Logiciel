import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000';

// Instance axios avec configuration de base
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Intercepteur pour ajouter le token JWT automatiquement
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Intercepteur pour gérer les erreurs d'authentification
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expiré ou invalide
      localStorage.removeItem('authToken');
      localStorage.removeItem('userData');
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

// ==================== AUTH ====================
export const authAPI = {
  login: (email, mot_de_passe) => 
    api.post('/api/auth/login', { email, mot_de_passe }),
  
  changePassword: (token, nouveau_mot_de_passe, confirmation_mot_de_passe) =>
    api.post('/api/auth/changer-mot-de-passe', {
      token,
      nouveau_mot_de_passe,
      confirmation_mot_de_passe
    }),
};

// ==================== DASHBOARD ====================
export const dashboardAPI = {
  getDashboard: () => api.get('/api/dashboard/'),
  getDEDashboard: () => api.get('/api/dashboard/de'),
  getFormateurDashboard: () => api.get('/api/dashboard/formateur'),
  getEtudiantDashboard: () => api.get('/api/dashboard/etudiant'),
};

// ==================== GESTION COMPTES ====================
export const gestionComptesAPI = {
  // Années académiques
  getAnneesAcademiques: () => api.get('/api/gestion-comptes/annees-academiques'),
  
  // Promotions
  getPromotions: () => api.get('/api/gestion-comptes/promotions'),
  
  // Formations
  getFormations: () => api.get('/api/gestion-comptes/formations'),
  
  // Formateurs
  getFormateurs: () => api.get('/api/gestion-comptes/formateurs'),
  
  // Création formateur
  createFormateur: (data) => api.post('/api/gestion-comptes/creer-formateur', data),
  
  // Création étudiant
  createEtudiant: (data) => api.post('/api/gestion-comptes/creer-etudiant', data),
};

// ==================== ESPACES PEDAGOGIQUES ====================
export const espacesPedagogiquesAPI = {
  // DE - Gestion espaces
  creerEspace: (data) => api.post('/api/espaces-pedagogiques/creer', data),
  listerEspaces: () => api.get('/api/espaces-pedagogiques/liste'),
  
  // Formateur - Mes espaces
  mesEspaces: () => api.get('/api/espaces-pedagogiques/mes-espaces'),
  listerEtudiantsEspace: (idEspace) => api.get(`/api/espaces-pedagogiques/espace/${idEspace}/etudiants`),
  creerTravail: (data) => api.post('/api/espaces-pedagogiques/travaux/creer', data),
  
  // Étudiant - Mes cours
  mesCours: () => api.get('/api/espaces-pedagogiques/mes-cours'),
  mesTravaux: () => api.get('/api/espaces-pedagogiques/travaux/mes-travaux'),
};

export default api;