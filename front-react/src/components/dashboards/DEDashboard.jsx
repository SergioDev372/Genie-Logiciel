import { useState, useEffect } from 'react';
import { Users, GraduationCap, Calendar, TrendingUp, UserPlus, Plus, BookOpen } from 'lucide-react';
import Navbar from '../common/Navbar';
import StatCard from '../common/StatCard';
import LoadingSpinner from '../common/LoadingSpinner';
import CreateFormateur from '../forms/CreateFormateur';
import CreateEtudiant from '../forms/CreateEtudiant';
import CreateEspacePedagogique from '../forms/CreateEspacePedagogique';
import { dashboardAPI } from '../../services/api';
import './DEDashboard.css';

const DEDashboard = ({ onLogout }) => {
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeModal, setActiveModal] = useState(null); // 'formateur' | 'etudiant' | 'espace' | null

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const response = await dashboardAPI.getDEDashboard();
      setDashboardData(response.data);
      setError(null);
    } catch (err) {
      console.error('Erreur chargement dashboard:', err);
      setError('Impossible de charger les données du dashboard');
    } finally {
      setLoading(false);
    }
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
            <h1>Dashboard Directeur d'Établissement</h1>
            <p>Vue d'ensemble de l'établissement</p>
          </div>
          
          <div className="dashboard-actions">
            <button 
              className="btn btn-primary"
              onClick={() => setActiveModal('formateur')}
            >
              <UserPlus size={20} />
              Créer Formateur
            </button>
            <button 
              className="btn btn-success"
              onClick={() => setActiveModal('etudiant')}
            >
              <Plus size={20} />
              Créer Étudiant
            </button>
            <button 
              className="btn btn-purple"
              onClick={() => setActiveModal('espace')}
            >
              <BookOpen size={20} />
              Créer Espace
            </button>
          </div>
        </div>

        {/* Statistiques */}
        <div className="stats-grid">
          <StatCard
            title="Formateurs"
            value={stats.total_formateurs || 0}
            icon={Users}
            color="blue"
          />
          <StatCard
            title="Étudiants"
            value={stats.total_etudiants || 0}
            icon={GraduationCap}
            color="green"
            subtitle={`${stats.etudiants_actifs || 0} actifs`}
          />
          <StatCard
            title="Promotions"
            value={stats.total_promotions || 0}
            icon={Calendar}
            color="purple"
          />
          <StatCard
            title="Formations"
            value={stats.total_formations || 0}
            icon={TrendingUp}
            color="yellow"
          />
        </div>

        {/* Promotions récentes */}
        <div className="dashboard-section">
          <h2>Promotions récentes</h2>
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Année académique</th>
                  <th>Libellé</th>
                  <th>Date début</th>
                  <th>Date fin</th>
                </tr>
              </thead>
              <tbody>
                {dashboardData?.promotions_recentes?.map((promo) => (
                  <tr key={promo.id_promotion}>
                    <td><strong>{promo.annee_academique}</strong></td>
                    <td>{promo.libelle}</td>
                    <td>{new Date(promo.date_debut).toLocaleDateString('fr-FR')}</td>
                    <td>{new Date(promo.date_fin).toLocaleDateString('fr-FR')}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Comptes récents */}
        <div className="dashboard-section">
          <h2>Comptes créés récemment</h2>
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Nom</th>
                  <th>Email</th>
                  <th>Rôle</th>
                  <th>Date création</th>
                  <th>Statut</th>
                </tr>
              </thead>
              <tbody>
                {dashboardData?.comptes_recents?.map((compte) => (
                  <tr key={compte.identifiant}>
                    <td>{compte.prenom} {compte.nom}</td>
                    <td>{compte.email}</td>
                    <td>
                      <span className={`badge badge-${compte.role.toLowerCase()}`}>
                        {compte.role}
                      </span>
                    </td>
                    <td>{new Date(compte.date_creation).toLocaleDateString('fr-FR')}</td>
                    <td>
                      <span className={`status-badge ${compte.actif ? 'active' : 'inactive'}`}>
                        {compte.actif ? 'Actif' : 'Inactif'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Modals */}
      {activeModal === 'formateur' && (
        <CreateFormateur
          onClose={() => setActiveModal(null)}
          onSuccess={handleCreateSuccess}
        />
      )}

      {activeModal === 'etudiant' && (
        <CreateEtudiant
          onClose={() => setActiveModal(null)}
          onSuccess={handleCreateSuccess}
        />
      )}

      {activeModal === 'espace' && (
        <CreateEspacePedagogique
          onClose={() => setActiveModal(null)}
          onSuccess={handleCreateSuccess}
        />
      )}
    </div>
  );
};

export default DEDashboard;