import { Button } from '../components/Button';
import { PrimaryButton } from '../components/PrimaryButton';
import { Card } from '../components/Card';
export function Dashboard() {
  return (
    <div className="container">
      <h1 style={{ color: '#1f2937' }}>Dashboard</h1>
      <p style={{ color: '#666', marginBottom: 7 }}>Welcome back</p>
      <Card title="Shipments">
        <span style={{ fontSize: 13, color: '#059669' }}>+12% this week</span>
        <Button>View all</Button>
        <PrimaryButton>Create shipment</PrimaryButton>
      </Card>
      <div style={{ padding: '7px 11px', background: '#fef3c7', color: '#92400e', borderRadius: 4, fontSize: 13 }}>
        3 shipments delayed
      </div>
    </div>
  );
}
