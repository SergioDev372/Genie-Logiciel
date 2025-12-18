import { useState, useEffect } from 'react';
import { BookOpen, FileText, Award, Clock } from 'lucide-react';
import Navbar from '../common/Navbar';
import StatCard from '../common/StatCard';
import LoadingSpinner from '../common/LoadingSpinner';
import { dashboardAPI } from '../../services/api';
import './EtudiantDashboard.css';

const EtudiantDashboard = ({ onLogout }) => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const response = await dashboardAPI.getEtudiantDashboard();
      setDashboardData(response.data);
      setError(null);
    } catch (err) {
      console.error('Erreur chargement dashboard:', err);
      setError('Impossible de charger les données du dashboard');
    } finally {
      setLoading(false);
    }
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
  const promotion = dashboardData?.promotion || {};

  return (
    <div className="dashboard-container">
      <Navbar onLogout={onLogout} />
      
      <div className="dashboard-content">
        <div className="dashboard-header">
          <div>
            <h1>Dashboard Étudiant</h1>
            <p>{promotion.libelle} - {promotion.formation}</p>
          </div>
          
          <div className="student-info">
            <div className="matricule">
              Matricule: <strong>{dashboardData?.utilisateur?.matricule}</strong>
            </div>
            {stats.moyenne_generale && (
              <div className="moyenne">
                Moyenne: <strong>{stats.moyenne_generale}/20</strong>
              </div>
            )}
          </div>
        </div>

        {/* Statistiques */}
        <div className="stats-grid">
          <StatCard
            title="Travaux total"
            value={stats.total_travaux || 0}
            icon={FileText}
            color="blue"
          />
          <StatCard
            title="Terminés"
            value={stats.travaux_termines || 0}
            icon={Award}
            color="green"
          />
          <StatCard
            title="En cours"
            value={stats.travaux_en_cours || 0}
            icon={Clock}
            color="yellow"
          />
          <StatCard
            title="En retard"
            value={stats.travaux_en_retard || 0}
            icon={Clock}
            color="red"
          />
        </div>

        {/* Mes espaces pédagogiques */}
        <div className="dashboard-section">
          <h2>Mes cours</h2>
          <div className="cours-grid">
            {dashboardData?.espaces_pedagogiques?.map((espace) => (
              <div key={espace.id_espace} className="cours-card">
                <h3>{espace.nom_matiere}</h3>
                <p className="cours-description">{espace.description}</p>
                <div className="cours-formateur">
                  Formateur: <strong>{espace.formateur}</strong>
                </div>
                {espace.code_acces && (
                  <div className="cours-code">
                    Code: <strong>{espace.code_acces}</strong>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Mes travaux */}
        <div className="dashboard-section">
          <h2>Mes travaux récents</h2>
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Titre</th>
                  <th>Cours</th>
                  <th>Type</th>
                  <th>Échéance</th>
                  <th>Statut</th>
                  <th>Note</th>
                </tr>
              </thead>
              <tbody>
                {dashboardData?.travaux?.map((travail) => (
                  <tr key={travail.id_assignation} className={travail.en_retard ? 'row-retard' : ''}>
                    <td><strong>{travail.titre}</strong></td>
                    <td>{travail.espace}</td>
                    <td>
                      <span className={`badge badge-${travail.type_travail.toLowerCase()}`}>
                        {travail.type_travail}
                      </span>
                    </td>
                    <td>
                      {new Date(travail.date_echeance).toLocaleDateString('fr-FR')}
                      {travail.en_retard && <span className="retard-indicator">⚠️</span>}
                    </td>
                    <td>
                      <span className={`status-badge status-${travail.statut.toLowerCase()}`}>
                        {travail.statut.replace('_', ' ')}
                      </span>
                    </td>
                    <td>
                      {travail.note !== null ? (
                        <strong>{travail.note}/{travail.note_max}</strong>
                      ) : (
                        <span className="no-note">-</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EtudiantDashboard;