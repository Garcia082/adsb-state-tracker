<script setup>
import { onMounted } from 'vue'
import L from 'leaflet'
import { getPlanes } from '@/api.js'
import 'leaflet/dist/leaflet.css'
import 'leaflet-rotatedmarker'

/* PNGs */
import blueIcon   from '@/assets/leaflet/marker-icon-blue.png'
import greenIcon  from '@/assets/leaflet/marker-icon-green.png'
import redIcon    from '@/assets/leaflet/marker-icon-red.png'
import shadowIcon from '@/assets/leaflet/marker-shadow.png'

function mk(url){
  return L.icon({
    iconUrl:url, shadowUrl:shadowIcon,
    iconSize:[25,41], iconAnchor:[12,41],
    popupAnchor:[1,-34], shadowSize:[41,41]
  })
}
const ICON = { civil:mk(blueIcon), state:mk(greenIcon), warn:mk(redIcon) }

let map
const markers = {}   // icao24 → L.Marker

function upsert(p){
  const key = p.icao24
  const ll  = [p.lat, p.lon]
  const ic  = !p.is_state      ? ICON.civil :
              p.autorizado     ? ICON.state : ICON.warn

  if (markers[key]){
    markers[key].setLatLng(ll).setIcon(ic).setRotationAngle(p.track||0)
  }else{
    markers[key] = L.marker(ll,{icon:ic,rotationAngle:p.track||0})
                    .addTo(map).bindTooltip(p.callsign||p.icao24)
  }
}

onMounted(()=>{
  map = L.map('map').setView([40.4,-3.7],6)
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
              {attribution:'© OSM'}).addTo(map)

 async function refresh () {
    const planes = await getPlanes()
    planes.forEach(upsert)
  }
  refresh()
  setInterval(refresh, 10_000)
})
</script>

<template><div id="map" style="height:100vh"></div></template>
