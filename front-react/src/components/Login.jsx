import { useState } from 'react'
import { authAPI } from '../services/api'
import './Login.css'

function Login({ onLoginSuccess }) {
  const [formData, setFormData] = useState({
    email: '',
    mot_de_passe: ''
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [rememberMe, setRememberMe] = useState(false)

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const response = await authAPI.login(formData.email, formData.mot_de_passe)
      const data = response.data

      if (data.statut === 'CHANGEMENT_MOT_DE_PASSE_REQUIS') {
        // Rediriger vers page de changement de mot de passe
        onLoginSuccess({ 
          requiresPasswordChange: true, 
          token: data.token,
          user: data.utilisateur 
        })
      } else {
        // Connexion normale
        onLoginSuccess({ 
          requiresPasswordChange: false, 
          token: data.token,
          user: data.utilisateur 
        })
      }
    } catch (err) {
      console.error('Erreur de connexion:', err)
      setError(
        err.response?.data?.detail?.message || 
        err.response?.data?.detail || 
        'Erreur de connexion'
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <div className="login-icon">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
              <circle cx="12" cy="7" r="4"></circle>
            </svg>
          </div>
          <h2>Bonjour !</h2>
          <p className="login-subtitle">Connectez-vous pour accéder à votre espace</p>
        </div>
        
        {error && <div className="error-message">{error}</div>}
        
        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="email">Adresse email</label>
            <div className="input-wrapper">
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
                placeholder="votre@email.com"
                className="modern-input"
              />
              <div className="input-icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path>
                  <polyline points="22,6 12,13 2,6"></polyline>
                </svg>
              </div>
            </div>
          </div>
          
          <div className="form-group">
            <label htmlFor="mot_de_passe">Mot de passe</label>
            <div className="input-wrapper">
              <input
                type={showPassword ? "text" : "password"}
                id="mot_de_passe"
                name="mot_de_passe"
                value={formData.mot_de_passe}
                onChange={handleChange}
                required
                placeholder="Entrez votre mot de passe"
                className="modern-input"
              />
              <button 
                type="button" 
                className="password-toggle"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? (
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
                    <line x1="1" y1="1" x2="23" y2="23"></line>
                  </svg>
                ) : (
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                    <circle cx="12" cy="12" r="3"></circle>
                  </svg>
                )}
              </button>
            </div>
          </div>
          
          <div className="form-options">
            <label className="checkbox-wrapper">
              <input
                type="checkbox"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
              />
              <span className="checkmark"></span>
              Se souvenir de moi
            </label>
            <a href="#" className="forgot-password">Mot de passe oublié?</a>
          </div>
          
          <button type="submit" disabled={loading} className="login-button">
            {loading ? (
              <span className="loading-spinner">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21 12a9 9 0 1 1-6.219-8.56"></path>
                </svg>
                Connexion en cours...
              </span>
            ) : (
              'Se connecter'
            )}
          </button>
        </form>
        
      </div>
    </div>
  )
}

export default Login
