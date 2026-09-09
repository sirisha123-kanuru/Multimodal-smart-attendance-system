function StatCard({ title, value, icon, color }) {
  return (
    <div className="stat-card">

      <div className="stat-top">

        <div
          className="stat-icon"
          style={{ backgroundColor: color }}
        >
          {icon}
        </div>

      </div>

      <h4>{title}</h4>

      <h2>{value}</h2>

    </div>
  );
}

export default StatCard;