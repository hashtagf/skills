// Added by another team — near-duplicate of Button
export function PrimaryButton({ children, onClick }) {
  return (
    <button
      onClick={onClick}
      style={{ background: '#2564ec', color: '#fff', padding: '10px 15px', borderRadius: 5, border: 0, fontSize: 15, fontWeight: 600 }}
    >
      {children}
    </button>
  );
}
