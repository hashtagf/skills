export function DataTable({rows,columns}:{rows:any[];columns:{key:string;label:string}[]}){
  // no loading, empty or error handling yet
  return <table><thead><tr>{columns.map(c=><th key={c.key}>{c.label}</th>)}</tr></thead>
  <tbody>{rows.map((r,i)=><tr key={i}>{columns.map(c=><td key={c.key}>{r[c.key]}</td>)}</tr>)}</tbody></table>
}
