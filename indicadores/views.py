from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import ConjuntoIndicadores, Dimension, Tematica, Indicador, SerieDatos, Dato, Comuna
import plotly.express as px
import pandas as pd
from datetime import datetime
from plotly.utils import PlotlyJSONEncoder  # Importa el encoder especializado
import folium
from django.contrib.gis.geos import GEOSGeometry
import json
import plotly.graph_objects as go
import re
import numpy as np

# Función auxiliar para crear anotaciones de pie de página mejoradas
def crear_pie_pagina(titulo, descripcion, entidad, fuente):
    """Crea un pie de página enriquecido para los gráficos.

    Args:
        titulo: Título descriptivo del gráfico
        descripcion: Breve descripción del contenido del gráfico
        entidad: Entidad recopilatoria de los datos
        fuente: Fuente de los datos o URL

    Returns:
        Diccionario con la configuración de la anotación
    """
    return dict(
        x=0.5,
        y=-0.4,
        showarrow=False,
        text=f"<b>{titulo}</b><br>{descripcion}<br>Fuente: {entidad} | {fuente}",
        xref='paper',
        yref='paper',
        font=dict(size=13, color='#2c3e50'),
        bgcolor='rgba(244, 244, 244, 0.8)',
        bordercolor='rgba(0, 0, 0, 0.1)',
        borderwidth=1,
        borderpad=4,
        align='center'
    )

def crear_grafico_barras(indicador_nombre, titulo, yaxis_title, unidad_medida):
    """
    Crea un gráfico de barras para un indicador específico.

    Args:
        indicador_nombre: Nombre del indicador (ej: 'SIS_4_T3_I13')
        titulo: Título del gráfico
        yaxis_title: Título del eje Y
        unidad_medida: Unidad de medida del indicador

    Returns:
        Diccionario con los datos del gráfico en formato JSON
    """
    try:
        # Obtener el indicador
        indicador = Indicador.objects.get(nombre=indicador_nombre)

        # Obtener la serie de datos
        serie = SerieDatos.objects.filter(
            indicador=indicador,
            desagregacion_geografica='Cali'
        ).first()

        if not serie:
            return None

        # Obtener los datos
        datos = Dato.objects.filter(serie_datos=serie).order_by('fecha_dato')

        # Crear listas para los datos
        anios = []
        valores = []

        # Agrupar datos por quinquenios desde 1990 hasta 2025
        for dato in datos:
            anio = dato.fecha_dato.year
            if 1990 <= anio <= 2025 and anio % 5 == 0:  # Solo considerar años quinquenales desde 1990 hasta 2025
                anios.append(anio)
                valores.append(float(dato.valor_dato))

        # Crear DataFrame
        df = pd.DataFrame({
            'Año': anios,
            'Valor': valores
        })

        # Crear gráfico de barras
        fig = px.bar(df, x='Año', y='Valor',
                    title=titulo,
                    labels={'Año': 'Año', 'Valor': yaxis_title}
        )

        # Mejorar el diseño
        fig.update_layout(
            margin=dict(l=40, r=40, t=80, b=160),
            xaxis_title='Año',
            yaxis_title=yaxis_title,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(
                family='Inter',
                size=14,
                color='rgb(33, 37, 41)'
            ),
            xaxis=dict(
                type='category',
                tickmode='array',
                tickvals=[1990, 1995, 2000, 2005, 2010, 2015, 2020, 2025],
                ticktext=['1990', '1995', '2000', '2005', '2010', '2015', '2020', '2025']
            ),
            yaxis=dict(
                tickformat=',.1f',  # Formato de números con 1 decimal
                tickangle=0
            ),
            annotations=[
                crear_pie_pagina(
                    titulo,
                    f"Evolución de {titulo.lower()} a lo largo del tiempo (quinquenios 1990-2025).",
                    serie.entidad_recopilatoria if serie else 'Sin especificar',
                    serie.fuente_datos if serie and serie.fuente_datos else 'indicadores.cali.gov.co'
                )
            ]
        )

        # Actualizar el color de las barras
        fig.update_traces(
            marker_color='#4299e1',
            text=[f'{v:.1f} {unidad_medida}' for v in valores],
            textposition='auto',
            textangle=0
        )

        return fig.to_dict()

    except Exception as e:
        print(f"Error al crear el gráfico {indicador_nombre}: {str(e)}")
        return None

def crear_grafico_lineas(indicador_nombre, titulo, yaxis_title, unidad_medida):
    """
    Crea un gráfico de líneas para un indicador específico.

    Args:
        indicador_nombre: Nombre del indicador (ej: 'SIS_4_T3_I9')
        titulo: Título del gráfico
        yaxis_title: Título del eje Y
        unidad_medida: Unidad de medida del indicador

    Returns:
        Diccionario con los datos del gráfico en formato JSON
    """
    try:
        # Obtener el indicador
        indicador = Indicador.objects.get(nombre=indicador_nombre)

        # Obtener la serie de datos
        serie = SerieDatos.objects.filter(
            indicador=indicador,
            desagregacion_geografica='Cali'
        ).first()

        if not serie:
            return None

        # Obtener los datos
        datos = Dato.objects.filter(serie_datos=serie).order_by('fecha_dato')

        # Crear listas para los datos
        anios = []
        valores = []

        # Agrupar datos por quinquenios desde 1990 hasta 2025
        for dato in datos:
            anio = dato.fecha_dato.year
            if 1990 <= anio <= 2025:  # Solo considerar años desde 1990 hasta 2025
                anios.append(anio)
                valores.append(float(dato.valor_dato))

        # Crear DataFrame
        df = pd.DataFrame({
            'Año': anios,
            'Valor': valores
        })

        # Crear gráfico de líneas
        fig = px.line(df, x='Año', y='Valor',
                    title=titulo,
                    labels={'Año': 'Año', 'Valor': yaxis_title}
        )

        # Mejorar el diseño
        fig.update_layout(
            margin=dict(l=40, r=40, t=80, b=160),
            xaxis_title='Año',
            yaxis_title=yaxis_title,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(
                family='Inter',
                size=14,
                color='rgb(33, 37, 41)'
            ),
            xaxis=dict(
                type='category',
                tickmode='array',
                tickvals=[1990, 1995, 2000, 2005, 2010, 2015, 2020, 2025],
                ticktext=['1990', '1995', '2000', '2005', '2010', '2015', '2020', '2025']
            ),
            yaxis=dict(
                tickformat=',.1f',  # Formato de números con 1 decimal
                tickangle=0
            ),
            annotations=[
                crear_pie_pagina(
                    titulo,
                    f"Evolución de {titulo.lower()} a lo largo del tiempo (quinquenios 1990-2025).",
                    serie.entidad_recopilatoria if serie else 'Sin especificar',
                    serie.fuente_datos if serie and serie.fuente_datos else 'indicadores.cali.gov.co'
                )
            ]
        )

        # Actualizar el color de la línea y los puntos
        fig.update_traces(
            line_color='#4299e1',
            line_width=2,
            mode='lines+markers',
            marker=dict(
                size=8,
                color='#4299e1'
            ),
            # Solo mostrar puntos en los años quinquenales
            hovertemplate='Año: %{x}<br>Valor: %{y:.1f} ' + unidad_medida,
            # Personalizar los puntos para que solo aparezcan en los años quinquenales
            marker_symbol=np.where(np.isin(df['Año'], [1990, 1995, 2000, 2005, 2010, 2015, 2020, 2025]), 'circle', 'x'),
            marker_size=np.where(np.isin(df['Año'], [1990, 1995, 2000, 2005, 2010, 2015, 2020, 2025]), 10, 0)
        )

        return fig.to_dict()

    except Exception as e:
        print(f"Error al crear el gráfico {indicador_nombre}: {str(e)}")
        return None

def home(request):
    # Crear mapa base centrado en Cali, Colombia (3.4516° N, 76.5320° W)
    m = folium.Map(
        location=[3.4, -76.5],
        zoom_start=12,
        tiles='CartoDB Positron',
        control_scale=True,
        scrollWheelZoom=False
    )

    # Script para asegurar que el scroll no sea interceptado por el mapa
    scroll_script = """
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        // Deshabilitar completamente el zoom con rueda en todos los mapas Leaflet
        let maps = document.querySelectorAll('.leaflet-container');
        maps.forEach(function(map) {
            map.style.scrollBehavior = 'auto';
            map.addEventListener('wheel', function(e) {
                e.stopPropagation();
            });
        });
    });
    </script>
    """
    m.get_root().html.add_child(folium.Element(scroll_script))

    # Añadir un título al mapa
    title_html = '''
    <div style="
        position: fixed;
        top: 10px;
        left: 50px;
        width: 250px;
        height: 40px;
        z-index: 9999;
        font-size: 16px;
        font-weight: bold;
        color: #333;
        background-color: white;
        border-radius: 8px;
        box-shadow: 0 0 15px rgba(0, 0, 0, 0.1);
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 10px;
        border-left: 4px solid #4299e1;
    ">
        Sistema de Información Geográfica
    </div>
    '''
    m.get_root().html.add_child(folium.Element(title_html))

    # Añadir comunas
    comunas = Comuna.objects.all()

    for comuna in comunas:
        datos_comuna = comuna.datos_comuna()
        try:
            # Convertir el campo geom a un formato GeoJSON adecuado
            geom_json = json.loads(comuna.geom.json)

            geojson = {
                "type": "Feature",
                "geometry": geom_json,
                "properties": {
                    "comuna_id": comuna.comuna_id,
                    "nombre": comuna.nombre,
                    "area": comuna.area,
                    "perimetro": comuna.perimetro,
                    "datos": datos_comuna
                }
            }

            # Crear popup con información de la comuna con estilo moderno
            popup_content = f"""
            <div style="font-family: system-ui, -apple-system, sans-serif; max-width: 600px; padding: 10px;">
                <div style="display: flex; align-items: center; margin-bottom: 15px; border-bottom: 2px solid #4299e1; padding-bottom: 10px;">
                    <div style="background-color: #4299e1; color: white; width: 40px; height: 40px; border-radius: 50%; display: flex; justify-content: center; align-items: center; margin-right: 10px; font-weight: bold;">{comuna.comuna_id}</div>
                    <h3 style="margin: 0; color: #2d3748; font-size: 18px;">{comuna.nombre}</h3>
                </div>

                <div style="display: flex; flex-wrap: wrap; gap: 10px; margin-bottom: 15px;">
                    <div style="background-color: #ebf8ff; border-left: 4px solid #4299e1; padding: 8px; border-radius: 4px; flex: 1;">
                        <div style="font-size: 12px; color: #718096;">Área</div>
                        <div style="font-weight: bold; color: #2b6cb0;">{comuna.area:.2f} metros cuadrados</div>
                    </div>
                    <div style="background-color: #ebf8ff; border-left: 4px solid #4299e1; padding: 8px; border-radius: 4px; flex: 1;">
                        <div style="font-size: 12px; color: #718096;">Perímetro</div>
                        <div style="font-weight: bold; color: #2b6cb0;">{comuna.perimetro:.2f} metros</div>
                    </div>
                </div>

                <h4 style="color: #2d3748; margin-top: 15px; margin-bottom: 10px; font-size: 16px;">Indicadores Principales</h4>
                <div style='max-height: 400px; overflow-y: auto;'>
                    <table style='border-collapse: collapse; width: 100%; border-radius: 8px; overflow: hidden;'>
                        <thead>
                            <tr style="background-color: #4299e1; color: white;">
                                <th style='padding: 10px; text-align: left;'>Indicador</th>
                                <th style='padding: 10px; text-align: center;'>Valor</th>
                                <th style='padding: 10px; text-align: center;'>Año</th>
                            </tr>
                        </thead>
                        <tbody>
            """

            # Agregar lista de indicadores con filas alternadas
            for i, dato in enumerate(datos_comuna):
                bg_color = "#f7fafc" if i % 2 == 0 else "white"
                popup_content += f"""
                <tr style="background-color: {bg_color};">
                    <td style='padding: 8px; border-bottom: 1px solid #e2e8f0;'>{dato['indicador_nombre']}</td>
                    <td style='padding: 8px; text-align: center; font-weight: bold; border-bottom: 1px solid #e2e8f0;'>{dato['valor_dato']} {dato['unidad_medida']}</td>
                    <td style='padding: 8px; text-align: center; color: #718096; border-bottom: 1px solid #e2e8f0;'>{dato['fecha_dato']}</td>
                </tr>
                """

            popup_content += """
                        </tbody>
                    </table>
                </div>
            </div>
            """
            popup = folium.Popup(popup_content, max_width=600)

            # Definir colores basados en el ID de la comuna para tener variedad
            color_options = [
                '#4299e1', '#48bb78', '#9f7aea', '#ed8936', '#f56565',
                '#38b2ac', '#ecc94b', '#667eea', '#ed64a6', '#48bb78'
            ]
            comuna_color = color_options[comuna.comuna_id % len(color_options)]

            # Añadir el GeoJSON al mapa con estilo moderno
            folium.GeoJson(
                data=geojson,
                style_function=lambda x: {
                    'fillColor': comuna_color,
                    'color': '#2d3748',
                    'weight': 1.5,
                    'fillOpacity': 0.5,
                    'dashArray': '3'
                },
                highlight_function=lambda x: {
                    'fillColor': comuna_color,
                    'color': '#1a202c',
                    'weight': 3,
                    'fillOpacity': 0.7,
                    'dashArray': '0'
                },
                tooltip=folium.Tooltip(
                    f"<div style='font-family: system-ui, -apple-system, sans-serif; font-weight: 600; color: #2d3748;'>{comuna.nombre}</div>"
                ),
                popup=popup
            ).add_to(m)

        except Exception as e:
            print(f"Error al procesar la comuna {comuna.nombre}: {str(e)}")

    # No se añade control de capas para mantener una interfaz más limpia

    # Convertir mapa a HTML
    mapa_html = m._repr_html_()

    # Pasar el mapa al template
    return render(request, 'home.html', {'mapa_html': mapa_html})

def poblacion(request):
    try:
        # Obtener el indicador SIS_4_T3_I1 para el gráfico de barras
        indicador_barras = Indicador.objects.get(nombre='SIS_4_T3_I1')

        # Obtener las series de datos para Cali
        series_cali = SerieDatos.objects.filter(
            indicador=indicador_barras,
            desagregacion_geografica='Cali'
        )

        # Obtener los datos para los años específicos (sin 1990)
        anios_especificos = [1985, 1995, 2000, 2005, 2010, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]

        # Diccionario para almacenar el valor más alto por año
        datos_por_anio = {}

        for serie in series_cali:
            datos = Dato.objects.filter(
                serie_datos=serie,
                fecha_dato__year__in=anios_especificos
            ).order_by('fecha_dato')

            for dato in datos:
                if dato.fecha_dato.year in anios_especificos:
                    anio = dato.fecha_dato.year
                    valor = float(dato.valor_dato)

                    # Si el año ya existe, mantener el valor más alto
                    if anio in datos_por_anio:
                        datos_por_anio[anio] = max(datos_por_anio[anio], valor)
                    else:
                        datos_por_anio[anio] = valor

        # Crear listas para los datos del gráfico de barras
        anios = []
        poblacion = []

        # Asegurarse de que todos los años tengan una entrada
        for anio in sorted(anios_especificos):
            anios.append(anio)
            poblacion.append(datos_por_anio.get(anio, 0))

        # Crear DataFrame para el gráfico de barras
        df_barras = pd.DataFrame({
            'Año': anios,
            'Población': poblacion
        })

        # Crear gráfico de barras
        fig_barras = px.bar(df_barras, x='Año', y='Población',
                           title='Población de Cali por Año',
                           labels={'Año': 'Año', 'Población': 'Población'}
        )

        # Obtener información de la serie de datos
        serie_info = series_cali.first() if series_cali else None

        # Mejorar el diseño del gráfico de barras
        fig_barras.update_layout(
            margin=dict(l=40, r=40, t=80, b=160),  # Aumentar el margen inferior para el pie de página
            xaxis_title='Año',
            yaxis_title='Población',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(
                family='Inter',
                size=14,
                color='rgb(33, 37, 41)'
            ),
            xaxis=dict(
                type='category',
                tickmode='array',
                tickvals=anios,
                ticktext=[str(a) for a in anios]
            ),
            yaxis=dict(
                tickformat=',.0f',  # Formato de números con separadores de miles
                tickangle=0  # Texto vertical en el eje Y
            ),
            annotations=[
                crear_pie_pagina(
                    "Población total de Cali",
                    "Evolución de la población total de Santiago de Cali a lo largo del tiempo.",
                    serie_info.entidad_recopilatoria if serie_info else 'Sin especificar',
                    serie_info.fuente_datos if serie_info and serie_info.fuente_datos else 'indicadores.cali.gov.co'
                )
            ]
        )

        # Actualizar el color de las barras a azul
        fig_barras.update_traces(
            marker_color='#4299e1',
            text=[f'{int(p):,}' for p in poblacion],  # Formatear con separadores de miles
            textposition='auto',
            textangle=0  # Texto vertical en las barras
        )

        # Obtener el indicador SIS_4_T3_I3 para la pirámide poblacional
        indicador_piramide = Indicador.objects.get(nombre='SIS_4_T3_I3')

        # Obtener las series de datos para Cali
        series_cali_piramide = SerieDatos.objects.filter(
            indicador=indicador_piramide,
            desagregacion_geografica='Cali'
        ).order_by('desagregacion_tematica')

        # Diccionarios para almacenar los datos por grupo de edad
        datos_hombres_dict = {}
        datos_mujeres_dict = {}

        # Diccionarios para almacenar los datos más recientes por grupo de edad
        datos_hombres_recientes = {}
        datos_mujeres_recientes = {}

        # Variable para almacenar el año de los datos
        anio_datos = 2025

        # Patrón para identificar los grupos de edad
        patron_edades = ['0-4', '5-9', '10-14', '15-19', '20-24', '25-29', '30-34', '35-39',
                         '40-44', '45-49', '50-54', '55-59', '60-64', '65-69', '70-74',
                         '75-79', '80 y más']

        # Imprimir todas las desagregaciones temáticas disponibles para depuración
        print("Desagregaciones temáticas disponibles:")
        desagregaciones_disponibles = set()
        for serie in series_cali_piramide:
            desagregacion = serie.desagregacion_tematica
            desagregaciones_disponibles.add(desagregacion)
            print(f"- {desagregacion}")

        # Obtener el total de población del año 2025
        total_poblacion_2025 = 0
        try:
            # Buscar la serie de datos para Total Hombres
            serie_hombres_total = SerieDatos.objects.get(
                indicador=indicador_piramide,
                desagregacion_geografica='Cali',
                desagregacion_tematica='Total Hombres'
            )
            datos_hombres_total = Dato.objects.filter(
                serie_datos=serie_hombres_total,
                fecha_dato__year=2025
            ).order_by('-fecha_dato')

            # Buscar la serie de datos para Total Mujeres
            serie_mujeres_total = SerieDatos.objects.get(
                indicador=indicador_piramide,
                desagregacion_geografica='Cali',
                desagregacion_tematica='Total Mujeres'
            )
            datos_mujeres_total = Dato.objects.filter(
                serie_datos=serie_mujeres_total,
                fecha_dato__year=2025
            ).order_by('-fecha_dato')

            if datos_hombres_total.exists() and datos_mujeres_total.exists():
                total_hombres = float(datos_hombres_total.first().valor_dato)
                total_mujeres = float(datos_mujeres_total.first().valor_dato)
                total_poblacion_2025 = total_hombres + total_mujeres
                print(f"Total de población 2025: {total_poblacion_2025} (Hombres: {total_hombres}, Mujeres: {total_mujeres})")
            else:
                print("No se encontraron datos para Total Hombres o Total Mujeres")
        except SerieDatos.DoesNotExist:
            print("No se encontró la serie de datos para Total Hombres o Total Mujeres")

        # Procesar cada serie de datos para la pirámide
        for serie in series_cali_piramide:
            # Obtener los datos específicamente del año 2025
            datos_serie = Dato.objects.filter(
                serie_datos=serie,
                fecha_dato__year=2025
            ).order_by('-fecha_dato')
            if datos_serie.exists():
                # Tomar el dato más reciente del año 2025
                dato = datos_serie.first()
                desagregacion = serie.desagregacion_tematica
                print(f"Procesando: {desagregacion}, valor: {dato.valor_dato}, fecha: {dato.fecha_dato}")

                # Verificar que realmente es del año 2025
                if dato.fecha_dato.year == 2025:
                    # Procesar datos para hombres
                    if 'Hombres' in desagregacion:
                        # Verificar primero casos especiales por nombre exacto
                        if desagregacion == '40-44 Hombres':
                            edad_encontrada = '40-44'
                            print(f"*** Asignando hombres directamente a 40-44 - valor: {dato.valor_dato}")
                        else:
                            # Buscar la edad usando una expresión regular más precisa
                            edad_encontrada = None
                            for edad in patron_edades:
                                if edad == '80 y más':
                                    if re.search(r'80 y más', desagregacion, re.IGNORECASE):
                                        edad_encontrada = edad
                                        break
                                # Manejo especial para '40-44'
                                elif edad == '40-44':
                                    if desagregacion.startswith('40-') or desagregacion.startswith('40 ') or re.search(r'^40', desagregacion):
                                        edad_encontrada = edad
                                        print(f"*** Detectado 40-44 usando regex - valor: {dato.valor_dato}")
                                        break
                                elif edad in desagregacion:
                                    edad_encontrada = edad
                                    break

                        if edad_encontrada and desagregacion != 'Total Hombres':
                            valor = float(dato.valor_dato)
                            # Convertir a porcentaje si hay total de población
                            if total_poblacion_2025 > 0:
                                valor_porcentaje = (valor / total_poblacion_2025) * 100
                                print(f"Agregando hombre para edad {edad_encontrada}: {valor_porcentaje:.2f}%")
                                datos_hombres_recientes[edad_encontrada] = valor_porcentaje

                    # Procesar datos para mujeres
                    elif 'Mujeres' in desagregacion:
                        # Verificar primero casos especiales por nombre exacto
                        if desagregacion == '40-44 Mujeres':
                            edad_encontrada = '40-44'
                            print(f"*** Asignando mujeres directamente a 40-44 - valor: {dato.valor_dato}")
                        else:
                            # Buscar la edad usando una expresión regular más precisa
                            edad_encontrada = None
                            for edad in patron_edades:
                                if edad == '80 y más':
                                    if re.search(r'80 y más', desagregacion, re.IGNORECASE):
                                        edad_encontrada = edad
                                        break
                                # Manejo especial para '40-44'
                                elif edad == '40-44':
                                    if desagregacion.startswith('40-') or desagregacion.startswith('40 ') or re.search(r'^40', desagregacion):
                                        edad_encontrada = edad
                                        print(f"*** Detectado 40-44 usando regex - valor: {dato.valor_dato}")
                                        break
                                elif edad in desagregacion:
                                    edad_encontrada = edad
                                    break

                        if edad_encontrada and desagregacion != 'Total Mujeres':
                            valor = float(dato.valor_dato)
                            # Convertir a porcentaje si hay total de población
                            if total_poblacion_2025 > 0:
                                valor_porcentaje = (valor / total_poblacion_2025) * 100
                                print(f"Agregando mujer para edad {edad_encontrada}: {valor_porcentaje:.2f}%")
                                datos_mujeres_recientes[edad_encontrada] = valor_porcentaje

        # Convertir los datos más recientes a los diccionarios finales
        for edad in patron_edades:
            # Obtener los valores (ya convertidos a porcentajes)
            valor_hombres = datos_hombres_recientes.get(edad, 0)
            valor_mujeres = datos_mujeres_recientes.get(edad, 0)

            datos_hombres_dict[edad] = valor_hombres
            datos_mujeres_dict[edad] = valor_mujeres

            # Imprimir los valores finales para depuración
            print(f"Edad: {edad}, Hombres: {valor_hombres:.2f}%, Mujeres: {valor_mujeres:.2f}%")

        # Crear listas ordenadas para el gráfico
        edades = patron_edades
        hombres = [datos_hombres_dict.get(edad, 0) for edad in edades]
        mujeres = [datos_mujeres_dict.get(edad, 0) for edad in edades]

        # Crear DataFrame para la pirámide con los datos en porcentaje
        df_piramide = pd.DataFrame({
            'Edad': list(datos_hombres_recientes.keys()),
            'Hombres': list(datos_hombres_recientes.values()),
            'Mujeres': list(datos_mujeres_recientes.values())
        })

        # Crear la pirámide poblacional con porcentajes
        fig_piramide = go.Figure()

        # Obtener información de la serie de datos
        serie_info = series_cali_piramide.first() if series_cali_piramide else None

        # Agregar barras para hombres (negativas)
        fig_piramide.add_trace(go.Bar(
            x=[-x for x in df_piramide['Hombres']],
            y=df_piramide['Edad'],
            name='Hombres',
            orientation='h',
            marker_color='#4299e1',
            text=[f'{x:.1f}%' for x in df_piramide['Hombres']],
            textposition='auto',
            hovertemplate='%{y}<br>Hombres: %{x:,.1f}%<extra></extra>'
        ))

        # Agregar barras para mujeres (positivas)
        fig_piramide.add_trace(go.Bar(
            x=df_piramide['Mujeres'],
            y=df_piramide['Edad'],
            name='Mujeres',
            orientation='h',
            marker_color='#dc2626',
            text=[f'{x:.1f}%' for x in df_piramide['Mujeres']],
            textposition='auto',
            hovertemplate='%{y}<br>Mujeres: %{x:,.1f}%<extra></extra>'
        ))

        # Mejorar el diseño de la pirámide
        fig_piramide.update_layout(
            margin=dict(l=40, r=40, t=80, b=160),  # Aumentar el margen inferior para el pie de página
            title='Pirámide Poblacional de Cali (2025)',
            xaxis_title='Porcentaje de la Población',
            yaxis_title='Edad',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(
                family='Inter',
                size=14,
                color='rgb(33, 37, 41)'
            ),
            barmode='relative',
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            xaxis=dict(
                tickformat='.1f%',
                range=[-9, 9],  # Ajustado a 5%
                tickvals=[-9, -8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
                ticktext=['9%','8%','7%','6%','5%', '4%', '3%', '2%', '1%', '0%', '1%', '2%', '3%', '4%', '5%', '6%', '7%', '8%', '9%']
            ),
            yaxis=dict(
                tickangle=0,
                tickfont=dict(
                    size=12
                )
            ),
            annotations=[
                crear_pie_pagina(
                    "Pirámide poblacional por sexo y edad",
                    "Distribución de la población de Cali por sexo y grupos etarios quinquenales.",
                    serie_info.entidad_recopilatoria if serie_info else 'Sin especificar',
                    serie_info.fuente_datos if serie_info and serie_info.fuente_datos else 'indicadores.cali.gov.co'
                )
            ]
        )

        # Convertir la pirámide a JSON
        chart_json_piramide = json.dumps(fig_piramide, cls=PlotlyJSONEncoder)

        # Obtener los años específicos del primer gráfico
        anios_especificos = [1985, 1995, 2000, 2005, 2010, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]

        # Crear un índice numérico para los años que será usado en el eje X
        indices = list(range(len(anios_especificos)))

        # Obtener datos para hombres
        datos_hombres = []
        for anio in anios_especificos:
            try:
                serie_hombres = SerieDatos.objects.get(
                    indicador=indicador_piramide,
                    desagregacion_geografica='Cali',
                    desagregacion_tematica='Total Hombres'
                )
                dato = Dato.objects.filter(
                    serie_datos=serie_hombres,
                    fecha_dato__year=anio
                ).order_by('-fecha_dato').first()
                if dato:
                    datos_hombres.append(float(dato.valor_dato))
                else:
                    datos_hombres.append(0)
            except SerieDatos.DoesNotExist:
                datos_hombres.append(0)

        # Obtener datos para mujeres
        datos_mujeres = []
        for anio in anios_especificos:
            try:
                serie_mujeres = SerieDatos.objects.get(
                    indicador=indicador_piramide,
                    desagregacion_geografica='Cali',
                    desagregacion_tematica='Total Mujeres'
                )
                dato = Dato.objects.filter(
                    serie_datos=serie_mujeres,
                    fecha_dato__year=anio
                ).order_by('-fecha_dato').first()
                if dato:
                    datos_mujeres.append(float(dato.valor_dato))
                else:
                    datos_mujeres.append(0)
            except SerieDatos.DoesNotExist:
                datos_mujeres.append(0)

        # Calcular porcentajes
        porcentajes_hombres = []
        porcentajes_mujeres = []

        for i in range(len(anios_especificos)):
            total_poblacion = datos_hombres[i] + datos_mujeres[i]
            if total_poblacion > 0:
                porcentaje_hombres = (datos_hombres[i] / total_poblacion) * 100
                porcentaje_mujeres = (datos_mujeres[i] / total_poblacion) * 100
                porcentajes_hombres.append(porcentaje_hombres)
                porcentajes_mujeres.append(porcentaje_mujeres)
            else:
                porcentajes_hombres.append(0)
                porcentajes_mujeres.append(0)

        # Crear barras para hombres
        fig_poblacion_sexo = go.Figure()
        fig_poblacion_sexo.add_trace(go.Bar(
            x=indices,
            y=porcentajes_hombres,
            name='Hombres',
            marker_color='#4299e1',
            text=[f'{h:.1f}%' for h in porcentajes_hombres],
            textposition='auto',
            hovertemplate='Año: %{customdata}<br>Hombres: %{y:.1f}%<extra></extra>',
            customdata=anios_especificos
        ))

        # Crear barras para mujeres
        fig_poblacion_sexo.add_trace(go.Bar(
            x=indices,
            y=porcentajes_mujeres,
            name='Mujeres',
            marker_color='#dc2626',
            text=[f'{m:.1f}%' for m in porcentajes_mujeres],
            textposition='auto',
            hovertemplate='Año: %{customdata}<br>Mujeres: %{y:.1f}%<extra></extra>',
            customdata=anios_especificos
        ))

        # Mejorar el diseño del gráfico
        fig_poblacion_sexo.update_layout(
            title='Distribución porcentual de la Población por Sexo (1985-2024)',
            xaxis_title='Año',
            yaxis_title='Porcentaje de la Población',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(
                family='Inter',
                size=14,
                color='rgb(33, 37, 41)'
            ),
            margin=dict(l=40, r=40, t=80, b=160),  # Aumentar el margen inferior para el pie de página
            barmode='group',
            bargap=0.3,
            bargroupgap=0.15,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            yaxis=dict(
                tickformat='.1f%',  # Formato de números con 1 decimal
                range=[0, 60]  # Ajustado a 60%
            ),
            xaxis=dict(
                tickmode='array',
                tickvals=indices,
                ticktext=anios_especificos,
                tickangle=45
            ),
            annotations=[
                crear_pie_pagina(
                    "Distribución de población por sexo",
                    "Evolución del porcentaje de hombres y mujeres en la población de Cali a lo largo del tiempo.",
                    'DANE',
                    'Proyecciones de población - indicadores.cali.gov.co'
                )
            ]
        )

        # Convertir el gráfico a JSON
        chart_json_poblacion_sexo = json.dumps(fig_poblacion_sexo, cls=PlotlyJSONEncoder)

        # Obtener el indicador SIS_4_T3_I3 para el gráfico de edades
        indicador_edades = Indicador.objects.get(nombre='SIS_4_T3_I3')

        # Obtener las series de datos quinquenales (sin 'Hombres' ni 'Mujeres' en el nombre)
        series_cali_edades = []
        todas_series = SerieDatos.objects.filter(
            indicador=indicador_edades,
            desagregacion_geografica='Cali'
        ).order_by('desagregacion_tematica')

        # Filtrar para incluir solo grupos quinquenales
        for serie in todas_series:
            tema = serie.desagregacion_tematica
            if 'Hombres' not in tema and 'Mujeres' not in tema and tema != 'Total':
                series_cali_edades.append(serie)

        # Imprimir series para depuración
        print("Series quinquenales:")
        for serie in series_cali_edades[:5]:  # Mostrar las primeras 5 para diagnóstico
            print(f"- {serie.desagregacion_tematica}")

        # Obtener los datos para el año 2025
        anio_datos = 2025
        datos_edades = []
        edades = []

        for serie in series_cali_edades:
            try:
                dato = Dato.objects.get(
                    serie_datos=serie,
                    fecha_dato__year=anio_datos
                )
                # Limpiar el nombre de la edad
                edad = serie.desagregacion_tematica
                # Normalizar algunos formatos para mejor visualización
                if edad == '05-09':
                    edad = '5-9'
                elif edad == '80 y más':
                    edad = '80+'

                edades.append(edad)
                datos_edades.append(float(dato.valor_dato))
                print(f"Agregando edad {edad}: {float(dato.valor_dato)}")
            except Dato.DoesNotExist:
                print(f"No hay datos para {serie.desagregacion_tematica} en {anio_datos}")

        # Calcular el total de población por edades
        total_poblacion_edades = sum(datos_edades)

        # Calcular los porcentajes
        porcentajes_edades = [100 * valor / total_poblacion_edades for valor in datos_edades]

        # Crear el gráfico de barras para población por edades (en porcentajes)
        fig_edades = go.Figure()

        # Obtener información de la serie de datos
        serie_info = series_cali_edades[0] if series_cali_edades else None

        fig_edades.add_trace(go.Bar(
            x=edades,
            y=porcentajes_edades,
            marker_color='#4299e1',
            text=[f'{p:.1f}%' for p in porcentajes_edades],
            textposition='auto',
            hovertemplate='Edad: %{x}<br>Porcentaje: %{y:.1f}%<extra></extra>'
        ))

        # Mejorar el diseño del gráfico de edades
        fig_edades.update_layout(
            margin=dict(l=40, r=40, t=80, b=160),  # Aumentar el margen inferior para el pie de página
            title='Distribución de Población por Edades (2025)',
            xaxis_title='Grupo de Edad',
            yaxis_title='Porcentaje de la Población (%)',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(
                family='Inter',
                size=14,
                color='rgb(33, 37, 41)'
            ),
            xaxis=dict(
                tickangle=45,
                tickfont=dict(size=12)
            ),
            yaxis=dict(
                tickformat='.1f',
                tickfont=dict(size=12)
            ),
            annotations=[
                crear_pie_pagina(
                    "Distribución poblacional por edades",
                    "Porcentaje del total de población que reside en cada grupo de edad de la ciudad.",
                    series_cali_edades[0].entidad_recopilatoria if series_cali_edades else 'Sin especificar',
                    series_cali_edades[0].fuente_datos if series_cali_edades and series_cali_edades[0].fuente_datos else 'indicadores.cali.gov.co'
                )
            ]
        )

        # Convertir el gráfico de edades a JSON
        chart_json_edades = json.dumps(fig_edades, cls=PlotlyJSONEncoder)

        # Obtener el indicador SIS_4_T3_I4 para la tasa de crecimiento demográfico
        indicador_tasa = Indicador.objects.get(nombre='SIS_4_T3_I4')

        # Obtener la serie de datos para Cali
        serie_tasa = SerieDatos.objects.filter(
            indicador=indicador_tasa,
            desagregacion_geografica='Cali'
        ).first()

        # Obtener los datos de la serie
        if serie_tasa:
            datos_tasa = Dato.objects.filter(
                serie_datos=serie_tasa
            ).order_by('fecha_dato')

            # Crear listas para los datos
            anios = []
            tasas = []

            for dato in datos_tasa:
                anios.append(dato.fecha_dato.year)
                tasas.append(float(dato.valor_dato))

            # Crear el gráfico de línea para la tasa de crecimiento
            fig_tasa = go.Figure()

            fig_tasa.add_trace(go.Scatter(
                x=anios,
                y=tasas,
                mode='lines+markers',
                line=dict(color='#4299e1', width=2),
                marker=dict(size=8),
                hovertemplate='Año: %{x}<br>Tasa: %{y:.2f}%<extra></extra>'
            ))

            # Mejorar el diseño del gráfico de tasa
            fig_tasa.update_layout(
                margin=dict(l=40, r=40, t=80, b=160),  # Aumentar el margen inferior para el pie de página
                title='Tasa de Crecimiento Demográfico',
                xaxis_title='Año',
                yaxis_title='Tasa de Crecimiento (%)',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(
                    family='Inter',
                    size=14,
                    color='rgb(33, 37, 41)'
                ),
                xaxis=dict(
                    tickfont=dict(size=12)
                ),
                yaxis=dict(
                    tickformat='.1f%',
                    tickfont=dict(size=12)
                ),
                annotations=[
                    crear_pie_pagina(
                        "Tasa de crecimiento poblacional",
                        "Variación porcentual anual de la población total de la ciudad.",
                        serie_tasa.entidad_recopilatoria if serie_tasa else 'Sin especificar',
                        serie_tasa.fuente_datos if serie_tasa and serie_tasa.fuente_datos else 'indicadores.cali.gov.co'
                    )
                ]
            )

            # Convertir el gráfico de tasa a JSON
            chart_json_tasa = json.dumps(fig_tasa, cls=PlotlyJSONEncoder)
        else:
            chart_json_tasa = None

        # Obtener el indicador SIS_4_T3_I6 para el gráfico de comunas
        try:
            indicador_comunas = Indicador.objects.get(nombre='SIS_4_T3_I6')
            print(f"Indicador de comunas encontrado: {indicador_comunas}")

            # Ver todas las series para este indicador
            todas_series = SerieDatos.objects.filter(indicador=indicador_comunas)
            print(f"Total de series para indicador SIS_4_T3_I6: {todas_series.count()}")

            # Ver desagregaciones geográficas disponibles
            desagregaciones_geo = todas_series.values_list('desagregacion_geografica', flat=True).distinct()
            print(f"Desagregaciones geográficas: {list(desagregaciones_geo)}")

            # Ver desagregaciones temáticas disponibles
            desagregaciones_tem = todas_series.values_list('desagregacion_tematica', flat=True).distinct()
            print(f"Desagregaciones temáticas: {list(desagregaciones_tem)}")

            # Determinar el año más reciente con datos disponibles
            anio_datos_disponible = Dato.objects.filter(
                serie_datos__indicador=indicador_comunas
            ).values_list('fecha_dato__year', flat=True).distinct().order_by('-fecha_dato__year').first()

            print(f"Año más reciente con datos: {anio_datos_disponible}")

            # Si no hay años con datos disponibles, usar datos de muestra
            if not anio_datos_disponible:
                print("No hay datos reales, usando datos de muestra")
                anio_datos = 2024  # Año de muestra
                # Datos de muestra - población estimada por comuna
                datos_muestra = {
                    'Comuna 1': 89500,
                    'Comuna 2': 106200,
                    'Comuna 3': 44900,
                    'Comuna 4': 53600,
                    'Comuna 5': 112500,
                    'Comuna 6': 188100,
                    'Comuna 7': 72500,
                    'Comuna 8': 103400,
                    'Comuna 9': 45200,
                    'Comuna 10': 112300,
                    'Comuna 11': 108600,
                    'Comuna 12': 66100,
                    'Comuna 13': 178300,
                    'Comuna 14': 169600,
                    'Comuna 15': 162100,
                    'Comuna 16': 107500,
                    'Comuna 17': 144000,
                    'Comuna 18': 127200,
                    'Comuna 19': 112500,
                    'Comuna 20': 68800,
                    'Comuna 21': 120300,
                    'Comuna 22': 13100
                }
                comunas = list(datos_muestra.keys())
                poblaciones = list(datos_muestra.values())
            else:
                # Usar el año con datos disponibles
                anio_datos = anio_datos_disponible

                # Obtener las series de datos para las comunas
                series_comunas = SerieDatos.objects.filter(
                    indicador=indicador_comunas
                ).order_by('desagregacion_geografica')

                # Imprimir información de las series encontradas
                print(f"Series de comunas encontradas: {series_comunas.count()}")
                for i, serie in enumerate(series_comunas[:5]):  # Mostrar las primeras 5 para diagnóstico
                    print(f"Serie {i+1}: nombre={serie.nombre}, geo={serie.desagregacion_geografica}, tema={serie.desagregacion_tematica}")

                # Crear listas para almacenar los datos
                comunas = []
                poblaciones = []
                poblacion_corregimientos = 0

                # Obtener datos para el año disponible
                for serie in series_comunas:
                    try:
                        dato = Dato.objects.filter(
                            serie_datos=serie,
                            fecha_dato__year=anio_datos
                        ).order_by('-fecha_dato').first()

                        if dato:
                            # Obtener el nombre de la comuna
                            nombre_comuna = serie.desagregacion_geografica

                            # Verificar si es comuna o corregimiento
                            if 'Comuna' in nombre_comuna:
                                # Es una comuna
                                comunas.append(nombre_comuna)
                                poblaciones.append(float(dato.valor_dato))
                                print(f"Agregando datos para {nombre_comuna}: {float(dato.valor_dato)}")
                            else:
                                # Es un corregimiento, sumar a la población total de corregimientos
                                poblacion_corregimientos += float(dato.valor_dato)
                                print(f"Sumando corregimiento {nombre_comuna}: {float(dato.valor_dato)}")
                        else:
                            print(f"No se encontraron datos para la serie {serie.nombre} en {anio_datos}")
                    except Exception as e:
                        print(f"Error procesando la serie {serie.nombre}: {str(e)}")

                # Agregar la suma de corregimientos como una barra adicional
                if poblacion_corregimientos > 0:
                    comunas.append('Corregimientos')
                    poblaciones.append(poblacion_corregimientos)
                    print(f"Total población de corregimientos: {poblacion_corregimientos}")

                # Si no se encontraron datos reales, usar datos de muestra
                if not comunas:
                    print("No se encontraron datos suficientes, usando datos de muestra")
                    # Datos de muestra - población estimada por comuna
                    datos_muestra = {
                        'Comuna 1': 89500,
                        'Comuna 2': 106200,
                        'Comuna 3': 44900,
                        'Comuna 4': 53600,
                        'Comuna 5': 112500,
                        'Comuna 6': 188100,
                        'Comuna 7': 72500,
                        'Comuna 8': 103400,
                        'Comuna 9': 45200,
                        'Comuna 10': 112300,
                        'Comuna 11': 108600,
                        'Comuna 12': 66100,
                        'Comuna 13': 178300,
                        'Comuna 14': 169600,
                        'Comuna 15': 162100,
                        'Comuna 16': 107500,
                        'Comuna 17': 144000,
                        'Comuna 18': 127200,
                        'Comuna 19': 112500,
                        'Comuna 20': 68800,
                        'Comuna 21': 120300,
                        'Comuna 22': 13100
                    }
                    comunas = list(datos_muestra.keys())
                    poblaciones = list(datos_muestra.values())
        except Indicador.DoesNotExist:
            print("ERROR: Indicador SIS_4_T3_I6 no encontrado")
            # Usar datos de muestra si el indicador no existe
            anio_datos = 2024
            datos_muestra = {
                'Comuna 1': 89500,
                'Comuna 2': 106200,
                'Comuna 3': 44900,
                'Comuna 4': 53600,
                'Comuna 5': 112500,
                'Comuna 6': 188100,
                'Comuna 7': 72500,
                'Comuna 8': 103400,
                'Comuna 9': 45200,
                'Comuna 10': 112300,
                'Comuna 11': 108600,
                'Comuna 12': 66100,
                'Comuna 13': 178300,
                'Comuna 14': 169600,
                'Comuna 15': 162100,
                'Comuna 16': 107500,
                'Comuna 17': 144000,
                'Comuna 18': 127200,
                'Comuna 19': 112500,
                'Comuna 20': 68800,
                'Comuna 21': 120300,
                'Comuna 22': 13100
            }
            comunas = list(datos_muestra.keys())
            poblaciones = list(datos_muestra.values())

        # Calcular el total de la población por comunas
        total_poblacion_comunas = sum(poblaciones)

        # Calcular los porcentajes
        porcentajes_comunas = [100 * valor / total_poblacion_comunas for valor in poblaciones]

        # Crear el gráfico de barras para las comunas (en porcentajes)
        fig_comunas = go.Figure()

        fig_comunas.add_trace(go.Bar(
            x=comunas,
            y=porcentajes_comunas,
            marker_color='#4299e1',
            text=[f'{p:.1f}%' for p in porcentajes_comunas],
            textposition='auto',
            hovertemplate='Comuna: %{x}<br>Porcentaje: %{y:.1f}%<extra></extra>'
        ))

        # Mejorar el diseño del gráfico
        fig_comunas.update_layout(
            margin=dict(l=40, r=40, t=80, b=160),  # Margen inferior aumentado para el pie de página
            title=f'Distribución de Población por Comunas ({anio_datos})',
            xaxis_title='Comuna',
            yaxis_title='Porcentaje de la Población (%)',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(
                family='Inter',
                size=14,
                color='rgb(33, 37, 41)'
            ),
            xaxis=dict(
                tickangle=45,
                tickfont=dict(size=12)
            ),
            yaxis=dict(
                tickformat='.1f',
                tickfont=dict(size=12)
            ),
            autosize=True,  # Permitir que se ajuste automáticamente a su contenedor
            annotations=[
                crear_pie_pagina(
                    "Distribución poblacional por comunas",
                    "Porcentaje del total de población que reside en cada comuna de la ciudad.",
                    series_comunas.first().entidad_recopilatoria if series_comunas else 'Sin especificar',
                    series_comunas.first().fuente_datos if series_comunas and series_comunas.first().fuente_datos else 'indicadores.cali.gov.co'
                )
            ]
        )

        # Convertir el gráfico a JSON
        chart_json_comunas = json.dumps(fig_comunas, cls=PlotlyJSONEncoder)

        # ------------------- Nuevo gráfico: Población Histórica por Ciudades -------------------
        try:
            # Obtener el indicador para población total por ciudades
            indicador_ciudades = Indicador.objects.get(nombre='SIS_4_T3_I1')

            # Lista de ciudades a incluir
            ciudades = ['Cali', 'Barranquilla', 'Medellín', 'Bogotá']

            # Colores para cada ciudad
            colores_ciudades = {
                'Cali': '#4299e1',  # Azul
                'Barranquilla': '#ed8936',  # Naranja
                'Medellín': '#48bb78',  # Verde
                'Bogotá': '#9f7aea'   # Púrpura
            }

            # Años para el análisis (usar un rango más amplio para ver tendencias históricas)
            anios_analisis = list(range(2000, 2026))

            # Crear figura para el gráfico de líneas
            fig_ciudades = go.Figure()

            # Para cada ciudad, obtener los datos históricos y añadir una línea
            for ciudad in ciudades:
                # Obtener la serie de datos para esta ciudad
                try:
                    serie_ciudad = SerieDatos.objects.get(
                        indicador=indicador_ciudades,
                        desagregacion_geografica=ciudad,
                        desagregacion_tematica='Total'
                    )

                    # Datos de población por año
                    datos_anios = []
                    poblacion_anios = []

                    # Obtener datos para cada año
                    for anio in anios_analisis:
                        try:
                            dato = Dato.objects.filter(
                                serie_datos=serie_ciudad,
                                fecha_dato__year=anio
                            ).order_by('-fecha_dato').first()

                            if dato:
                                datos_anios.append(anio)
                                poblacion_anios.append(float(dato.valor_dato))
                        except Exception as e:
                            print(f"Error al obtener datos para {ciudad} en {anio}: {str(e)}")

                    # Añadir línea para esta ciudad si hay datos
                    if datos_anios and poblacion_anios:
                        fig_ciudades.add_trace(go.Scatter(
                            x=datos_anios,
                            y=poblacion_anios,
                            mode='lines+markers',
                            name=ciudad,
                            line=dict(color=colores_ciudades.get(ciudad, '#666666'), width=3),
                            marker=dict(size=8),
                            hovertemplate=f'{ciudad}<br>Año: %{{x}}<br>Población: %{{y:,.0f}}<extra></extra>'
                        ))
                except SerieDatos.DoesNotExist:
                    print(f"No se encontraron series de datos para {ciudad}")

            # Mejorar el diseño del gráfico
            fig_ciudades.update_layout(
                margin=dict(l=40, r=40, t=80, b=160),  # Aumentar el margen inferior para el pie de página
                title='Población Histórica por Ciudades',
                xaxis_title='Año',
                yaxis_title='Población',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(
                    family='Inter',
                    size=14,
                    color='rgb(33, 37, 41)'
                ),
                autosize=True,  # Permitir que se ajuste automáticamente a su contenedor
                xaxis=dict(
                    tickmode='array',
                    tickvals=list(range(2000, 2026, 5)),  # Mostrar cada 5 años para mejor legibilidad
                    tickangle=45
                ),
                yaxis=dict(
                    tickformat=',.0f'  # Formato con separadores de miles
                ),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                annotations=[
                    crear_pie_pagina(
                        "Evolución poblacional de las principales ciudades",
                        "Comparativa del crecimiento poblacional de Cali con otras ciudades importantes del país.",
                        'DANE',
                        'Proyecciones de población - indicadores.cali.gov.co'
                    )
                ]
            )

            # Convertir el gráfico a JSON
            chart_json_ciudades = json.dumps(fig_ciudades, cls=PlotlyJSONEncoder)
        except Indicador.DoesNotExist:
            print("ERROR: Indicador SIS_4_T3_I1 no encontrado")
            chart_json_ciudades = '{}'
        except Exception as e:
            print(f"Error al crear gráfico de ciudades: {str(e)}")
            chart_json_ciudades = '{}'

        # Crear gráficos de barras para los nuevos indicadores
        grafico_edad_mediana = crear_grafico_barras(
            'SIS_4_T3_I13',
            'Edad Mediana de la Población',
            'Edad',
            'años'
        )

        if not grafico_edad_mediana:
            grafico_edad_mediana = {
                'layout': {
                    'annotations': [
                        {
                            'text': 'No hay datos disponibles para la edad mediana de la población.<br>Este indicador mostrará información cuando esté disponible.',
                            'xref': 'paper',
                            'yref': 'paper',
                            'x': 0.5,
                            'y': 0.5,
                            'showarrow': False,
                            'font': {'size': 14},
                            'align': 'center'
                        }
                    ]
                }
            }

        grafico_relacion_hm = crear_grafico_barras(
            'SIS_4_T3_I7',
            'Relación Hombre-Mujer',
            'Ratio',
            'ratio'
        )

        # Crear gráficos de líneas para los indicadores
        grafico_indice_envejecimiento = crear_grafico_lineas(
            'SIS_4_T3_I9',
            'Índice de Envejecimiento',
            'Personas',
            'por cada 100 personas'
        )

        grafico_dependencia_total = crear_grafico_lineas(
            'SIS_4_T3_I11',
            'Dependencia Total',
            'Porcentaje',
            '%'
        )

        # Convertir todos los gráficos a JSON antes de pasarlos al contexto
        context = {
            'chart_json_barras': json.dumps(fig_barras, cls=PlotlyJSONEncoder),
            'chart_json_piramide': chart_json_piramide,
            'chart_json_poblacion_sexo': chart_json_poblacion_sexo,
            'chart_json_edades': chart_json_edades,
            'chart_json_tasa': chart_json_tasa,
            'chart_json_comunas': chart_json_comunas,
            'chart_json_ciudades': chart_json_ciudades,
            'chart_json_edad_mediana': json.dumps(grafico_edad_mediana, cls=PlotlyJSONEncoder) if grafico_edad_mediana else '{}',
            'chart_json_relacion_hm': json.dumps(grafico_relacion_hm, cls=PlotlyJSONEncoder) if grafico_relacion_hm else '{}',
            'chart_json_indice_envejecimiento': json.dumps(grafico_indice_envejecimiento, cls=PlotlyJSONEncoder) if grafico_indice_envejecimiento else '{}',
            'chart_json_dependencia_total': json.dumps(grafico_dependencia_total, cls=PlotlyJSONEncoder) if grafico_dependencia_total else '{}'
        }

        return render(request, 'poblacion.html', context)

    except Exception as e:
        print(f"Error en la vista poblacion: {str(e)}")
        return render(request, 'poblacion.html', {'error_message': str(e)})

def sistemas(request):
    return render(request, 'sistemas.html')

def temas(request):
    return render(request, 'temas.html')


def conjuntos(request):
    return render(request, 'conjuntos.html')

def conjuntos_json(request):
    conjuntos = ConjuntoIndicadores.objects.all().values('id', 'nombre', 'descripcion')
    return JsonResponse(list(conjuntos), safe=False)

def dimensiones_json(request, conjunto_id):
    dimensiones = Dimension.objects.filter(conjunto__id=conjunto_id).values('id', 'nombre', 'descripcion')
    return JsonResponse(list(dimensiones), safe=False)

def tematicas_json(request, dimension_id):
    tematicas = Tematica.objects.filter(dimension__id=dimension_id).values('id', 'nombre', 'descripcion')
    return JsonResponse(list(tematicas), safe=False)

def indicadores_json(request, tematica_id):
    indicadores = Indicador.objects.filter(tematica__id=tematica_id).values('id', 'nombre', 'descripcion')
    return JsonResponse(list(indicadores), safe=False)


def datos_json(request, indicador_id):
    indicador = get_object_or_404(Indicador, pk=indicador_id)
    series_datos = SerieDatos.objects.filter(indicador=indicador)
    datos = Dato.objects.filter(serie_datos__in=series_datos)

    df = pd.DataFrame(list(datos.values(
        'fecha_dato',
        'valor_dato',
        'serie_datos__desagregacion_geografica',
        'serie_datos__desagregacion_tematica'
    )))
    try:
        df['fecha_dato'] = pd.to_datetime(df['fecha_dato'])
        df = df.sort_values(by='fecha_dato')

        fecha_min = df['fecha_dato'].min()
        fecha_max = df['fecha_dato'].max()

        fecha_inicio_str = request.GET.get('fecha_inicio', fecha_min.strftime('%Y-%m-%d'))
        fecha_fin_str = request.GET.get('fecha_fin', fecha_max.strftime('%Y-%m-%d'))

        fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
        fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()

        df = df[(df['fecha_dato'].dt.date >= fecha_inicio) & (df['fecha_dato'].dt.date <= fecha_fin)]
        if df.empty:
            return JsonResponse({'mensaje': 'No se encontraron datos para los criterios seleccionados.'})

        # Genera el gráfico utilizando Plotly Express
        fig = px.line(
            df,
            x='fecha_dato',
            y='valor_dato',
            color='serie_datos__desagregacion_geografica',
            line_group='serie_datos__desagregacion_tematica',
            title=indicador.nombre
        )
        fig_dict = fig.to_dict()

        return JsonResponse({
            'fig': fig_dict,
            'indicador': {'nombre': indicador.nombre, 'descripcion': indicador.descripcion},
            'fecha_min': fecha_min,
            'fecha_max': fecha_max,
            'fecha_inicio': fecha_inicio_str,
            'fecha_fin': fecha_fin_str
        }, encoder=PlotlyJSONEncoder)
    except Exception as e:
        print(f"Error en la vista datos: {e}")
        return JsonResponse({'error_message': str(e)})
