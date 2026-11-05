import {Button} from "../components/Button"
export default function Refunds(){
  // finance approves refunds here; amounts up to 500,000 THB
  return <div className="card"><h1>Refund requests</h1>
   <ul>{[{id:"R-1042",amount:"฿48,500",reason:"Damaged"}].map(r=><li key={r.id}>{r.id} {r.amount} {r.reason}
     <Button onClick={()=>fetch(`/api/refunds/${r.id}/approve`,{method:"POST"})}>Approve</Button>
     <Button variant="danger" onClick={()=>fetch(`/api/refunds/${r.id}/reject`,{method:"POST"})}>Reject</Button></li>)}</ul></div>
}
