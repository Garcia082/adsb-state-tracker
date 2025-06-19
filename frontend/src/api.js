//const API = import.meta.env.VITE_API  || `http://${window.location.hostname}:5000`
  const API = 'http://192.168.1.192:5000'

export async function getPlanes () {
  const r = await fetch(`${API}/api/aeronaves?det=1`)
  if (!r.ok) throw new Error('API aeronautas')
  return r.json()
}

export async function getAutorizacion (hex) {
  const r = await fetch(`${API}/api/autorizacion/${hex}`)
  return r.ok ? r.json() : null
}
