from flask import Flask, render_template, request, jsonify
import folium
from folium.features import DivIcon
import random

app = Flask(__name__)
ubicaciones = {}

# Lista de colores de marcadores disponibles
COLORES = [
    "red", "blue", "green", "purple", "orange", "darkred",
    "lightblue", "lightgreen", "cadetblue", "darkblue", "black", "pink", "gray"
]
color_asignado = {}  # Guarda el color de cada vendedor para mantener consistencia

@app.route('/')
def index():
    return render_template('rastreo.html')

@app.route('/actualizar_ubicacion', methods=['POST'])
def actualizar_ubicacion():
    data = request.get_json()
    nombre = data.get('nombre', 'Vendedor')
    lat = data.get('lat')
    lng = data.get('lng')

    if lat and lng:
        # Asignar color si no tenía antes
        if nombre not in color_asignado:
            color_asignado[nombre] = random.choice(COLORES)

        ubicaciones[nombre] = {'lat': lat, 'lng': lng}
        print(f"📍 Ubicación recibida: {nombre} -> ({lat}, {lng})")
        return jsonify({'status': 'ok'})
    else:
        return jsonify({'status': 'error', 'message': 'Faltan coordenadas'}), 400

@app.route('/mapa')
def mapa():
    if not ubicaciones:
        return "<h3>No hay ubicaciones registradas aún</h3>"

    # Centra el mapa en la primera ubicación
    primera = next(iter(ubicaciones.values()))
    mapa = folium.Map(location=[primera['lat'], primera['lng']], zoom_start=13)

    # Agregar marcadores con nombres y colores únicos
    for nombre, pos in ubicaciones.items():
        color = color_asignado.get(nombre, "blue")

        # Marcador principal
        folium.CircleMarker(
            location=[pos['lat'], pos['lng']],
            radius=8,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.9,
            popup=f"<b>{nombre}</b>",
            tooltip=f"{nombre}"
        ).add_to(mapa)

        # Nombre flotante encima del marcador
        folium.map.Marker(
            [pos['lat'] + 0.0003, pos['lng']],  # un poco más arriba para que no tape el punto
            icon=DivIcon(
                icon_size=(150,36),
                icon_anchor=(0,0),
                html=f'<div style="font-size: 13px; font-weight: bold; color:{color}; background-color:white; padding:2px; border-radius:4px;">{nombre}</div>'
            )
        ).add_to(mapa)

    mapa_html = mapa._repr_html_()

    # JavaScript para refrescar el mapa cada 5 segundos
    js_script = """
    <script>
      const prevLat = localStorage.getItem('mapLat');
      const prevLng = localStorage.getItem('mapLng');
      const prevZoom = localStorage.getItem('mapZoom');
      setTimeout(() => {
        if (window.map && prevLat && prevLng && prevZoom) {
          window.map.setView([parseFloat(prevLat), parseFloat(prevLng)], parseInt(prevZoom));
        }
        window.map.on('moveend', () => {
          const center = window.map.getCenter();
          localStorage.setItem('mapLat', center.lat);
          localStorage.setItem('mapLng', center.lng);
          localStorage.setItem('mapZoom', window.map.getZoom());
        });
        setTimeout(() => { location.reload(); }, 5000);
      }, 1000);
    </script>
    """

    return mapa_html + js_script


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
