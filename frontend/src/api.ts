const API_BASE = (location.origin.includes('localhost') ? 'http://localhost:8000' : '')

export function getToken(){ return localStorage.getItem('token') }
export function setToken(t: string|null){ t ? localStorage.setItem('token',t) : localStorage.removeItem('token') }

async function req(path: string, opts: RequestInit = {}){
  const token = getToken()
  const headers:any = {'Content-Type':'application/json', ...(opts.headers||{})}
  if(token) headers.Authorization = `Bearer ${token}`
  const r = await fetch(`${API_BASE}${path}`, {...opts, headers})
  if(!r.ok) throw new Error(await r.text())
  const ct = r.headers.get('content-type')||''
  return ct.includes('application/json') ? r.json() : r.text()
}

export const api = {
  register: (email:string,name:string,password:string)=>req('/auth/register',{method:'POST',body:JSON.stringify({email,name,password})}),
  login: (email:string,password:string)=>req('/auth/login',{method:'POST',body:JSON.stringify({email,password})}),
  me: ()=>req('/me'),
  events: ()=>req('/events'),
  proposeEvent: (title:string,date:string,location:string)=>req('/events',{method:'POST',body:JSON.stringify({title,date,location})}),
  notifications: ()=>req('/notifications'),
}
