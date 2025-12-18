import { useState, useEffect } from 'react';
import { X, FileText, Calendar, Users, User, CheckSquare } from 'lucide-react';
import { espacesPedagogiquesAPI } from '../../services/api';
import './CreateFormateur.css'; // Réutiliser les mêmes styles

const CreateTravail = ({ idEspace, onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    id_espace: idEspace,
    titre: '',
    description: '',
    type_travail: 'INDIVIDUEL',
    date_echeance: '',
    note_max: 20.0,
    etudiants_selectionnes: []
  });
  
  const [etudiants, setEtudiants] = useState([]);
  const [espaceInfo, setEspaceInfo] = useState(null);
  const [loading, setLoading] = useState(false);
  const [loadingEtudiants, setLoadingEtudiants] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [assignationType, setAssignationType] = useState('tous'); // 'tous' ou 'selectionnes'

  useEffect(() => {
    loadEtudiants();
    // Définir date d'échéance par défaut (dans 7 jours)
    const dateEcheance = new Date();
    dateEcheance.setDate(dateEcheance.getDate() + 7);
    setFormData(prev => ({
      ...prev,
      date_echeance: dateEcheance.toISOString().slice(0, 16) // Format datetime-local
    }));
  }, [idEspace]);

  const loadEtudiants = async () => {
    try {
      setLoadingEtudiants(true);
      const response = await espacesPedagogiquesAPI.listerEtudiantsEspace(idEspace);
      setEtudiants(response.data.etudiants);
      setEspaceInfo(response.data.espace);
    } catch (err) {
      console.error('Erreur chargement étudiants:', err);
      setError('Impossible de charger la liste des étudiants');
    } finally {
      setLoadingEtudiants(false);
    }
  };

  const handleChange = (e) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'number' ? parseFloat(value) : value
    }));
  };

  const handleAssignationTypeChange = (type) => {
    setAssignationType(type);
    if (type === 'tous') {
      setFormData(prev => ({
        ...prev,
        etudiants_selectionnes: []
      }));
    }
  };

  const handleEtudiantToggle = (idEtudiant) => {
    setFormData(prev => {
      const isSelected = prev.etudiants_selectionnes.includes(idEtudiant);
      const newSelection = isSelected
        ? prev.etudiants_selectionnes.filter(id => id !== idEtudiant)
        : [...prev.etudiants_selectionnes, idEtudiant];
      
      return {
        ...prev,
        etudiants_selectionnes: newSelection
      };
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);

    // Validation
    if (assignationType === 'selectionnes' && formData.etudiants_selectionnes.length === 0) {
      setError('Veuillez sélectionner au moins un étudiant');
      setLoading(false);
      return;
    }

    try {
      const dataToSend = {
        ...formData,
        etudiants_selectionnes: assignationType === 'tous' ? [] : formData.etudiants_selectionnes
      };

      const response = await espacesPedagogiquesAPI.creerTravail(dataToSend);
      
      const nbAssignations = response.data.travail.nb_assignations;
      const typeAssignation = assignationType === 'tous' ? 'toute la promotion' : `${nbAssignations} étudiant(s) sélectionné(s)`;
      
      setSuccess(`Travail créé et assigné à ${typeAssignation} avec succès !`);
      
      // Attendre 2 secondes puis fermer
      setTimeout(() => {
        onSuccess();
      }, 2000);
      
    } catch (err) {
      console.error('Erreur création travail:', err);
      setError(
        err.response?.data?.detail || 
        'Erreur lors de la création du travail'
      );
    } finally {
      setLoading(false);
    }
  };

  if (loadingEtudiants) {
    return (
      <div className="modal-overlay">
        <div className="modal-content">
          <div className="modal-header">
            <h2>Créer un travail</h2>
            <button className="close-btn" onClick={onClose}>
              <X size={20} />
            </button>
          </div>
          <div className="create-form">
            <div className="loading-select">Chargement des étudiants...</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="modal-overlay">
      <div className="modal-content" style={{ maxWidth: '700px' }}>
        <div className="modal-header">
          <div>
            <h2>Créer un travail</h2>
            {espaceInfo && (
              <p style={{ margin: '0.5rem 0 0 0', color: '#6b7280', fontSize: '0.875rem' }}>
                {espaceInfo.nom_matiere} - {espaceInfo.promotion}
              </p>
            )}
          </div>
          <button className="close-btn" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="create-form">
          <div className="form-group">
            <label htmlFor="titre">
              <FileText size={16} />
              Titre du travail
            </label>
            <input
              type="text"
              id="titre"
              name="titre"
              value={formData.titre}
              onChange={handleChange}
              required
              placeholder="Ex: Projet final, Exercice 1, TP Base de données..."
            />
          </div>

          <div className="form-group">
            <label htmlFor="description">
              <FileText size={16} />
              Description
            </label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              required
              placeholder="Décrivez les objectifs, consignes, livrables attendus..."
              rows="4"
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

          <div className="form-row">
            <div className="form-group">
              <label htmlFor="type_travail">
                <Users size={16} />
                Type de travail
              </label>
              <select
                id="type_travail"
                name="type_travail"
                value={formData.type_travail}
                onChange={handleChange}
                required
              >
                <option value="INDIVIDUEL">Individuel</option>
                <option value="COLLECTIF">Collectif</option>
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="date_echeance">
                <Calendar size={16} />
                Date d'échéance
              </label>
              <input
                type="datetime-local"
                id="date_echeance"
                name="date_echeance"
                value={formData.date_echeance}
                onChange={handleChange}
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="note_max">
              Note maximale
            </label>
            <input
              type="number"
              id="note_max"
              name="note_max"
              value={formData.note_max}
              onChange={handleChange}
              min="1"
              max="100"
              step="0.5"
              required
            />
          </div>

          {/* Sélection des étudiants */}
          <div className="form-group">
            <label>
              <User size={16} />
              Assignation
            </label>
            
            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem', cursor: 'pointer' }}>
                <input
                  type="radio"
                  name="assignationType"
                  checked={assignationType === 'tous'}
                  onChange={() => handleAssignationTypeChange('tous')}
                />
                <span>Assigner à toute la promotion ({etudiants.length} étudiants)</span>
              </label>
              
              <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                <input
                  type="radio"
                  name="assignationType"
                  checked={assignationType === 'selectionnes'}
                  onChange={() => handleAssignationTypeChange('selectionnes')}
                />
                <span>Assigner à des étudiants spécifiques</span>
              </label>
            </div>

            {assignationType === 'selectionnes' && (
              <div style={{ 
                border: '1px solid #d1d5db', 
                borderRadius: '6px', 
                padding: '1rem',
                maxHeight: '200px',
                overflowY: 'auto'
              }}>
                <div style={{ marginBottom: '0.5rem', fontSize: '0.875rem', color: '#6b7280' }}>
                  Sélectionnez les étudiants ({formData.etudiants_selectionnes.length} sélectionné(s)) :
                </div>
                {etudiants.map((etudiant) => (
                  <label 
                    key={etudiant.id_etudiant}
                    style={{ 
                      display: 'flex', 
                      alignItems: 'center', 
                      gap: '0.5rem', 
                      padding: '0.5rem',
                      cursor: 'pointer',
                      borderRadius: '4px',
                      backgroundColor: formData.etudiants_selectionnes.includes(etudiant.id_etudiant) ? '#f0f9ff' : 'transparent'
                    }}
                  >
                    <input
                      type="checkbox"
                      checked={formData.etudiants_selectionnes.includes(etudiant.id_etudiant)}
                      onChange={() => handleEtudiantToggle(etudiant.id_etudiant)}
                    />
                    <CheckSquare size={16} style={{ color: '#3b82f6' }} />
                    <span style={{ flex: 1 }}>
                      {etudiant.prenom} {etudiant.nom}
                      <span style={{ color: '#6b7280', fontSize: '0.75rem', marginLeft: '0.5rem' }}>
                        ({etudiant.matricule})
                      </span>
                    </span>
                  </label>
                ))}
              </div>
            )}
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
              {loading ? 'Création...' : 'Créer et assigner'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateTravail;