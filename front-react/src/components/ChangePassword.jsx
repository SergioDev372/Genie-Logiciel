import { useState } from 'react'
import { authAPI } from '../services/api'
import './ChangePassword.css'

function ChangePassword({ token, onPasswordChangeSuccess }) {
  const [formData, setFormData] = useState({
    token: token,
    nouveau_mot_de_passe: '',
    confirmation_mot_de_passe: ''
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

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

    // Validation côté client
    if (formData.nouveau_mot_de_passe !== formData.confirmation_mot_de_passe) {
      setError('Les mots de passe ne correspondent pas')
      setLoading(false)
      return
    }

    if (formData.nouveau_mot_de_passe.length < 6) {
      setError('Le mot de passe doit contenir au moins 6 caractères')
      setLoading(false)
      return
    }

    try {
      const response = await authAPI.changePassword(
        formData.token,
        formData.nouveau_mot_de_passe,
        formData.confirmation_mot_de_passe
      )
      const data = response.data
      
      // Notifier le composant parent
      onPasswordChangeSuccess({
        token: data.token,
        user: data.utilisateur
      })
    } catch (err) {
      console.error('Erreur changement mot de passe:', err)
      setError(
        err.response?.data?.detail || 
        'Erreur lors du changement de mot de passe'
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="change-password-container">
      <div className="change-password-card">
        <h2>Changement de Mot de Passe Obligatoire</h2>
        <p className="subtitle">
          Pour des raisons de sécurité, vous devez changer votre mot de passe temporaire.
        </p>
        
        {error && <div className="error-message">{error}</div>}
        
        <form onSubmit={handleSubmit} className="change-password-form">
          <div className="form-group">
            <label htmlFor="nouveau_mot_de_passe">Nouveau mot de passe</label>
            <input
              type="password"
              id="nouveau_mot_de_passe"
              name="nouveau_mot_de_passe"
              value={formData.nouveau_mot_de_passe}
              onChange={handleChange}
              required
              placeholder="Entrez votre nouveau mot de passe"
              minLength="6"
            />
          </div>
          
          <div className="form-group">
            <label htmlFor="confirmation_mot_de_passe">Confirmer le mot de passe</label>
            <input
              type="password"
              id="confirmation_mot_de_passe"
              name="confirmation_mot_de_passe"
              value={formData.confirmation_mot_de_passe}
              onChange={handleChange}
              required
              placeholder="Confirmez votre nouveau mot de passe"
              minLength="6"
            />
          </div>
          
          <button type="submit" disabled={loading} className="change-password-button">
            {loading ? 'Changement...' : 'Changer le mot de passe'}
          </button>
        </form>
        
        <div className="password-requirements">
          <h4>Exigences de mot de passe :</h4>
          <ul>
            <li>Au moins 6 caractères</li>
            <li>Doit correspondre à la confirmation</li>
            <li>Évitez les mots de passe trop simples</li>
          </ul>
        </div>
      </div>
    </div>
  )
}

export default ChangePassword
