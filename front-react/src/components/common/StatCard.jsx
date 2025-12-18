import './StatCard.css';

const StatCard = ({ title, value, icon: Icon, color = 'blue', subtitle }) => {
  return (
    <div className={`stat-card stat-card-${color}`}>
      <div className="stat-card-content">
        <div className="stat-card-header">
          <h3 className="stat-card-title">{title}</h3>
          {Icon && <Icon size={24} className="stat-card-icon" />}
        </div>
        <div className="stat-card-value">{value}</div>
        {subtitle && <div className="stat-card-subtitle">{subtitle}</div>}
      </div>
    </div>
  );
};

export default StatCard;