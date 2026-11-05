export default function Settings(){
  // 31 settings in one long list: profile, password, 2FA, API keys, webhooks, billing, invoices, team, roles, notifications (email/sms/push x 6 events), language, timezone, delete workspace
  return <form className="card">{Array.from({length:31}).map((_,i)=><label key={i}>Setting {i+1}<input/></label>)}<button className="btn">Save</button></form>
}
