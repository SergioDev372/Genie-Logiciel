import { useState, useEffect } from 'react';
import { BookOpen, Users, FileText, CheckCircle, Plus } from 'lucide-react';
import Navbar from '../common/Navbar';
import StatCard from '../common/StatCard';
import LoadingSpinner from '../common/LoadingSpinner';
import CreateTravail from '../forms/CreateTravail';
import { dashboardAPI } from '../../services/api';
import './FormateurDashboard.css';

const FormateurDashboard = ({ onLogout }) => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeModal, setActiveModal] = useState(null); // { type: 'travail', idEspace: 'xxx' } | null

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const response = await dashboardAPI.getFormateurDashboard();
      setDashboardData(response.data);
      setError(null);
    } catch (err) {
      console.error('Erreur chargement dashboard:', err);
      setError('Impossible de charger les données du dashboard');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTravail = (idEspace) => {
    setActiveModal({ type: 'travail', idEspace });
  };

  const handleCreateSuccess = () => {
    setActiveModal(null);
    loadDashboardData(); // Recharger les données
  };

  if (loading) {
    return (
      <div className="dashboard-container">
        <Navbar onLogout={onLogout} />
        <LoadingSpinner message="Chargement du dashboard..." />
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-container">
        <Navbar onLogout={onLogout} />
        <div className="error-message">{error}</div>
      </div>
    );
  }

  const stats = dashboardData?.statistiques || {};

  return (
    <div className="dashboard-container">
      <Navbar onLogout={onLogout} />
      
      <div className="dashboard-content">
        <div className="dashboard-header">
          <div>
            <h1>Dashboard Formateur</h1>
            <p>Gestion de vos espaces pédagogiques</p>
          </div>
        </div>

        {/* Statistiques */}
        <div className="stats-grid">
          <StatCard
            title="Espaces pédagogiques"
            value={stats.total_espaces || 0}
            icon={BookOpen}
            color="blue"
          />
          <StatCard
            title="Travaux créés"
            value={stats.total_travaux || 0}
            icon={FileText}
            color="green"
          />
          <StatCard
            title="Étudiants"
            value={stats.total_etudiants || 0}
            icon={Users}
            color="purple"
          />
          <StatCard
            title="À corriger"
            value={stats.assignations_a_corriger || 0}
            icon={CheckCircle}
            color="yellow"
          />
        </div>

        {/* Mes espaces pédagogiques */}
        <div className="dashboard-section">
          <h2>Mes espaces pédagogiques</h2>
          <div className="espaces-grid">
            {dashboardData?.espaces_pedagogiques?.map((espace) => (
              <div key={espace.id_espace} className="espace-card">
                <div className="espace-header">
                  <h3>{espace.nom_matiere}</h3>
                  <button 
                    className="btn-create-travail"
                    onClick={() => handleCreateTravail(espace.id_espace)}
                    title="Créer un travail"
                  >
                    <Plus size={16} />
                  </button>
                </div>
                <p className="espace-description">{espace.description}</p>
                <div className="espace-info">
                  <span className="espace-promotion">{espace.promotion}</span>
                  <span className="espace-stats">
                    {espace.nombre_travaux} travaux • {espace.nombre_etudiants} étudiants
                  </span>
                </div>
                {espace.code_acces && (
                  <div className="espace-code">
                    Code d'accès: <strong>{espace.code_acces}</strong>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Travaux récents */}
        <div className="dashboard-section">
          <h2>Travaux récents</h2>
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Titre</th>
                  <th>Type</th>
                  <th>Espace</th>
                  <th>Échéance</th>
                  <th>Créé le</th>
                </tr>
              </thead>
              <tbody>
                {dashboardData?.travaux_recents?.map((travail) => (
                  <tr key={travail.id_travail}>
                    <td><strong>{travail.titre}</strong></td>
                    <td>
                      <span className={`badge badge-${travail.type_travail.toLowerCase()}`}>
                        {travail.type_travail}
                      </span>
                    </td>
                    <td>{travail.espace}</td>
                    <td>{new Date(travail.date_echeance).toLocaleDateString('fr-FR')}</td>
                    <td>{new Date(travail.date_creation).toLocaleDateString('fr-FR')}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Modal création travail */}
      {activeModal?.type === 'travail' && (
        <CreateTravail
          idEspace={activeModal.idEspace}
          onClose={() => setActiveModal(null)}
          onSuccess={handleCreateSuccess}
        />
      )}
    </div>
  );
};

export default FormateurDashboard;