import './Card.css';
export function Card({ title, children }) {
  return <div className="card">{title && <div className="card-title">{title}</div>}{children}</div>;
}
