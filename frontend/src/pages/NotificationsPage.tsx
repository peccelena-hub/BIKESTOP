import React, { useEffect, useState } from 'react'
import { api } from '../api'

export default function NotificationsPage(){
  const [items,setItems]=useState<any[]>([])
  async function load(){ setItems(await api.notifications()) }
  useEffect(()=>{ load() },[])
  return <div className="card">
    <div className="row" style={{justifyContent:'space-between'}}>
      <h2 style={{marginTop:0}}>Notifiche</h2>
      <button className="btn" onClick={load}>Aggiorna</button>
    </div>
    <div className="hr"/>
    {items.length===0 ? <div className="small">Nessuna notifica (MVP).</div> :
      <div className="list">{items.map(n=><div key={n.id} className="card" style={{background:'#fbfbfc'}}><b>{n.title}</b><div className="small">{n.body}</div></div>)}</div>
    }
  </div>
}
