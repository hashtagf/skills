import {DataTable} from "../components/DataTable"
export default function Orders(){
  const [rows,setRows]=useState<any[]>([])
  useEffect(()=>{fetch("/api/orders").then(r=>r.json()).then(setRows)},[])
  return <div className="card"><h1>Orders</h1><DataTable rows={rows} columns={[{key:"id",label:"ID"},{key:"customer",label:"Customer"},{key:"total",label:"Total"},{key:"status",label:"Status"}]}/></div>
}
