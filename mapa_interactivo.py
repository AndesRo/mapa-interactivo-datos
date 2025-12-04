#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mapa Interactivo 
mapa web interactivo con datos dinámicos
Autor: [Andres]
Fecha: 2025
"""

import warnings
warnings.filterwarnings('ignore')

import json
import os
import webbrowser
from datetime import datetime, timedelta

import folium
import pandas as pd
import requests
from folium.plugins import MarkerCluster, HeatMap, Fullscreen, MiniMap

# Configuración
API_ELEGIDA = "terremotos"  # Cambiar entre: "terremotos", "clima", "incendios"
API_KEY_OPENWEATHER = "47442571cbb67ffbbabbbf33efe1d5e1"  # Opcional: Para clima, obtener en openweathermap.org
CENTER_COORDS = [-33.4489, -70.6693]  # Santiago, Chile
ZOOM_INICIAL = 6
ARCHIVO_SALIDA = "mapa_interactivo.html"
ARCHIVO_JSON_FALLBACK = "datos_ejemplo.json"


def obtener_datos_api():
    """
    Obtiene datos reales de una API pública según la opción seleccionada.
    Retorna un DataFrame de pandas con los datos procesados.
    """
    
    if API_ELEGIDA == "terremotos":
        # API de terremotos de USGS (últimos 30 días)
        url = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_month.geojson"
        print("Obteniendo datos de terremotos recientes (USGS API)...")
        
        try:
            respuesta = requests.get(url, timeout=10)
            respuesta.raise_for_status()
            datos = respuesta.json()
            
            # Procesar datos GeoJSON
            features = datos['features']
            datos_procesados = []
            
            for feature in features:
                props = feature['properties']
                coords = feature['geometry']['coordinates']
                
                # Filtrar solo terremotos con magnitud significativa
                if props['mag'] is not None and props['mag'] >= 2.0:
                    datos_procesados.append({
                        'magnitud': props['mag'],
                        'lugar': props['place'],
                        'lat': coords[1],
                        'lon': coords[0],
                        'profundidad': coords[2],
                        'fecha': datetime.fromtimestamp(props['time']/1000).strftime('%Y-%m-%d %H:%M'),
                        'tipo': 'Terremoto'
                    })
            
            df = pd.DataFrame(datos_procesados)
            print(f"✓ {len(df)} terremotos obtenidos de la API")
            return df
            
        except (requests.exceptions.RequestException, KeyError, ValueError) as e:
            print(f"✗ Error al obtener datos de terremotos: {e}")
            print("Usando datos de ejemplo...")
            return usar_datos_ejemplo()
    
    elif API_ELEGIDA == "clima":
        # API de OpenWeatherMap para ciudades de Chile
        if not API_KEY_OPENWEATHER:
            print("⚠️  Advertencia: No hay API key para OpenWeatherMap")
            print("Usando datos de ejemplo...")
            return usar_datos_ejemplo()
        
        ciudades_chile = [
            ("Santiago", -33.4489, -70.6693),
            ("Valparaíso", -33.0458, -71.6197),
            ("Concepción", -36.8269, -73.0497),
            ("Antofagasta", -23.6500, -70.4000),
            ("Puerto Montt", -41.4718, -72.9396),
            ("Iquique", -20.2208, -70.1431),
            ("La Serena", -29.9027, -71.2519)
        ]
        
        datos_procesados = []
        print("Obteniendo datos climáticos (OpenWeatherMap API)...")
        
        try:
            for ciudad, lat, lon in ciudades_chile:
                url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY_OPENWEATHER}&units=metric&lang=es"
                respuesta = requests.get(url, timeout=10)
                
                if respuesta.status_code == 200:
                    datos = respuesta.json()
                    datos_procesados.append({
                        'ciudad': ciudad,
                        'temperatura': datos['main']['temp'],
                        'humedad': datos['main']['humidity'],
                        'viento': datos['wind']['speed'],
                        'descripcion': datos['weather'][0]['description'],
                        'lat': lat,
                        'lon': lon,
                        'fecha': datetime.now().strftime('%Y-%m-%d %H:%M'),
                        'tipo': 'Clima'
                    })
                    print(f"  ✓ Datos obtenidos para {ciudad}")
            
            df = pd.DataFrame(datos_procesados)
            print(f"✓ Datos climáticos obtenidos para {len(df)} ciudades")
            return df
            
        except (requests.exceptions.RequestException, KeyError, ValueError) as e:
            print(f"✗ Error al obtener datos climáticos: {e}")
            print("Usando datos de ejemplo...")
            return usar_datos_ejemplo()
    
    elif API_ELEGIDA == "incendios":
        # NASA FIRMS API para incendios activos (datos de ejemplo)
        print("⚠️  API de incendios requiere clave especial, usando datos de ejemplo...")
        return usar_datos_ejemplo()
    
    else:
        print("Opción no válida, usando datos de ejemplo...")
        return usar_datos_ejemplo()


def usar_datos_ejemplo():
    """
    Carga datos de ejemplo desde archivo JSON cuando la API falla.
    """
    try:
        # Crear datos de ejemplo si no existe el archivo
        if not os.path.exists(ARCHIVO_JSON_FALLBACK):
            crear_datos_ejemplo()
        
        with open(ARCHIVO_JSON_FALLBACK, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        
        df = pd.DataFrame(datos)
        print(f"✓ {len(df)} registros cargados desde archivo de ejemplo")
        return df
        
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        print(f"✗ Error al cargar datos de ejemplo: {e}")
        # Datos de emergencia
        datos_emergencia = [
            {
                'lugar': 'Santiago Centro',
                'magnitud': 4.2,
                'lat': -33.4489,
                'lon': -70.6693,
                'fecha': datetime.now().strftime('%Y-%m-%d %H:%M'),
                'tipo': 'Terremoto',
                'profundidad': 10
            }
        ]
        df = pd.DataFrame(datos_emergencia)
        print("✓ Datos de emergencia creados")
        return df


def crear_datos_ejemplo():
    """
    Crea un archivo JSON con datos de ejemplo.
    """
    datos_ejemplo = [
        {
            "lugar": "30km al norte de Santiago",
            "magnitud": 4.2,
            "lat": -33.1,
            "lon": -70.5,
            "profundidad": 15,
            "fecha": datetime.now().strftime('%Y-%m-%d %H:%M'),
            "tipo": "Terremoto"
        },
        {
            "lugar": "Valparaíso",
            "magnitud": 3.8,
            "lat": -33.0458,
            "lon": -71.6197,
            "profundidad": 25,
            "fecha": (datetime.now() - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M'),
            "tipo": "Terremoto"
        },
        {
            "lugar": "Concepción",
            "magnitud": 5.1,
            "lat": -36.8269,
            "lon": -73.0497,
            "profundidad": 30,
            "fecha": (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M'),
            "tipo": "Terremoto"
        },
        {
            "lugar": "Antofagasta",
            "magnitud": 4.5,
            "lat": -23.6500,
            "lon": -70.4000,
            "profundidad": 40,
            "fecha": (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d %H:%M'),
            "tipo": "Terremoto"
        }
    ]
    
    with open(ARCHIVO_JSON_FALLBACK, 'w', encoding='utf-8') as f:
        json.dump(datos_ejemplo, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Archivo de ejemplo creado: {ARCHIVO_JSON_FALLBACK}")


def asignar_color_marcador(dato, tipo_dato):
    """
    Asigna color al marcador según el tipo de dato y su valor.
    """
    if tipo_dato == "terremotos":
        if dato >= 5.0:
            return 'red'
        elif dato >= 4.0:
            return 'orange'
        elif dato >= 3.0:
            return 'lightgreen'
        else:
            return 'green'
    
    elif tipo_dato == "clima":
        if dato >= 30:
            return 'red'
        elif dato >= 20:
            return 'orange'
        elif dato >= 10:
            return 'lightblue'
        else:
            return 'blue'
    
    return 'blue'  # Color por defecto


def asignar_icono(tipo):
    """
    Asigna un ícono según el tipo de dato.
    """
    if tipo == "Terremoto":
        return "info-sign"
    elif tipo == "Clima":
        return "cloud"
    else:
        return "info-sign"


def crear_mapa_interactivo(df):
    """
    Crea un mapa interactivo con Folium usando los datos del DataFrame.
    """
    print("Creando mapa interactivo...")
    
    # Crear mapa base
    mapa = folium.Map(
        location=CENTER_COORDS,
        zoom_start=ZOOM_INICIAL,
        tiles="OpenStreetMap",
        control_scale=True
    )
    
    # Añadir capa alternativa
    folium.TileLayer(
        'Stamen Terrain',
        name='Terreno (Stamen)',
        attr='Map tiles by Stamen Design, under CC BY 3.0.'
    ).add_to(mapa)
    
    # Añadir plugin de pantalla completa
    Fullscreen().add_to(mapa)
    
    # Añadir minimapa
    MiniMap(toggle_display=True).add_to(mapa)
    
    # Crear clusters para marcadores
    marker_cluster = MarkerCluster(
        name="Marcadores",
        overlay=True,
        control=True,
        icon_create_function=None
    ).add_to(mapa)
    
    # Procesar cada fila del DataFrame
    for idx, row in df.iterrows():
        try:
            # Validar coordenadas
            lat = float(row.get('lat', 0))
            lon = float(row.get('lon', 0))
            
            if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                print(f"⚠️  Coordenadas inválidas para {row.get('lugar', 'desconocido')}")
                continue
            
            # Determinar color según el tipo de datos
            if API_ELEGIDA == "terremotos":
                color = asignar_color_marcador(row.get('magnitud', 0), "terremotos")
                tooltip_text = f"{row.get('lugar', 'Lugar desconocido')} - M{row.get('magnitud', 'N/A')}"
                
                # Tamaño del marcador según magnitud
                tamaño = min(30, max(10, row.get('magnitud', 1) * 5))
                
                # Popup con información detallada
                popup_html = f"""
                <div style="width: 200px;">
                    <h4 style="color: {color}; margin: 5px 0;">Terremoto</h4>
                    <hr>
                    <p><strong>Lugar:</strong> {row.get('lugar', 'N/A')}</p>
                    <p><strong>Magnitud:</strong> {row.get('magnitud', 'N/A')}</p>
                    <p><strong>Profundidad:</strong> {row.get('profundidad', 'N/A')} km</p>
                    <p><strong>Fecha:</strong> {row.get('fecha', 'N/A')}</p>
                </div>
                """
                
            elif API_ELEGIDA == "clima":
                color = asignar_color_marcador(row.get('temperatura', 0), "clima")
                tooltip_text = f"{row.get('ciudad', 'Ciudad desconocida')} - {row.get('temperatura', 'N/A')}°C"
                tamaño = 15
                
                popup_html = f"""
                <div style="width: 200px;">
                    <h4 style="color: {color}; margin: 5px 0;">Condiciones Climáticas</h4>
                    <hr>
                    <p><strong>Ciudad:</strong> {row.get('ciudad', 'N/A')}</p>
                    <p><strong>Temperatura:</strong> {row.get('temperatura', 'N/A')}°C</p>
                    <p><strong>Humedad:</strong> {row.get('humedad', 'N/A')}%</p>
                    <p><strong>Viento:</strong> {row.get('viento', 'N/A')} km/h</p>
                    <p><strong>Descripción:</strong> {row.get('descripcion', 'N/A')}</p>
                    <p><strong>Actualizado:</strong> {row.get('fecha', 'N/A')}</p>
                </div>
                """
            
            else:
                color = 'blue'
                tooltip_text = row.get('lugar', 'Ubicación')
                tamaño = 12
                
                popup_html = f"""
                <div style="width: 200px;">
                    <h4>Información</h4>
                    <hr>
                    <p><strong>Lugar:</strong> {row.get('lugar', 'N/A')}</p>
                    <p><strong>Tipo:</strong> {row.get('tipo', 'N/A')}</p>
                    <p><strong>Fecha:</strong> {row.get('fecha', 'N/A')}</p>
                </div>
                """
            
            # Crear marcador
            folium.CircleMarker(
                location=[lat, lon],
                radius=tamaño,
                popup=folium.Popup(popup_html, max_width=300),
                tooltip=tooltip_text,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.7,
                weight=2
            ).add_to(marker_cluster)
            
        except (KeyError, ValueError, TypeError) as e:
            print(f"✗ Error al procesar fila {idx}: {e}")
            continue
    
    # Crear heatmap si hay suficientes datos
    if len(df) >= 5:
        print("Añadiendo capa de heatmap...")
        datos_heatmap = []
        
        # Ponderar por magnitud si es terremoto
        if API_ELEGIDA == "terremotos" and 'magnitud' in df.columns:
            for _, row in df.iterrows():
                try:
                    peso = float(row['magnitud']) / 5.0 if row['magnitud'] > 0 else 0.1
                    datos_heatmap.append([row['lat'], row['lon'], peso])
                except (ValueError, KeyError):
                    continue
        else:
            datos_heatmap = df[['lat', 'lon']].values.tolist()
        
        if datos_heatmap:
            HeatMap(datos_heatmap, name="Mapa de calor", radius=15).add_to(mapa)
    
    # Añadir leyenda
    if API_ELEGIDA == "terremotos":
        leyenda_html = '''
        <div style="
            position: fixed; 
            bottom: 50px; 
            left: 50px; 
            width: 180px; 
            height: auto;
            background-color: white; 
            border: 2px solid grey; 
            z-index: 9999; 
            font-size: 12px;
            padding: 10px;
            border-radius: 5px;
            box-shadow: 0 0 10px rgba(0,0,0,0.2);
        ">
            <h4 style="margin-top: 0;">Leyenda - Terremotos</h4>
            <p><span style="color: red;">●</span> Magnitud ≥ 5.0 (Alta)</p>
            <p><span style="color: orange;">●</span> Magnitud 4.0-4.9 (Media)</p>
            <p><span style="color: lightgreen;">●</span> Magnitud 3.0-3.9 (Baja)</p>
            <p><span style="color: green;">●</span> Magnitud < 3.0 (Muy baja)</p>
            <p>Tamaño: proporcional a magnitud</p>
        </div>
        '''
    elif API_ELEGIDA == "clima":
        leyenda_html = '''
        <div style="
            position: fixed; 
            bottom: 50px; 
            left: 50px; 
            width: 180px; 
            height: auto;
            background-color: white; 
            border: 2px solid grey; 
            z-index: 9999; 
            font-size: 12px;
            padding: 10px;
            border-radius: 5px;
            box-shadow: 0 0 10px rgba(0,0,0,0.2);
        ">
            <h4 style="margin-top: 0;">Leyenda - Clima</h4>
            <p><span style="color: red;">●</span> ≥ 30°C (Caluroso)</p>
            <p><span style="color: orange;">●</span> 20-29°C (Templado)</p>
            <p><span style="color: lightblue;">●</span> 10-19°C (Fresco)</p>
            <p><span style="color: blue;">●</span> < 10°C (Frío)</p>
        </div>
        '''
    else:
        leyenda_html = '''
        <div style="
            position: fixed; 
            bottom: 50px; 
            left: 50px; 
            width: 150px; 
            height: auto;
            background-color: white; 
            border: 2px solid grey; 
            z-index: 9999; 
            font-size: 12px;
            padding: 10px;
            border-radius: 5px;
            box-shadow: 0 0 10px rgba(0,0,0,0.2);
        ">
            <h4 style="margin-top: 0;">Leyenda</h4>
            <p><span style="color: blue;">●</span> Puntos de datos</p>
        </div>
        '''
    
    mapa.get_root().html.add_child(folium.Element(leyenda_html))
    
    # Añadir control de capas
    folium.LayerControl(collapsed=False).add_to(mapa)
    
    # Añadir título al mapa
    titulo = f"Mapa Interactivo - Datos de {API_ELEGIDA.capitalize()} en tiempo real"
    titulo_html = f'''
    <div style="
        position: fixed; 
        top: 10px; 
        left: 50%; 
        transform: translateX(-50%);
        z-index: 9999; 
        font-size: 16px; 
        font-weight: bold;
        background-color: white; 
        padding: 10px 20px;
        border-radius: 5px;
        box-shadow: 0 0 10px rgba(0,0,0,0.2);
        border: 2px solid #0078A8;
        text-align: center;
    ">
        {titulo}<br>
        <span style="font-size: 12px; font-weight: normal;">
            Actualizado: {datetime.now().strftime('%Y-%m-%d %H:%M')} | Datos: {len(df)} registros
        </span>
    </div>
    '''
    mapa.get_root().html.add_child(folium.Element(titulo_html))
    
    print("✓ Mapa creado exitosamente")
    return mapa


def guardar_y_abrir_mapa(mapa, df):
    """
    Guarda el mapa como archivo HTML y lo abre en el navegador.
    """
    try:
        # Guardar mapa
        mapa.save(ARCHIVO_SALIDA)
        print(f"✓ Mapa guardado como: {ARCHIVO_SALIDA}")
        
        # Exportar datos como CSV
        if df is not None and not df.empty:
            archivo_csv = "datos_exportados.csv"
            df.to_csv(archivo_csv, index=False, encoding='utf-8')
            print(f"✓ Datos exportados como: {archivo_csv}")
        
        # Abrir en navegador
        ruta_completa = os.path.abspath(ARCHIVO_SALIDA)
        print("✓ Abriendo en navegador...")
        webbrowser.open(f'file://{ruta_completa}')
        
        return True
        
    except (IOError, OSError, PermissionError) as e:
        print(f"✗ Error al guardar/abrir mapa: {e}")
        return False


def main():
    """
    Función principal del programa.
    """
    print("=" * 60)
    print("       MAPA INTERACTIVO DE DATOS REALES")
    print("=" * 60)
    print(f"Fuente de datos: {API_ELEGIDA.upper()}")
    print(f"Centro del mapa: Santiago, Chile")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    
    # Obtener datos
    df = obtener_datos_api()
    
    # Validar que tenemos datos
    if df.empty:
        print("✗ No se pudieron obtener datos. Saliendo...")
        return
    
    # Mostrar estadísticas básicas
    print(f"\n📊 Estadísticas de datos:")
    print(f"   - Total de registros: {len(df)}")
    
    if API_ELEGIDA == "terremotos" and 'magnitud' in df.columns:
        print(f"   - Magnitud máxima: {df['magnitud'].max():.1f}")
        print(f"   - Magnitud mínima: {df['magnitud'].min():.1f}")
        print(f"   - Magnitud promedio: {df['magnitud'].mean():.1f}")
    
    # Crear mapa
    mapa = crear_mapa_interactivo(df)
    
    # Guardar y abrir
    if guardar_y_abrir_mapa(mapa, df):
        print("\n" + "=" * 60)
        print("✅ ¡Mapa generado exitosamente!")
        print(f"📁 Archivo: {ARCHIVO_SALIDA}")
        print("🌐 ¡Abre tu navegador para ver el mapa interactivo!")
        print("=" * 60)
    else:
        print("\n✗ Error al generar el mapa")


# Función para refrescar datos (opcional, comentada)
def refrescar_datos(minutos=5):
    """
    Función para refrescar datos automáticamente cada X minutos.
    Descomentar y adaptar para uso en tiempo real.
    """
    # import time
    # while True:
    #     print(f"\n🔄 Refrescando datos... ({datetime.now().strftime('%H:%M:%S')})")
    #     df = obtener_datos_api()
    #     mapa = crear_mapa_interactivo(df)
    #     mapa.save(ARCHIVO_SALIDA)
    #     print(f"✓ Datos actualizados. Próxima actualización en {minutos} minutos.")
    #     time.sleep(minutos * 60)


if __name__ == "__main__":
    # Ejecutar programa principal
    main()
    
    # Para usar la función de refresco automático, descomentar:
    # refrescar_datos(minutos=10)