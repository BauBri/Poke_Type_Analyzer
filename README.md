# Pokémon Team Coverage Analyzer

Web app para analizar la **cobertura defensiva por tipos** de un equipo Pokémon bajo reglas **Smogon 1v1**, enfocada exclusivamente en **interacciones de tipos**.

La aplicación permite construir un equipo de hasta 6 Pokémon y evaluar de forma clara:
- Debilidades
- Resistencias
- Inmunidades
- Riesgo defensivo del equipo frente a cada tipo atacante

---

## Características principales

- Selector de Pokémon con filtro por **generación**
- Base de datos completa obtenida desde **Pokémon Showdown**  
  (incluye formas regionales, megas, gmax, etc.)
- Visualización del equipo con **sprites oficiales de Showdown**
- Tabla individual de **debilidades y resistencias por Pokémon**
- Tabla global de **análisis defensivo por tipo atacante**
  - Conteo de inmunidades, resistencias y debilidades
  - Detección de debilidades críticas (x4)
  - Rating defensivo por tipo

---


## Tecnologías utilizadas

- Python 3
- Streamlit
- Pandas
- Requests
- Sprites y datos de Pokémon Showdown

---

## Ejecución local

1. Clona el repositorio:
   ```bash
   git clone https://github.com/tu-usuario/tu-repo.git
   cd tu-repo
