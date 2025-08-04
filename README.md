# Sistema de Información Estadística Territorial (SIS)

Sistema de gestión, visualización y documentación de indicadores estadísticos para el Departamento de Planeación Distrital de Santiago de Cali.

## Descripción

El Sistema de Información Estadística Territorial (SIS) es una plataforma web desarrollada en Django que permite gestionar, visualizar y documentar indicadores estadísticos con enfoque territorial. El sistema integra datos geográficos, series temporales y documentación estadística siguiendo estándares internacionales.

## Características Principales

- **Gestión de Indicadores**: Estructura jerárquica para organización de indicadores estadísticos
- **Visualización Geoespacial**: Integración con PostGIS para mapas interactivos
- **Documentación Estadística**: Módulo completo según estándares DDI (Data Documentation Initiative)
- **Gráficos Interactivos**: Visualización de datos mediante Plotly.js
- **Navegación por Temas**: Sistema de menús dinámico para exploración de indicadores
- **Microdatos**: Gestión de archivos CSV con datos detallados

## Arquitectura del Sistema

### Tecnologías

- **Backend**: Python 3.8+, Django 4.2+
- **Base de Datos**: PostgreSQL 13+ con PostGIS
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Visualización**: Plotly.js, Folium
- **Documentación**: PlantUML, Sphinx

### Estructura de Proyecto

```
indicadores/
├── indicadores/           # Aplicación principal
│   ├── models.py          # Modelos de datos
│   ├── views.py           # Vistas y lógica
│   ├── urls.py            # Enrutamiento
│   ├── admin.py           # Panel administrativo
│   ├── forms.py           # Formularios
│   ├── services.py        # Servicios y utilidades
│   ├── templates/         # Plantillas HTML
│   ├── static/            # Archivos estáticos
│   ├── migrations/        # Migraciones de base de datos
│   └── docs/              # Documentación técnica
├── manage.py
├── requirements.txt
└── README.md
```

## Modelos de Datos

El sistema utiliza una estructura de datos compleja para gestionar indicadores estadísticos:

### Estructura Jerárquica Principal

1. **MenuDominio** → **MenuTema** → **MenuSubtema** → **Indicador** → **Dato**

### Sistema Geográfico

- **NivelGeografico**: Niveles de desagregación geográfica
- **CapaGeo**: Capas geográficas
- **ElementoGeo**: Elementos geográficos específicos

### Documentación Estadística

- **OperacionEstadistica**: Censos, encuestas y registros administrativos
- **MetadataOperacion**: Metadatos detallados de operaciones
- **MaterialReferencia**: Documentos de referencia (PDF, XLS, etc.)

### Visualización

- **Grafico**: Configuración de gráficos
- **GraficoSerie**: Series de datos para visualización

## Instalación

### Requisitos Previos

- Python 3.8 o superior
- PostgreSQL 13+ con PostGIS
- Virtualenv (recomendado)

### Pasos de Instalación

1. **Clonar el repositorio**
   ```bash
   git clone <url-repositorio>
   cd sis
   ```

2. **Crear entorno virtual**
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar base de datos**
   ```bash
   # Crear base de datos en PostgreSQL
   createdb sis_db
   
   # Ejecutar migraciones
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Crear superusuario**
   ```bash
   python manage.py createsuperuser
   ```

6. **Iniciar servidor de desarrollo**
   ```bash
   python manage.py runserver
   ```

## Uso

### Acceso al Sistema

- **Sitio público**: `http://localhost:8000/`
- **Panel administrativo**: `http://localhost:8000/admin/`

### Funcionalidades Principales

1. **Gestión de Indicadores**
   - Crear y editar indicadores estadísticos
   - Asociar indicadores a temas y subtemas
   - Cargar datos históricos

2. **Visualización de Datos**
   - Generar gráficos interactivos
   - Visualizar mapas temáticos
   - Exportar datos en múltiples formatos

3. **Documentación Estadística**
   - Registrar operaciones estadísticas
   - Documentar metodologías
   - Gestionar materiales de referencia

4. **Microdatos**
   - Cargar archivos CSV
   - Procesar y validar datos
   - Generar indicadores agregados

## API

El sistema expone una API REST para acceso a datos:

### Endpoints Principales

- `GET /api/indicadores/` - Listado de indicadores
- `GET /api/indicadores/{id}/` - Detalle de indicador
- `GET /api/indicadores/{id}/datos/` - Datos de un indicador
- `GET /api/graficos/{id}/` - Configuración de gráfico

### Ejemplo de Uso

```javascript
// Obtener datos de un indicador
fetch('/api/indicadores/1/datos/')
  .then(response => response.json())
  .then(data => console.log(data));
```

## Desarrollo

### Estructura de Branches

- `main`: Código en producción
- `develop`: Desarrollo activo
- `feature/*`: Nuevas funcionalidades
- `hotfix/*`: Correcciones urgentes

### Convenciones de Código

- Seguir PEP 8 para Python
- Utilizar docstrings en todas las funciones
- Escribir tests para nuevas funcionalidades
- Mantener migraciones limpias y atómicas

### Ejecutar Tests

```bash
python manage.py test
```

## Documentación

- [Diagrama de Base de Datos](docs/database_model.puml)
- [Guía de Usuario](docs/user_guide.md)
- [Guía Técnica](docs/technical_guide.md)
- [API Documentation](docs/api.md)

## Contribución

1. Crear un fork del repositorio
2. Crear una rama para la nueva funcionalidad (`git checkout -b feature/nueva-funcionalidad`)
3. Realizar los cambios necesarios
4. Ejecutar tests y verificar que pasen
5. Hacer commit de los cambios (`git commit -am 'Añadir nueva funcionalidad'`)
6. Hacer push a la rama (`git push origin feature/nueva-funcionalidad`)
7. Crear un nuevo Pull Request

## Mantenimiento

### Actualización de Datos

El sistema incluye scripts para actualización automatizada de datos:

```bash
# Actualizar indicadores desde fuentes externas
python manage.py update_indicadores

# Procesar microdatos CSV
python manage.py process_microdata
```

### Respaldo de Base de Datos

```bash
# Crear respaldo
pg_dump -h localhost -U usuario sis_db > backup_$(date +%Y%m%d).sql

# Restaurar respaldo
psql -h localhost -U usuario sis_db < backup.sql
```

## Seguridad

- Las credenciales deben mantenerse en variables de entorno
- Se recomienda HTTPS en producción
- Actualizar dependencias regularmente
- Realizar auditorías de seguridad periódicas

## Problemas Conocidos

- Vista `tema_detalle` incompleta (pendiente de implementación)
- Optimización de consultas complejas para grandes volúmenes de datos
- Documentación técnica incompleta

## Roadmap

### Versión 1.1 (Próximo release)

- Completar implementación de vista `tema_detalle`
- Implementar sistema de caching para mejorar performance
- Ampliar tipos de gráficos disponibles

### Versión 1.2

- Dashboard personalizable para usuarios
- Sistema de notificaciones para actualización de datos
- Mejoras en la exportación de datos

### Versión 2.0

- Migración a arquitectura de microservicios
- Implementación de machine learning para predicciones
- API GraphQL

## Licencia

Este proyecto es propiedad del Departamento de Planeación Distrital de Santiago de Cali y no puede ser distribuido sin autorización previa.

## Contacto

Para soporte técnico o consultas sobre el sistema:

- **Departamento de Planeación Distrital**
- **Email**: planeacion@cali.gov.co
- **Teléfono**: +57 (2) XXX XXXX

## Agradecimientos

- Alcaldía de Santiago de Cali
- Departamento Administrativo de Estadística (DANE)
- Gobernación del Valle del Cauca
