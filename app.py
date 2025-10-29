from flask import Flask, render_template, request, jsonify
import folium
from folium.features import DivIcon
import random

app = Flask(__name__)
ubicaciones = {}

# Colores disponibles para los marcadores (uno por vendedor)
COLORES = [
    "red", "blue", "green", "purple", "orange", "darkred", "lightblue",
    "lightgreen", "cadetblue", "darkblue", "black", "pink", "gray"
]
color_asignado = {}  # Guarda el color de cada vendedor para mantenerlo igual

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
        # Asigna color único si no tenía antes
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

    # Toma la primera ubicación para centrar el mapa
    primera = next(iter(ubicaciones.values()))
    mapa = folium.Map(location=[primera['lat'], primera['lng']], zoom_start=13)

    # Agrega los marcadores
    for nombre, pos in ubicaciones.items():
        color = color_asignado.get(nombre, "blue")

        # Marcador con icono y popup
        folium.Marker(
            [pos['lat'], pos['lng']],
            popup=f"<b>{nombre}</b>",
            tooltip=f"{nombre}",
            icon=folium.Icon(color=color, icon='car', prefix='fa')  # 🚗 icono de vehículo
        ).add_to(mapa)

        # Nombre flotante sobre el punto
        folium.map.Marker(
            [pos['lat'], pos['lng']],
            icon=DivIcon(
                icon_size=(150,36),
                icon_anchor=(0,0),
                html=f'<div style="font-size: 12px; color: {color}; background: white; border-radius: 4px; padding: 2px;">{nombre}</div>',
            )
        ).add_to(mapa)

    # HTML del mapa
    mapa_html = mapa._repr_html_()

    # Script JS: guarda vista y refresca cada 5 segundos
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
