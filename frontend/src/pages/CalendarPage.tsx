import React, { useEffect, useMemo, useState } from 'react'
import { Calendar, dateFnsLocalizer } from 'react-big-calendar'
import { format, parse, startOfWeek, getDay } from 'date-fns'
import { it } from 'date-fns/locale'
import { api } from '../api'

const localizer = dateFnsLocalizer({
  format,
  parse,
  startOfWeek: () => startOfWeek(new Date(), { weekStartsOn: 1 }),
  getDay,
  locales: { it },
})

export default function CalendarPage(){
  const [events,setEvents]=useState<any[]>([])
  const [title,setTitle]=useState('')
  const [date,setDate]=useState('')
  const [location,setLocation]=useState('')

  async function load(){ setEvents(await api.events()) }
  useEffect(()=>{ load() },[])

  const calEvents = useMemo(()=>events.map(e=>({title:e.title,start:new Date(e.date),end:new Date(e.date),allDay:true,resource:e})),[events])

  async function propose(){
    await api.proposeEvent(title,date,location)
    alert('Proposta inviata (serve approvazione admin).')
    setTitle(''); setDate(''); setLocation('')
  }

  return <div className="grid2">
    <div className="card">
      <h2 style={{marginTop:0}}>Calendario gare</h2>
      <div className="hr"/>
      <Calendar localizer={localizer} events={calEvents} startAccessor="start" endAccessor="end" style={{height:520}} />
      <div className="small" style={{marginTop:10}}>Per la versione completa con viaggi/chat/admin: prossimo step.</div>
    </div>
    <div className="card">
      <h3 style={{marginTop:0}}>Proponi una gara</h3>
      <div className="hr"/>
      <div className="list">
        <input className="input" placeholder="Titolo" value={title} onChange={e=>setTitle(e.target.value)}/>
        <input className="input" type="datetime-local" value={date} onChange={e=>setDate(e.target.value)}/>
        <input className="input" placeholder="Località" value={location} onChange={e=>setLocation(e.target.value)}/>
        <button className="btn primary" onClick={propose}>Invia proposta</button>
      </div>
    </div>
  </div>
}
