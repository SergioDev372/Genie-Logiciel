import { useState, useEffect } from 'react';
import { X, BookOpen, Users, GraduationCap, User } from 'lucide-react';
import { gestionComptesAPI, espacesPedagogiquesAPI } from '../../services/api';
import './CreateFormateur.css'; // Réutiliser les mêmes styles

const CreateEspacePedagogique = ({ onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    id_formation: '',
    id_promotion: '',
    id_formateur: '',
    nom_matiere: '',
    description: ''
  });
  
  const [formations, setFormations] = useState([]);
  const [promotions, setPromotions] = useState([]);
  const [formateurs, setFormateurs] = useState([]);
  
  const [loading, setLoading] = useState(false);
  const [loadingData, setLoadingData] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  useEffect(() => {
    loadFormData();
  }, []);

  const loadFormData = async () => {
    try {
      setLoadingData(true);
      const [formationsRes, promotionsRes, formateursRes] = await Promise.all([
        gestionComptesAPI.getFormations(),
        gestionComptesAPI.getPromotions(),
        gestionComptesAPI.getFormateurs()
      ]);
      
      setFormations(formationsRes.data.formations);
      setPromotions(promotionsRes.data.promotions);
      setFormateurs(formateursRes.data.formateurs);
    } catch (err) {
      console.error('Erreur chargement données:', err);
      setError('Impossible de charger les données nécessaires');
    } finally {
      setLoadingData(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Auto-générer le nom de la matière basé sur la formation
    if (name === 'id_formation') {
      const formation = formations.find(f => f.id_formation === value);
      if (formation) {
        setFormData(prev => ({
          ...prev,
          nom_matiere: formation.nom_formation
        }));
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      const response = await espacesPedagogiquesAPI.creerEspace(formData);
      setSuccess('Espace pédagogique créé avec succès !');
      
      // Attendre 2 secondes puis fermer
      setTimeout(() => {
        onSuccess();
      }, 2000);
      
    } catch (err) {
      console.error('Erreur création espace:', err);
      setError(
        err.response?.data?.detail || 
        'Erreur lors de la création de l\'espace pédagogique'
      );
    } finally {
      setLoading(false);
    }
  };

  if (loadingData) {
    return (
      <div className="modal-overlay">
        <div className="modal-content">
          <div className="modal-header">
            <h2>Créer un espace pédagogique</h2>
            <button className="close-btn" onClick={onClose}>
              <X size={20} />
            </button>
          </div>
          <div className="create-form">
            <div className="loading-select">Chargement des données...</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="modal-header">
          <h2>Créer un espace pédagogique</h2>
          <button className="close-btn" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="create-form">
          <div className="form-group">
            <label htmlFor="id_formation">
              <BookOpen size={16} />
              Formation (Matière)
            </label>
            <select
              id="id_formation"
              name="id_formation"
              value={formData.id_formation}
              onChange={handleChange}
              required
            >
              <option value="">Sélectionner une formation</option>
              {formations.map((formation) => (
                <option key={formation.id_formation} value={formation.id_formation}>
                  {formation.nom_formation}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="nom_matiere">
              <BookOpen size={16} />
              Nom de la matière
            </label>
            <input
              type="text"
              id="nom_matiere"
              name="nom_matiere"
              value={formData.nom_matiere}
              onChange={handleChange}
              required
              placeholder="Ex: Développement Web Avancé"
            />
            <small className="form-help">
              Personnalisez le nom si nécessaire (auto-rempli depuis la formation)
            </small>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="id_promotion">
                <GraduationCap size={16} />
                Promotion
              </label>
              <select
                id="id_promotion"
                name="id_promotion"
                value={formData.id_promotion}
                onChange={handleChange}
                required
              >
                <option value="">Sélectionner une promotion</option>
                {promotions.map((promotion) => (
                  <option key={promotion.id_promotion} value={promotion.id_promotion}>
                    {promotion.libelle}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="id_formateur">
                <User size={16} />
                Formateur
              </label>
              <select
                id="id_formateur"
                name="id_formateur"
                value={formData.id_formateur}
                onChange={handleChange}
                required
              >
                <option value="">Sélectionner un formateur</option>
                {formateurs.map((formateur) => (
                  <option key={formateur.id_formateur} value={formateur.id_formateur}>
                    {formateur.prenom} {formateur.nom} 
                    {formateur.specialite && ` (${formateur.specialite})`}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="description">
              <BookOpen size={16} />
              Description (optionnel)
            </label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              placeholder="Description du cours, objectifs, prérequis..."
              rows="3"
              style={{
                width: '100%',
                padding: '0.75rem',
                border: '1px solid #d1d5db',
                borderRadius: '6px',
                fontSize: '0.875rem',
                resize: 'vertical'
              }}
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
              {loading ? 'Création...' : 'Créer l\'espace'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateEspacePedagogique;