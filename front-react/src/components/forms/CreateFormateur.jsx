import { useState } from 'react';
import { X, User, Mail, Briefcase } from 'lucide-react';
import { gestionComptesAPI } from '../../services/api';
import './CreateFormateur.css';

const CreateFormateur = ({ onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    email: '',
    nom: '',
    prenom: '',
    specialite: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await gestionComptesAPI.createFormateur(formData);
      setSuccess('Formateur créé avec succès ! Un email a été envoyé avec les identifiants.');
      
      // Attendre 2 secondes puis fermer
      setTimeout(() => {
        onSuccess();
      }, 2000);
      
    } catch (err) {
      console.error('Erreur création formateur:', err);
      setError(
        err.response?.data?.detail || 
        'Erreur lors de la création du formateur'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="modal-header">
          <h2>Créer un compte formateur</h2>
          <button className="close-btn" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="create-form">
          <div className="form-group">
            <label htmlFor="email">
              <Mail size={16} />
              Email
            </label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              placeholder="formateur@example.com"
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="nom">
                <User size={16} />
                Nom
              </label>
              <input
                type="text"
                id="nom"
                name="nom"
                value={formData.nom}
                onChange={handleChange}
                required
                placeholder="Dupont"
              />
            </div>

            <div className="form-group">
              <label htmlFor="prenom">
                <User size={16} />
                Prénom
              </label>
              <input
                type="text"
                id="prenom"
                name="prenom"
                value={formData.prenom}
                onChange={handleChange}
                required
                placeholder="Jean"
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="specialite">
              <Briefcase size={16} />
              Spécialité (optionnel)
            </label>
            <input
              type="text"
              id="specialite"
              name="specialite"
              value={formData.specialite}
              onChange={handleChange}
              placeholder="Développement Web, Base de données..."
            />
          </div>

          {error && (
            <div className="alert alert-error">
              {error}
            </div>
          )}

          {success && (
            <div className="alert alert-success">
              {success}
            </div>
          )}

          <div className="form-actions">
            <button 
              type="button" 
              className="btn btn-secondary"
              onClick={onClose}
              disabled={loading}
            >
              Annuler
            </button>
            <button 
              type="submit" 
              className="btn btn-primary"
              disabled={loading}
            >
              {loading ? 'Création...' : 'Créer le formateur'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateFormateur;