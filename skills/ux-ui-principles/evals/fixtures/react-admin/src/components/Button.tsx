export function Button({children,onClick,variant="primary"}:{children:React.ReactNode;onClick?:()=>void;variant?:"primary"|"danger"}){
  return <button className={variant==="danger"?"btn btn-danger":"btn"} onClick={onClick}>{children}</button>
}
