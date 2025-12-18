import { useState, useEffect } from 'react';
import { X, User, Mail, Calendar } from 'lucide-react';
import { gestionComptesAPI } from '../../services/api';
import './CreateFormateur.css'; // Réutiliser les mêmes styles

const CreateEtudiant = ({ onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    email: '',
    nom: '',
    prenom: '',
    annee_academique: ''
  });
  const [anneesDisponibles, setAnneesDisponibles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [loadingAnnees, setLoadingAnnees] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  useEffect(() => {
    loadAnneesAcademiques();
  }, []);

  const loadAnneesAcademiques = async () => {
    try {
      const response = await gestionComptesAPI.getAnneesAcademiques();
      setAnneesDisponibles(response.data.annees_disponibles);
    } catch (err) {
      console.error('Erreur chargement années:', err);
      setError('Impossible de charger les années académiques');
    } finally {
      setLoadingAnnees(false);
    }
  };

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
      const response = await gestionComptesAPI.createEtudiant(formData);
      setSuccess('Étudiant créé avec succès ! Un email a été envoyé avec les identifiants.');
      
      // Attendre 2 secondes puis fermer
      setTimeout(() => {
        onSuccess();
      }, 2000);
      
    } catch (err) {
      console.error('Erreur création étudiant:', err);
      setError(
        err.response?.data?.detail || 
        'Erreur lors de la création de l\'étudiant'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="modal-header">
          <h2>Créer un compte étudiant</h2>
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
              placeholder="etudiant@example.com"
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
                placeholder="Martin"
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
                placeholder="Sophie"
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="annee_academique">
              <Calendar size={16} />
              Année académique
            </label>
            {loadingAnnees ? (
              <div className="loading-select">Chargement des années...</div>
            ) : (
              <select
                id="annee_academique"
                name="annee_academique"
                value={formData.annee_academique}
                onChange={handleChange}
                required
              >
                <option value="">Sélectionner une année</option>
                {anneesDisponibles.map((annee) => (
                  <option key={annee} value={annee}>
                    {annee}
                  </option>
                ))}
              </select>
            )}
            <small className="form-help">
              La promotion sera créée automatiquement si elle n'existe pas
            </small>
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
              disabled={loading || loadingAnnees}
            >
              {loading ? 'Création...' : 'Créer l\'étudiant'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateEtudiant;