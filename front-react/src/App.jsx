import { useState, useEffect } from 'react'
import Login from './components/Login'
import ChangePassword from './components/ChangePassword'
import DEDashboard from './components/dashboards/DEDashboard'
import FormateurDashboard from './components/dashboards/FormateurDashboard'
import EtudiantDashboard from './components/dashboards/EtudiantDashboard'
import { getAuthData, saveAuthData, clearAuthData } from './utils/auth'
import './App.css'

function App() {
  const [currentView, setCurrentView] = useState('loading')
  const [authData, setAuthData] = useState(null)

  useEffect(() => {
    // Vérifier si l'utilisateur est déjà connecté
    const existingAuth = getAuthData()
    if (existingAuth) {
      setAuthData(existingAuth)
      setCurrentView(getDashboardView(existingAuth.user.role))
    } else {
      setCurrentView('login')
    }
  }, [])

  const getDashboardView = (role) => {
    switch (role) {
      case 'DE':
        return 'deDashboard'
      case 'FORMATEUR':
        return 'formateurDashboard'
      case 'ETUDIANT':
        return 'etudiantDashboard'
      default:
        return 'login'
    }
  }

  const handleLoginSuccess = (data) => {
    setAuthData(data)
    
    if (data.requiresPasswordChange) {
      setCurrentView('changePassword')
    } else {
      // Sauvegarder les données d'authentification
      saveAuthData(data.token, data.user)
      
      // Rediriger vers le bon dashboard
      const dashboardView = getDashboardView(data.user.role)
      setCurrentView(dashboardView)
    }
  }

  const handlePasswordChangeSuccess = (data) => {
    console.log('Mot de passe changé avec succès:', data)
    
    // Sauvegarder les nouvelles données d'authentification
    saveAuthData(data.token, data.user)
    setAuthData(data)
    
    // Rediriger vers le bon dashboard
    const dashboardView = getDashboardView(data.user.role)
    setCurrentView(dashboardView)
  }

  const handleLogout = () => {
    clearAuthData()
    setAuthData(null)
    setCurrentView('login')
  }

  if (currentView === 'loading') {
    return (
      <div className="app loading">
        <div className="loading-spinner"></div>
        <p>Chargement...</p>
      </div>
    )
  }

  return (
    <div className="app">
      {currentView === 'login' && (
        <Login onLoginSuccess={handleLoginSuccess} />
      )}
      
      {currentView === 'changePassword' && authData && (
        <ChangePassword 
          token={authData.token} 
          onPasswordChangeSuccess={handlePasswordChangeSuccess}
        />
      )}

      {currentView === 'deDashboard' && (
        <DEDashboard onLogout={handleLogout} />
      )}

      {currentView === 'formateurDashboard' && (
        <FormateurDashboard onLogout={handleLogout} />
      )}

      {currentView === 'etudiantDashboard' && (
        <EtudiantDashboard onLogout={handleLogout} />
      )}
    </div>
  )
}

export default App
