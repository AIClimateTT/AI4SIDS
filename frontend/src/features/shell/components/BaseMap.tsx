import { MapContainer, TileLayer, CircleMarker, Tooltip } from 'react-leaflet'
import 'leaflet/dist/leaflet.css'

export interface MapMarker {
  id: string
  label: string
  lat: number
  lng: number
  color: string
  value?: string
}

interface BaseMapProps {
  markers: MapMarker[]
  height?: string
  center?: [number, number]
  zoom?: number
}

export function BaseMap({
  markers,
  height = 'h-96',
  center = [10.5, -61.3],
  zoom = 9,
}: BaseMapProps) {
  return (
    <div className={`w-full ${height} overflow-hidden rounded-lg border`}>
      <MapContainer center={center} zoom={zoom} style={{ height: '100%', width: '100%', zIndex: 1 }}>
        <TileLayer
          url="https://tile.openstreetmap.org/{z}/{x}/{y}.png"
          maxZoom={19}
          attribution='© <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        />
        {markers.map((m) => (
          <CircleMarker
            key={m.id}
            center={[m.lat, m.lng]}
            radius={11}
            pathOptions={{ color: m.color, fillColor: m.color, fillOpacity: 0.75, weight: 2 }}
          >
            <Tooltip>
              <span className="font-medium">{m.label}</span>
              {m.value ? <span> — {m.value}</span> : null}
            </Tooltip>
          </CircleMarker>
        ))}
      </MapContainer>
    </div>
  )
}

export default BaseMap
