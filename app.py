from flask import Flask, render_template, request, jsonify
import folium

app = Flask(__name__)
ubicaciones = {}

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
        ubicaciones[nombre] = {'lat': lat, 'lng': lng}
        return jsonify({'status': 'ok'})
    else:
        return jsonify({'status': 'error', 'message': 'Faltan coordenadas'}), 400

@app.route('/mapa')
def mapa():
    if not ubicaciones:
        return "<h3>No hay ubicaciones registradas aún</h3>"

    primera = next(iter(ubicaciones.values()))
    mapa = folium.Map(location=[primera['lat'], primera['lng']], zoom_start=13)
    for nombre, pos in ubicaciones.items():
        folium.Marker([pos['lat'], pos['lng']], popup=nombre).add_to(mapa)

    mapa_html = mapa._repr_html_()
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
