# Sistema de Seguimiento de Entrenamiento y Nutrición

## Descripción
Aplicación web para el seguimiento integral de entrenamiento físico, nutrición y métricas corporales, desarrollada con Python, Streamlit y PostgreSQL.

## Requisitos del Sistema
- Python 3.8+
- PostgreSQL 12+
- pip (gestor de paquetes de Python)

## Configuración del Entorno

1. Clonar el repositorio:
```bash
git clone <url-del-repositorio>
cd <nombre-del-directorio>Si
```

2. Crear un entorno virtual:
```bash
python -m venv venv
```

3. Activar el entorno virtual:
- Windows:
```bash
.\venv\Scripts\activate
```
- Linux/Mac:
```bash
source venv/bin/activate
```

4. Instalar dependencias:
```bash
pip install -r requirements.txt
```

5. Configurar variables de entorno:
- Crear archivo `.env` en la raíz del proyecto
- Copiar el contenido de `.env.example` y configurar las variables

6. Inicializar la base de datos:
```bash
alembic upgrade head
```

7. Ejecutar la aplicación:
```bash
cd src
streamlit run app.py
```

## Estructura del Proyecto
```
├── alembic/              # Migraciones de base de datos
├── src/                  # Código fuente
│   ├── app.py            # Punto de entrada de la aplicación
│   ├── login.py          # Página de inicio de sesión
│   ├── register.py       # Página de registro de usuario
│   ├── dashboard.py      # Dashboard resumen
│   ├── training.py       # Módulo de entrenamiento
│   ├── metrics.py        # Módulo de métricas corporales
│   ├── nutrition.py      # Módulo de nutrición
│   ├── database/         # Configuración de base de datos
│   ├── models/           # Modelos SQLAlchemy
│   │   └── base_model.py # Clase base para modelos
│   ├── views/            # Vistas de la aplicación (Streamlit u otros)
│   ├── controllers/      # Lógica de controladores (gestión de flujo y lógica de negocio)
│   ├── utils/            # Funciones utilitarias y helpers
│   ├── static/           # Archivos estáticos (imágenes, CSS, JS)
│   └── tests/            # Tests unitarios y de integración
├── .env.example          # Ejemplo de variables de entorno
├── requirements.txt      # Dependencias del proyecto
└── README.md             # Este archivo
```

### Descripción de carpetas nuevas:
- **views/**: Contendrá las vistas de la aplicación, como páginas o componentes visuales.
- **controllers/**: Lógica de controladores, separación de la lógica de negocio y flujo de la app.
- **utils/**: Funciones utilitarias, helpers y código reutilizable.
- **static/**: Archivos estáticos como imágenes, hojas de estilo o scripts JS.
- **tests/**: Pruebas unitarias y de integración.
- **models/base_model.py**: Clase base para los modelos SQLAlchemy, útil para herencia y consistencia.

## Características Implementadas
- [x] Configuración del entorno de desarrollo
- [x] Autenticación de usuarios (login y registro)
- [x] Dashboard resumen con KPIs
- [x] Módulo de entrenamiento (registro, historial, ejercicios)
- [x] Registro y visualización de métricas corporales (peso, altura, IMC)
- [x] Módulo de nutrición (alimentos, registro de comidas, calorías)

## Flujo de Ejecución
1. El usuario debe iniciar sesión o registrarse para acceder a la aplicación.
2. Una vez autenticado, puede navegar entre las siguientes secciones:
   - Dashboard: KPIs y gráficos de resumen
   - Entrenamiento: registro de entrenamientos y ejercicios
   - Nutrición: registro de comidas y alimentos, historial de calorías
   - Métricas Corporales: registro y evolución de peso, altura e IMC
   - Configuración: (en desarrollo)

## Contribución
1. Crear un branch (`git checkout -b feature/nombre-caracteristica`)
2. Commit de cambios (`git commit -am 'Agregar nueva característica'`)
3. Push al branch (`git push origin feature/nombre-caracteristica`)
4. Crear Pull Request

## Licencia
Este proyecto está bajo la licencia MIT. 

## Diagramas de Flujo y Casos de Uso

### Diagrama de Flujo General

```mermaid
flowchart TD
    A[Inicio] --> B{¿Usuario autenticado?}
    B -- No --> C[Mostrar Login/Registro]
    C -->|Login exitoso| D[Dashboard]
    B -- Sí --> D[Dashboard]
    D --> E{Navegación}
    E --> F[Entrenamiento]
    E --> G[Nutrición]
    E --> H[Métricas Corporales]
    E --> I[Configuración]
    F --> D
    G --> D
    H --> D
    I --> D
    D --> J[Cerrar Sesión]
    J --> C
```

### Diagrama de Casos de Uso

```mermaid
flowchart TD
    subgraph Casos de Uso
        U1[Registrar usuario] --> U2[Iniciar sesión]
        U2 --> U3[Ver Dashboard]
        U3 --> U4[Registrar entrenamiento]
        U3 --> U5[Registrar comida]
        U3 --> U6[Registrar métrica corporal]
        U3 --> U7[Ver historial de entrenamientos]
        U3 --> U8[Ver historial de comidas]
        U3 --> U9[Ver evolución de peso]
        U3 --> U10[Editar/eliminar registros]
        U3 --> U11[Cerrar sesión]
    end
```

### Casos de Uso Posibles

1. **Registrar usuario:**  Un nuevo usuario crea una cuenta con email, usuario y contraseña.
2. **Iniciar sesión:**  El usuario accede a la app con sus credenciales.
3. **Ver Dashboard:**  El usuario visualiza un resumen de su progreso y KPIs principales.
4. **Registrar entrenamiento:**  El usuario añade un nuevo entrenamiento con ejercicios, series, repeticiones y peso.
5. **Registrar comida:**  El usuario registra alimentos consumidos y la cantidad, calculando calorías.
6. **Registrar métrica corporal:**  El usuario registra su peso y altura, calculando el IMC.
7. **Ver historial de entrenamientos:**  El usuario consulta entrenamientos pasados y detalles.
8. **Ver historial de comidas:**  El usuario consulta comidas registradas y calorías consumidas.
9. **Ver evolución de peso:**  El usuario visualiza la evolución de su peso en el tiempo mediante gráficos.
10. **Editar/eliminar registros:**  El usuario puede modificar o eliminar entrenamientos, comidas o métricas.
11. **Cerrar sesión:**  El usuario sale de la aplicación y debe volver a autenticarse para acceder. 

## Solución de Problemas

### Error: FileNotFoundError: No such file or directory: 'alembic\\script.py.mako'

Si al ejecutar una migración con Alembic ves este error:

```
FileNotFoundError: [Errno 2] No such file or directory: 'alembic\\script.py.mako'
```

Esto significa que falta el archivo de plantilla de migración en la carpeta alembic/. Para restaurarlo:

1. Crea una carpeta temporal y genera la estructura de Alembic en ella:
   ```bash
   mkdir alembic_tmp
   alembic init alembic_tmp
   ```
2. Copia el archivo de plantilla a tu carpeta alembic original:
   ```bash
   copy alembic_tmp\script.py.mako alembic\
   ```
3. Elimina la carpeta temporal:
   ```bash
   rmdir /s /q alembic_tmp
   ```
4. Vuelve a intentar la migración:
   ```bash
   alembic revision --autogenerate -m "Initial users table"
   ```

Con esto, Alembic debería funcionar correctamente. 

## Buenas Prácticas de Seguridad y Producción

- Todas las contraseñas se almacenan con hash seguro (bcrypt).
- Las sesiones expiran automáticamente tras 5 minutos de inactividad.
- Todas las entradas de usuario son validadas en formularios.
- Se recomienda ejecutar la app detrás de HTTPS en producción.
- Configura variables de entorno seguras y nunca subas tu archivo .env real al repositorio.
- Realiza backups periódicos de la base de datos PostgreSQL.
- Usa herramientas de monitoreo y logging (ejemplo: Sentry, Prometheus, Grafana).
- Cumple con normativas de privacidad (GDPR/LGPD): permite a los usuarios exportar/eliminar sus datos si es necesario.
- Para pruebas de carga y seguridad, utiliza herramientas como Locust, OWASP ZAP, etc.
- Consulta la documentación de cada módulo en este README y en los comentarios del código. 

## Despliegue en Streamlit Cloud y Supabase

- Sube tu código a GitHub.
- Crea un archivo `.streamlit/secrets.toml` con las credenciales de tu base de datos Supabase.
- Entra a https://streamlit.io/cloud, conecta tu repo y selecciona `src/app.py` como entrypoint.
- ¡Listo! Tu app usará Supabase como base de datos y será accesible desde cualquier lugar. 