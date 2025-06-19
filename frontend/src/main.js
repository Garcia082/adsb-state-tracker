import L from 'leaflet'

// Íconos
const iconBlue = L.icon({
  iconUrl:  '/src/icons/blue.png',
  shadowUrl:'/src/icons/shadow.png',
  iconSize: [25, 41],
  shadowSize:[41, 41],
  iconAnchor:[12, 41],
  shadowAnchor:[12, 41]
})

const iconGreen = L.icon({
  iconUrl:  '/src/icons/green.png',
  shadowUrl:'/src/icons/shadow.png',
  iconSize: [25, 41],
  shadowSize:[41, 41],
  iconAnchor:[12, 41],
  shadowAnchor:[12, 41]
})

// Mapa base
const map = L.map('map').setView([40.0, -3.5], 6)
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  maxZoom: 13,
  attribution: '&copy; OSM contributors'
}).addTo(map)

// Diccionario para reutilizar marcadores
const markers = new Map()

async function fetchAeronaves () {
  const res = await fetch('/api/aeronaves')
  if (!res.ok) return console.error('Error API aeronaves')
  const data = await res.json()

  const ahora = Date.now()
  const activos = new Set()

  data.forEach(a => {
    activos.add(a.icao24)
    const pos = [a.lat, a.lon]
    let m = markers.get(a.icao24)

    if (!m) {
      m = L.marker(pos, { icon: a.is_state ? iconGreen : iconBlue })
        .addTo(map)
        .on('click', () => popupAutorizacion(a.icao24, m))
      markers.set(a.icao24, m)
    } else {
      m.setLatLng(pos)
    }
    m.lastUpdate = ahora
  })

  // elimina obsoletos (>30 s sin actualizar)
  for (const [hex, m] of markers) {
    if (ahora - m.lastUpdate > 30_000 || !activos.has(hex)) {
      map.removeLayer(m)
      markers.delete(hex)
    }
  }
}

async function popupAutorizacion (hex, marker) {
  const res = await fetch(`/api/autorizacion/${hex}`)
  let html
  if (res.ok) {
    const a = await res.json()
    html = `
      <table class="popup-table">
        <tr><th>ICAO</th><td>${a.icao24}</td></tr>
        <tr><th>Autorización</th><td>${a.autorizacion}</td></tr>
        <tr><th>Válida</th><td>${a.desde} → ${a.hasta}</td></tr>
        <tr><th>Casilla 18</th><td>${a.casilla18}</td></tr>
      </table>`
  } else {
    html = `<b>${hex}</b>: sin autorización registrada`
  }
  marker.bindPopup(html).openPopup()
}

// Bucle de refresco
fetchAeronaves()
setInterval(fetchAeronaves, 5_000)
