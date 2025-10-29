from flask import Flask, render_template, request, jsonify
import folium
from pyngrok import ngrok

app = Flask(__name__)

# Diccionario para guardar las ubicaciones de los vehículos
ubicaciones = {}

@app.route('/')
def index():
    # Página que usan los celulares para enviar su ubicación
    return render_template('rastreo.html')

@app.route('/actualizar_ubicacion', methods=['POST'])
def actualizar_ubicacion():
    data = request.get_json()
    nombre = data.get('nombre', 'Vendedor')
    lat = data.get('lat')
    lng = data.get('lng')

    if lat and lng:
        ubicaciones[nombre] = {'lat': lat, 'lng': lng}
        print(f"📍 Ubicación recibida: {nombre} -> ({lat}, {lng})")
        return jsonify({'status': 'ok'})
    else:
        return jsonify({'status': 'error', 'message': 'Faltan coordenadas'}), 400

@app.route('/mapa')
def mapa():
    if not ubicaciones:
        return "<h3>No hay ubicaciones registradas aún</h3>"

    # Crear mapa centrado en la primera ubicación
    primera = next(iter(ubicaciones.values()))
    mapa = folium.Map(location=[primera['lat'], primera['lng']], zoom_start=13)

    # Agregar marcadores de todos los vehículos
    for nombre, pos in ubicaciones.items():
        folium.Marker([pos['lat'], pos['lng']], popup=nombre).add_to(mapa)

    # Convertir el mapa a HTML
    mapa_html = mapa._repr_html_()

    # Script JS para guardar y restaurar posición/zoom + recargar automáticamente
    js_script = """
    <script>
      // Recuperar la posición y zoom anteriores (si existen)
      const prevLat = localStorage.getItem('mapLat');
      const prevLng = localStorage.getItem('mapLng');
      const prevZoom = localStorage.getItem('mapZoom');

      // Esperar a que Folium cargue el mapa
      setTimeout(() => {
        if (window.map && prevLat && prevLng && prevZoom) {
          window.map.setView([parseFloat(prevLat), parseFloat(prevLng)], parseInt(prevZoom));
        }

        // Guardar posición y zoom antes de salir o recargar
        window.map.on('moveend', () => {
          const center = window.map.getCenter();
          localStorage.setItem('mapLat', center.lat);
          localStorage.setItem('mapLng', center.lng);
          localStorage.setItem('mapZoom', window.map.getZoom());
        });

        // Recargar automáticamente cada 5 segundos
        setTimeout(() => {
          location.reload();
        }, 5000);
      }, 1000);
    </script>
    """

    return mapa_html + js_script

if __name__ == '__main__':
    # Crear túnel HTTPS con ngrok
    public_url = ngrok.connect(5000, "http")
    print("🌍 URL pública para usar desde el celular:", public_url)
    print("📡 Abre en tu PC: http://localhost:5000/mapa")

    # Iniciar Flask
    app.run(host='0.0.0.0', port=5000)
