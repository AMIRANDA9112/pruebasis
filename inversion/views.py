from django.shortcuts import render
from .models import Proyecto
from django.shortcuts import render, get_object_or_404
from .models import Proyecto, Ciudadano, Predio, Barrio
import plotly.graph_objects as go
from plotly.offline import plot
from django.db.models import Avg, Max, Min
from django.contrib.gis.geos import GEOSGeometry
import json  # Importa la librería json

def lista_proyectos(request):
    proyectos = Proyecto.objects.all()
    context = {'proyectos': proyectos}
    return render(request, 'inversion/lista_proyectos.html', context)

def detalle_proyecto(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)

    # Ciudadanos y cálculos básicos
    ciudadanos_beneficiados = proyecto.ciudadanos.select_related('predio__barrio').all()
    num_ciudadanos_beneficiados = ciudadanos_beneficiados.count()
    valor_total_inversion = proyecto.valor
    valor_por_beneficiario = valor_total_inversion / num_ciudadanos_beneficiados if num_ciudadanos_beneficiados > 0 else 0

    # Predios y Barrios relacionados
    predios_beneficiados = Predio.objects.filter(ciudadanos__proyecto=proyecto).distinct()
    num_predios_afectados = predios_beneficiados.count()
    barrios_beneficiados = Barrio.objects.filter(predios__ciudadanos__proyecto=proyecto).distinct()

    # GeoJSON para mapas
    predios_geojson_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": json.loads(predio.geom.json) if predio.geom else None,
                "properties": {
                    "numero_unico": predio.numero_unico,
                    "direccion": predio.direccion,
                }
            }
            for predio in predios_beneficiados if predio.geom
        ]
    }

    barrios_geojson_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": json.loads(barrio.geom.json) if barrio.geom else None,
                "properties": {
                    "nombre": barrio.nombre,
                    "comuna": barrio.comuna,
                    "numero": barrio.numero
                }
            }
            for barrio in barrios_beneficiados if barrio.geom
        ]
    }

    # ------------------------------------------
    # SECCIÓN DE GRÁFICOS (FALTANTE EN LA RESPUESTA ANTERIOR)
    # ------------------------------------------

    # Gráfico de edades
    edades_beneficiados = [c.edad for c in ciudadanos_beneficiados]
    edad_rangos = {'Menores de 18': 0, 'Entre 18 y 35': 0, 'Mayores de 35': 0}
    for edad in edades_beneficiados:
        if edad < 18:
            edad_rangos['Menores de 18'] += 1
        elif 18 <= edad <= 35:
            edad_rangos['Entre 18 y 35'] += 1
        else:
            edad_rangos['Mayores de 35'] += 1

    fig_edad = go.Figure(data=[go.Pie(
        labels=list(edad_rangos.keys()),
        values=list(edad_rangos.values()),
        hole=0.4
    )])
    fig_edad.update_layout(title_text='Distribución por Edades')
    plot_div_edad = plot(fig_edad, output_type='div')

    # Gráficos de ingresos beneficiados
    if ciudadanos_beneficiados.exists():
        ingresos_beneficiados = ciudadanos_beneficiados.aggregate(
            promedio=Avg('ingresos_anuales'),
            maximo=Max('ingresos_anuales'),
            minimo=Min('ingresos_anuales')
        )
        fig_ingresos_benef = go.Figure(data=[
            go.Bar(
                x=['Promedio', 'Máximo', 'Mínimo'],
                y=[ingresos_beneficiados['promedio'],
                   ingresos_beneficiados['maximo'],
                   ingresos_beneficiados['minimo']],
                marker_color=['#2ecc71', '#e74c3c', '#f1c40f']
            )
        ])
        fig_ingresos_benef.update_layout(title='Ingresos de Beneficiados')
        plot_div_ingresos_beneficiados = plot(fig_ingresos_benef, output_type='div')
    else:
        plot_div_ingresos_beneficiados = "<p>No hay datos de ingresos para beneficiados</p>"

    # Gráficos de ingresos NO beneficiados
    ciudadanos_no_beneficiados = Ciudadano.objects.filter(proyecto__isnull=True)
    if ciudadanos_no_beneficiados.exists():
        ingresos_no_benef = ciudadanos_no_beneficiados.aggregate(
            promedio=Avg('ingresos_anuales'),
            maximo=Max('ingresos_anuales'),
            minimo=Min('ingresos_anuales')
        )
        fig_ingresos_no_benef = go.Figure(data=[
            go.Bar(
                x=['Promedio', 'Máximo', 'Mínimo'],
                y=[ingresos_no_benef['promedio'],
                   ingresos_no_benef['maximo'],
                   ingresos_no_benef['minimo']],
                marker_color=['#95a5a6', '#7f8c8d', '#bdc3c7']
            )
        ])
        fig_ingresos_no_benef.update_layout(title='Ingresos de No Beneficiados')
        plot_div_ingresos_no_beneficiados = plot(fig_ingresos_no_benef, output_type='div')
    else:
        plot_div_ingresos_no_beneficiados = "<p>No hay datos de ingresos para no beneficiados</p>"

    # ------------------------------------------
    # FIN SECCIÓN DE GRÁFICOS
    # ------------------------------------------

    context = {
        'proyecto': proyecto,
        'num_predios_afectados': num_predios_afectados,
        'valor_total_inversion': valor_total_inversion,
        'valor_por_beneficiario': valor_por_beneficiario,
        'plot_div_edad': plot_div_edad,
        'plot_div_ingresos_beneficiados': plot_div_ingresos_beneficiados,
        'plot_div_ingresos_no_beneficiados': plot_div_ingresos_no_beneficiados,
        'num_ciudadanos_beneficiados': num_ciudadanos_beneficiados,
        'predios_geojson': json.dumps(predios_geojson_data),
        'barrios_geojson': json.dumps(barrios_geojson_data),
    }
    return render(request, 'inversion/detalle_proyecto.html', context)

