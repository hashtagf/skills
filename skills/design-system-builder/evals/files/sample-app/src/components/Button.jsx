import './Button.css';
export function Button({ children, secondary, ...props }) {
  return <button className={secondary ? 'btn btn-secondary' : 'btn'} {...props}>{children}</button>;
}
