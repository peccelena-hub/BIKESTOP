import React from 'react'
import ReactDOM from 'react-dom/client'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <div style={{ fontFamily: 'system-ui', padding: 20 }}>
    <h1>BikeStop</h1>
    <p>✅ Aggiornamento riuscito: questa è la nuova versione</p>
    <p>API health: <a href="/api/health">/api/health</a></p>
  </div>
)
