# Sprint Summary Report Skill

Professional Sprint Performance Report Generator

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/Chart.js-4.4.1-green?style=flat-square" alt="Chart.js">
  <img src="https://img.shields.io/badge/license-MIT-orange?style=flat-square" alt="License">
</p>

---

## 📑 Tabla de Contenidos

- [Vista Rápida](#-vista-rápida)
- [Requisitos](#-requisitos)
- [Instalación](#-instalación)
- [Uso](#-uso)
  - [Para Usuarios No Técnicos](#para-usuarios-no-técnicos)
  - [Para Desarrolladores](#para-desarrolladores)
- [Características](#-características)
- [Interpretación del Reporte](#-interpretación-del-reporte)
  - [Glosario de Términos](#glosario-de-términos)
  - [Guía Visual](#guía-visual)
- [Rendimiento y Límites](#-rendimiento-y-límites)
- [Solución de Problemas](#-solución-de-problemas)
- [Contribuir](#-contribuir)
- [Changelog](#-changelog)

---

## 👀 Vista Rápida

Genera reportes profesionales de sprint en segundos:

```bash
python3 scripts/generate_report.py ./UserStories.csv \
  --sprint-start 2026-04-07 \
  --sprint-end 2026-04-17 \
  --output my-sprint-report.html
```

**Resultado:** Un archivo HTML autocontenido, listo para compartir o imprimir a PDF.

---

## 🔒 Privacidad y Protección de Datos

> **⚠️ IMPORTANTE - Directiva de Privacidad**
>
> **Esta skill procesa datos localmente. Los datos de JIRA exportados NO se utilizan para entrenar modelos de lenguaje (LLM) ni se envían a servicios externos.**

### Recomendaciones de Anonimización

Antes de exportar tu CSV de Jira, asegúrate de:

- ✅ **Anonimizar nombres** - No incluir nombres completos de personas en el campo Assignee (usar iniciales o IDs)
- ✅ **Eliminar marcas comerciales** - Remover nombres de productos propietarios de los títulos de tickets
- ✅ **Excluir información confidencial** - No exportar tickets con datos sensibles, contratos, o información de clientes
- ✅ **Revisar descripciones** - Asegurar que los campos Summary no contengan datos sensibles
- ✅ **Usar proyectos de prueba** - Para pruebas de esta skill, usar datos de proyectos ficticios o de demostración

### Qué datos permanecen locales

| Dato | Procesamiento | Almacenamiento |
|------|---------------|----------------|
| CSV exportado | Local | Temporal (solo durante generación) |
| Reporte HTML | Local | Archivo de salida elegido por usuario |
| Métricas calculadas | Local | No persistente |

**Ningún dato se transmite a servicios externos, APIs de terceros, ni se utiliza para entrenamiento de modelos AI.**

---

## 📋 Requisitos

| Componente | Versión | Notas |
|------------|---------|-------|
| Python | 3.8+ | Requerido |
| pandas | 1.3+ | `pip install pandas` |
| Navegador | Cualquiera | Para ver el reporte |

---

## 🚀 Instalación

### 1. Clonar o descargar el repositorio

```bash
git clone <url-del-repo>
cd sprint-summary
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

**Contenido de `requirements.txt`:**
```
pandas>=1.3.0
```

### 3. Verificar instalación

```bash
python3 scripts/generate_report.py --help
```

---

## 💻 Uso

### Para Usuarios No Técnicos

#### Paso 1: Exportar datos de Jira

1. Ve a **Issues** en tu proyecto de Jira
2. Filtra los tickets del sprint actual
3. Haz clic en **Export** → **CSV (All fields)**
4. Guarda el archivo (ej: `UserStories.csv`)

#### Paso 2: Ejecutar el script

**En Windows:**
```bash
python scripts/generate_report.py UserStories.csv --sprint-start 2026-04-07 --sprint-end 2026-04-17
```

**En Mac/Linux:**
```bash
python3 scripts/generate_report.py UserStories.csv --sprint-start 2026-04-07 --sprint-end 2026-04-17
```

#### Paso 3: Abrir el reporte

El archivo `sprint-report.html` se creará en la misma carpeta. Ábrelo con tu navegador.

<details>
<summary><b>📖 Ver ejemplo paso a paso con imágenes</b></summary>

1. **Exportar de Jira:**
   - Navega a tu proyecto → Issues
   - Selecciona el sprint en el filtro
   - Export → CSV

2. **Ejecutar comando:**
   - Abre terminal/cmd en la carpeta del proyecto
   - Escribe el comando con las fechas de tu sprint
   - Presiona Enter

3. **Ver reporte:**
   - Busca `sprint-report.html`
   - Doble clic para abrir en navegador
   - Ctrl+P para guardar como PDF

</details>

---

### Para Desarrolladores

#### Parámetros disponibles (entrypoint: scripts/generate_report.py)

| Parámetro | Requerido | Formato | Default | Descripción |
|-----------|-----------|---------|---------|-------------|
| `csv_path` | ✅ | Path | - | Ruta al archivo CSV exportado de Jira |
| `--sprint-start` | ✅ | YYYY-MM-DD | - | Fecha de inicio del sprint |
| `--sprint-end` | ✅ | YYYY-MM-DD | - | Fecha de fin del sprint |
| `--output` | ❌ | Filename | `sprint-report.html` | Nombre del archivo de salida |
| `--config`, `-c` | ❌ | Path | `scripts/generate_report_input.json` | Ruta a JSON de configuración con los parámetros de entrada |

#### Configuración con JSON

El script puede cargar valores desde el archivo JSON `scripts/generate_report_input.json` cuando no se proporcionan todos los parámetros por línea de comandos.

Ejemplo de `scripts/generate_report_input.json`:

```json
{
  "csv_path": "UserStories.csv",
  "sprint_start": "2026-04-01",
  "sprint_end": "2026-04-14",
  "output": "sprint-report.html"
}
```

Uso con archivo de configuración por defecto:

```bash
python scripts/generate_report.py
```

Uso con archivo de configuración personalizado:

```bash
python scripts/generate_report.py --config ./scripts/generate_report_input.json
```

Uso mixto (override de valores desde línea de comandos):

```bash
python scripts/generate_report.py --config ./scripts/generate_report_input.json --sprint-start 2026-04-07 --sprint-end 2026-04-17
```

#### Uso avanzado y pruebas

- `scripts/generate_report.py` es el único entrypoint de la skill.
- El script lee el CSV, calcula los KPIs y genera directamente el HTML final.

Ejemplo de ejecución:

```bash
python3 scripts/generate_report.py UserStories.csv --sprint-start 2026-04-07 --sprint-end 2026-04-17 --output my-report.html
```

#### Comandos rápidos para desarrollo y pruebas

- Instalar dependencias: `pip install -r requirements.txt` (pandas)
- Comprobación sintáctica de un archivo: `python -m py_compile scripts/generate_report.py`

---

## ✨ Características

### Dashboard

| Métrica | Descripción |
|---------|-------------|
| Total de tickets | Contador de items en el sprint |
| Leftovers | Items que venían de sprints anteriores |
| Abiertos | Tickets pendientes de completar |
| Progreso | Porcentaje con barra visual |
| 📊 Gráfico Donut | Distribución visual Completados/Abiertos/Not Started |

### Scatter Plot de Antigüedad

| Elemento | Significado |
|----------|-------------|
| Eje Y (vertical) | Días desde creación (más arriba = más antiguo) |
| Eje X (horizontal) | Dispersión aleatoria para visibilidad |
| 🟢 Puntos verdes | Tickets completados |
| 🔵 Puntos azules | Tickets en progreso (Open + In Progress) |
| 🟠 Puntos naranja | Tickets no iniciados |

### Diseño Profesional

- ✨ UI inspirada en Apple (Inter font)
- 📱 Responsive para móvil y desktop
- 🖨️ Optimizado para impresión (Ctrl+P → PDF)
- 🎨 Texto oscuro sobre fondo claro
- 📊 Sin dependencias externas (HTML autocontenido)

---

## 📖 Interpretación del Reporte

### Glosario de Términos

| Término | Significado | Por qué importa |
|---------|-------------|-----------------|
| **Leftovers** | Tickets que venían de sprints anteriores | Indica deuda acumulada |
| **WIP** (Work in Progress) | Tickets iniciados pero no terminados | Mucho WIP retrasa entregas |
| **Velocity** | Velocidad de completado (tickets/día) | Ayuda a estimar capacidad |
| **Risk Items** | Tickets abiertos >14 días | Pueden bloquear el sprint |
| **Scatter Plot** | Gráfico de puntos | Visualiza antigüedad de tickets |
| **Left Axis** | Eje izquierdo (Y) | Muestra días de antigüedad |

### Guía Visual

<details>
<summary><b>🎨 Significado de colores en gráficos</b></summary>

| Color | Significado | Tickets incluidos |
|-------|-------------|-------------------|
| 🟢 Verde | Completados | Done, Closed, Rejected |
| 🔵 Azul | Abiertos | Open, In Progress |
| 🟠 Naranja | Not Started | New, Aceptado, otros estados |
| 🔴 Rojo (línea) | Riesgo alto | 28+ días de antigüedad |
| 🟡 Ámbar (línea) | Riesgo moderado | 14+ días de antigüedad |

</details>

<details>
<summary><b>📊 Cómo leer el Scatter Plot</b></summary>

1. **Puntos más arriba** = Tickets más antiguos
2. **Puntos de color** = Agrupados por categoría (verde=completado, azul=abierto, naranja=no iniciado)
3. **Líneas de riesgo:**
   - Ámbar: MODERATE_RISK_DAYS (5): Moderate risk
   - Roja:  y HIGH_RISK_DAYS (8): High risk
4. **Hover** sobre puntos para ver detalles del ticket

**Interpretación:**
- Muchos puntos arriba de la línea roja = Sprint en riesgo
- Puntos azules arriba de línea ámbar = Atención requerida

</details>

---

## ⚡ Rendimiento y Límites

### Recomendaciones

| Métrica | Recomendación | Notas |
|---------|---------------|-------|
| **Tamaño CSV** | Hasta 5,000 tickets | Más allá puede ralentizarse |
| **Tiempo de generación** | < 5 segundos | Para archivos < 1MB |
| **Navegador** | Chrome/Firefox/Safari reciente | Chart.js 4.4.1 requiere ES6 |

### Optimización para CSV grandes

Si tienes más de 3,000 tickets:

```bash
# Filtrar solo el sprint actual antes de exportar
# En Jira: usa el filtro de sprint antes de exportar CSV
```

### Caché de CDN

El reporte usa Chart.js vía CDN (jsdelivr). La primera carga puede tardar ~1s, posteriores usan caché.

---

## 🔧 Solución de Problemas

### Errores comunes

<details>
<summary><b>❌ "No such file or directory: UserStories.csv"</b></summary>

**Causa:** El archivo CSV no está en la carpeta actual.

**Solución:**
```bash
# Usa la ruta completa
python3 scripts/generate_report.py /ruta/completa/a/UserStories.csv ...

# O navega a la carpeta del CSV
cd /ruta/al/csv
python3 /ruta/al/script/generate_report.py UserStories.csv ...
```

</details>

<details>
<summary><b>❌ "ModuleNotFoundError: No module named 'pandas'"</b></summary>

**Causa:** Falta instalar dependencias.

**Solución:**
```bash
pip install pandas
```

</details>

<details>
<summary><b>❌ "ValueError: time data does not match format"</b></summary>

**Causa:** Las fechas no están en formato YYYY-MM-DD.

**Solución:**
```bash
# Formato correcto: 2026-04-07
# Formato incorrecto: 07/04/2026, 7-Apr-2026, etc.

python3 scripts/generate_report.py UserStories.csv \
  --sprint-start 2026-04-07 \
  --sprint-end 2026-04-17
```

</details>

<details>
<summary><b>❌ El gráfico no aparece / está en blanco</b></summary>

**Causa:** Problema de conexión a CDN de Chart.js.

**Soluciones:**
1. Verifica conexión a internet (carga Chart.js desde CDN)
2. Abre el archivo HTML en navegador diferente
3. Espera unos segundos y recarga (puede ser caché)

</details>

<details>
<summary><b>⚠️ PerformanceWarning: DataFrame is highly fragmented</b></summary>

**Causa:** Advertencia de pandas por el modo de procesamiento.

**Impacto:** Solo afecta rendimiento en CSVs >10,000 filas. Para uso normal, ignorar es seguro.

**Solución (opcional):**
```python
# En el código, antes de procesar:
df = df.copy()  # Desfragmenta el DataFrame
```

</details>

### Preguntas frecuentes (FAQ)

**Q: ¿Por qué no veo los nombres de asignados?**
> A: Por privacidad, los asignados se muestran en hover del scatter plot, no en la tabla principal.

**Q: ¿Puedo generar reportes de sprints pasados?**
> A: Sí, solo necesitas el CSV exportado de Jira con las fechas correctas.

**Q: ¿Funciona con otros sistemas además de Jira?**
> A: Sí, siempre que el CSV tenga las columnas requeridas: Issue key, Issue Type, Status, Created, Resolved, Assignee.

**Q: ¿Cómo comparto el reporte?**
> A: El archivo HTML es autocontenido. Puedes enviarlo por email, subirlo a Drive, o compartirlo directamente.

---

## 🤝 Contribuir

1. Fork el repositorio
2. Crea una rama (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Agrega nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crea un Pull Request

### Testing

```bash
# Ejecutar análisis de código
python -m py_compile scripts/generate_report.py

# Verificar con datos de prueba
python scripts/generate_report.py test_data/sample.csv \
  --sprint-start 2026-01-01 \
  --sprint-end 2026-01-14
```

---

## 📝 Changelog

### v1.1.0 (2026-04-14)
- ✨ Agregada sección Highlights con análisis automático
- 🎨 Mejorada consistencia de colores entre gráficos
- 🐛 Corregido mapeo de estados (Open → Abiertos)
- 📚 Documentación mejorada para usuarios no técnicos

### v1.0.0 (2026-04-10)
- 🎉 Lanzamiento inicial
- 📊 Dashboard de completado con donut chart
- 📈 Scatter plot de antigüedad
- 📱 Diseño responsive y print-friendly

---

## 📄 Licencia

MIT License - Libre para uso personal y comercial.

---

<p align="center">
  <b>¿Necesitas ayuda?</b> Abre un issue en el repositorio.<br>
  <b>¿Te gusta?</b> Dale ⭐ al repo!
</p>
