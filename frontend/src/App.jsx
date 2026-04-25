import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  Activity, 
  Settings, 
  Play, 
  Square, 
  TrendingUp, 
  DollarSign, 
  List, 
  Key,
  Database
} from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

function App() {
  const [status, setStatus] = useState({
    bot_active: false,
    dhan_connected: false,
    live_price: 0,
    trades_today: 0,
    max_trades: 3
  });
  
  const [positions, setPositions] = useState([]);
  const [trades, setTrades] = useState([]);
  const [configKeys, setConfigKeys] = useState({ client_id: '', access_token: '' });

  // Fetch initial data
  useEffect(() => {
    fetchStatus();
    fetchPositions();
    fetchTrades();
    
    // Poll for live status every 2 seconds
    const interval = setInterval(fetchStatus, 2000);
    return () => clearInterval(interval);
  }, []);

  const fetchStatus = async () => {
    try {
      const res = await axios.get(`${API_BASE_URL}/status`);
      setStatus(res.data);
    } catch (error) {
      console.error("Error fetching status", error);
    }
  };

  const fetchPositions = async () => {
    try {
      const res = await axios.get(`${API_BASE_URL}/positions`);
      setPositions(res.data);
    } catch (error) {
      console.error("Error fetching positions", error);
    }
  };
  
  const fetchTrades = async () => {
    try {
      const res = await axios.get(`${API_BASE_URL}/trades`);
      setTrades(res.data);
    } catch (error) {
      console.error("Error fetching trades", error);
    }
  };

  const toggleBot = async () => {
    try {
      await axios.post(`${API_BASE_URL}/toggle_bot`);
      fetchStatus();
    } catch (error) {
      console.error("Error toggling bot", error);
    }
  };

  const saveConfig = async () => {
    try {
      await axios.post(`${API_BASE_URL}/config/keys`, null, {
        params: configKeys
      });
      alert('Configuration Saved & Reconnecting DhanHQ...');
      fetchStatus();
    } catch (error) {
      console.error("Error saving config", error);
    }
  };

  return (
    <>
      <header className="app-header">
        <div className="logo-wrapper">
          <div className="logo-icon">
            <Activity size={24} />
          </div>
          <div>
            <h1>Antigravity</h1>
            <p className="text-sm">Silver Autonomous Scalping</p>
          </div>
        </div>
        
        <div className="flex gap-4 items-center">
          <div className="status-indicator">
            <span className={`status-dot ${status.dhan_connected ? 'active' : 'inactive'}`}></span>
            DhanHQ {status.dhan_connected ? 'Connected' : 'Disconnected'}
          </div>
        </div>
      </header>

      <main className="container">
        <div className="grid grid-cols-3">
          
          {/* Main Control Panel */}
          <div className="card" style={{ gridColumn: 'span 2' }}>
            <div className="card-header">
              <h2 className="card-title"><Settings /> Control Panel & Metrics</h2>
            </div>
            
            <div className="flex justify-between items-center" style={{ marginBottom: '2rem' }}>
              <div className="metric">
                <span className="metric-label">Live Silver</span>
                <span className={`metric-value ${status.bot_active ? 'text-primary' : ''}`}>
                  {status.live_price > 0 ? status.live_price.toFixed(2) : "---.--"}
                </span>
              </div>
              
              <div className="metric">
                <span className="metric-label">Daily Trades</span>
                <span className="metric-value">
                  <span className={status.trades_today >= status.max_trades ? 'text-warning' : 'text-success'}>
                    {status.trades_today}
                  </span>
                  <span className="text-muted"> / {status.max_trades}</span>
                </span>
              </div>
              
              <div className="flex items-center gap-4">
                <div className="flex flex-col items-end mr-4">
                  <span className="text-sm text-secondary font-medium mb-1">Algorithmic Engine</span>
                  <span className={`text-sm ${status.bot_active ? 'text-success' : 'text-muted'}`}>
                    {status.bot_active ? 'RUNNING' : 'STOPPED'}
                  </span>
                </div>
                <label className="toggle-switch">
                  <input type="checkbox" checked={status.bot_active} onChange={toggleBot} />
                  <span className="toggle-slider"></span>
                </label>
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-6" style={{ marginTop: '2rem', borderTop: '1px solid var(--border-color)', paddingTop: '2rem' }}>
              <div>
                <h3 className="text-secondary font-medium mb-4 flex items-center gap-2">
                  <Key size={18} /> API Configuration
                </h3>
                <div className="input-group">
                  <label className="input-label">Dhan Client ID</label>
                  <input 
                    type="text" 
                    className="input" 
                    placeholder="Enter Client ID"
                    value={configKeys.client_id}
                    onChange={(e) => setConfigKeys({...configKeys, client_id: e.target.value})}
                  />
                </div>
                <div className="input-group">
                  <label className="input-label">Dhan Access Token</label>
                  <input 
                    type="password" 
                    className="input" 
                    placeholder="Enter Access Token"
                    value={configKeys.access_token}
                    onChange={(e) => setConfigKeys({...configKeys, access_token: e.target.value})}
                  />
                </div>
                <button className="btn btn-primary" onClick={saveConfig} style={{ marginTop: '0.5rem' }}>
                  Save & Connect
                </button>
              </div>
              
              <div className="card" style={{ background: 'rgba(255,255,255,0.02)', border: 'none' }}>
                <h3 className="text-secondary font-medium mb-3">Strategy Details</h3>
                <ul className="text-sm text-muted gap-2 flex flex-col" style={{ listStyle: 'none' }}>
                  <li className="flex justify-between"><span>Instrument:</span> <span className="text-primary">MCX SILVER Options</span></li>
                  <li className="flex justify-between"><span>Indicator:</span> <span className="text-primary">9 & 20 EMA Crossover</span></li>
                  <li className="flex justify-between"><span>Execution:</span> <span className="text-primary">3-Strike DITM (CE/PE)</span></li>
                  <li className="flex justify-between"><span>Profit Target:</span> <span className="text-success">12 Points</span></li>
                  <li className="flex justify-between"><span>Stop-Loss:</span> <span className="text-danger">6 Points</span></li>
                </ul>
              </div>
            </div>
          </div>
          
          {/* Live Positions */}
          <div className="card">
            <div className="card-header">
              <h2 className="card-title"><TrendingUp /> Active Positions</h2>
            </div>
            
            {positions.length === 0 ? (
              <div className="flex flex-col items-center justify-center text-muted" style={{ height: '200px', textAlign: 'center' }}>
                <Activity size={48} style={{ opacity: 0.2, marginBottom: '1rem' }} />
                <p>No active positions.</p>
                <p className="text-sm mt-1">Waiting for EMA Crossover...</p>
              </div>
            ) : (
              <div className="flex flex-col gap-4">
                {positions.map(pos => (
                  <div key={pos.id} className="card" style={{ padding: '1rem', border: '1px solid rgba(0, 210, 255, 0.2)' }}>
                    <div className="flex justify-between items-center mb-2">
                      <span className="font-bold flex items-center gap-2">
                        {pos.symbol} {pos.strike} 
                        <span className={`status-indicator ${pos.type === 'CE' ? 'text-success' : 'text-danger'}`} style={{ padding: '0.1rem 0.5rem', fontSize: '0.75rem'}}>
                          {pos.type}
                        </span>
                      </span>
                      <span className="text-sm">{pos.quantity} Qty</span>
                    </div>
                    <div className="flex justify-between items-center mt-3">
                      <span className="text-sm text-secondary">Entry: ₹{pos.entry_price.toFixed(2)}</span>
                      <span className={`font-bold ${pos.unrealized_pnl >= 0 ? 'text-success' : 'text-danger'}`}>
                        ₹{pos.unrealized_pnl.toFixed(2)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
          
          {/* Trade History */}
          <div className="card" style={{ gridColumn: 'span 3' }}>
            <div className="card-header">
              <h2 className="card-title"><Database /> Execution Log</h2>
              <button className="btn" style={{ padding: '0.5rem 1rem', background: 'transparent', border: '1px solid var(--border-color)', color: 'var(--text-secondary)' }} onClick={fetchTrades}>
                Refresh Log
              </button>
            </div>
            
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Time</th>
                    <th>Action</th>
                    <th>Strike</th>
                    <th>Type</th>
                    <th>Qty</th>
                    <th>Entry</th>
                    <th>Exit</th>
                    <th>Realized P&L</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {trades.length === 0 ? (
                    <tr>
                      <td colSpan="9" style={{ textAlign: 'center', color: 'var(--text-muted)' }}>No trade history found for today.</td>
                    </tr>
                  ) : (
                    trades.map(trade => (
                      <tr key={trade.id}>
                        <td className="text-sm text-secondary">{new Date(trade.timestamp).toLocaleTimeString()}</td>
                        <td>
                          <span className={`font-medium ${trade.transaction_type === 'BUY' ? 'text-success' : 'text-danger'}`}>
                            {trade.transaction_type}
                          </span>
                        </td>
                        <td>{trade.strike_price}</td>
                        <td className={trade.option_type === 'CE' ? 'text-success' : 'text-danger'}>{trade.option_type}</td>
                        <td>{trade.quantity}</td>
                        <td>₹{trade.entry_price.toFixed(2)}</td>
                        <td>{trade.exit_price ? `₹${trade.exit_price.toFixed(2)}` : '-'}</td>
                        <td className={trade.pnl > 0 ? 'text-success' : trade.pnl < 0 ? 'text-danger' : ''}>
                          {trade.pnl ? `₹${trade.pnl.toFixed(2)}` : '-'}
                        </td>
                        <td>
                          <span className={`status-indicator ${trade.status === 'CLOSED' ? '' : 'active'}`} style={{ padding: '0.2rem 0.5rem', fontSize: '0.7rem' }}>
                            {trade.status}
                          </span>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
          
        </div>
      </main>
    </>
  )
}

export default App;
