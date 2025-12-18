import './LoadingSpinner.css';

const LoadingSpinner = ({ size = 'medium', message = 'Chargement...' }) => {
  return (
    <div className="loading-container">
      <div className={`loading-spinner loading-spinner-${size}`}></div>
      <p className="loading-message">{message}</p>
    </div>
  );
};

export default LoadingSpinner;