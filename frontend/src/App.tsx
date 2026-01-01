import React, { useEffect, useState } from 'react'
import { NavLink, Route, Routes } from 'react-router-dom'
import { api, setToken } from './api'
import CalendarPage from './pages/CalendarPage'
import NotificationsPage from './pages/NotificationsPage'

function Auth() {
  const [email,setEmail]=useState('')
  const [name,setName]=useState('')
  const [password,setPassword]=useState('')
  const [mode,setMode]=useState<'login'|'register'>('login')
  const [err,setErr]=useState<string|undefined>()

  async function go(){
    setErr(undefined)
    try{
      if(mode==='register') await api.register(email,name,password)
      const t = await api.login(email,password)
      setToken(t.access_token)
      location.reload()
    }catch(e:any){ setErr(e.message) }
  }

  return <div className="card">
    <div className="row" style={{justifyContent:'space-between'}}>
      <h2 style={{margin:0}}>{mode==='login'?'Login':'Registrazione'}</h2>
      <button className="btn" onClick={()=>setMode(mode==='login'?'register':'login')}>{mode==='login'?'Crea account':'Ho già un account'}</button>
    </div>
    <div className="hr"/>
    <div className="list">
      <input className="input" placeholder="Email" value={email} onChange={e=>setEmail(e.target.value)}/>
      {mode==='register' && <input className="input" placeholder="Nome" value={name} onChange={e=>setName(e.target.value)}/>}
      <input className="input" placeholder="Password" type="password" value={password} onChange={e=>setPassword(e.target.value)}/>
      {err && <div className="small" style={{color:'crimson'}}>{err}</div>}
      <button className="btn primary" onClick={go}>Entra</button>
      <div className="small">Nota: questa build è il "pacchetto completo". Se vuoi, nel prossimo step rifiniamo tutte le schermate (viaggi, chat, admin) con la versione avanzata.</div>
    </div>
  </div>
}

export default function App(){
  const [me,setMe]=useState<any>(null)
  useEffect(()=>{ api.me().then(setMe).catch(()=>setMe(null)) },[])
  if(!me) return <div className="container"><Auth/></div>

  return <div>
    <div className="nav">
      <NavLink to="/" className={({isActive})=>isActive?'active':''}>Calendario</NavLink>
      <NavLink to="/notifications" className={({isActive})=>isActive?'active':''}>Notifiche</NavLink>
      <div style={{marginLeft:'auto'}} className="row">
        <span className="badge">{me.name}</span>
        <button className="btn" onClick={()=>{setToken(null); location.reload()}}>Esci</button>
      </div>
    </div>
    <div className="container">
      <Routes>
        <Route path="/" element={<CalendarPage/>}/>
        <Route path="/notifications" element={<NotificationsPage/>}/>
      </Routes>
    </div>
  </div>
}
