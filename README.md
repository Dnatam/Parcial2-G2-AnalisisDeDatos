# Parcial-2---Grupo-2---Analisis-de-Datos
Simulación Monte Carlo  y análisis de probabilidades: Chelsea y Cabo Verde.

## Documentación de Datos y Fuentes (Auditoría Día 2)

### 1. Caso Chelsea ("I think I'm a special one")
* **Fuente oficial:** [Football-Data.co.uk](https://www.football-data.co.uk/)
* **Cobertura:** 31 temporadas completas de la Premier League (1995-1996 a 2025-2026).
* **Estructura de variables:**
  * `HomeTeam`: Equipo local.
  * `AwayTeam`: Equipo visitante.
  * `FTHG` (*Full Time Home Goals*): Goles anotados por el equipo local.
  * `FTAG` (*Full Time Away Goals*): Goles anotados por el equipo visitante.
  * `FTR` (*Full Time Result*): Resultado final del partido (`H` = Victoria Local, `D` = Empate, `A` = Victoria Visitante).

### 2. Caso Cabo Verde ("La nueva cenicienta del fútbol")
* **Fuente de Ratings:** World Football Elo Ratings (`eloratings.net` / `clubelo.com`).
* **Fecha de corte de datos:** Agosto de 2026.
* **Selecciones Registradas (13 en total):**
  * **Grupo CAF:** Cabo Verde, Camerún, Libia, Angola, Mauricio, Esuatini.
  * **Fase de Grupos Mundial:** Uruguay, España, Arabia Saudita.
  * **Fase Eliminatoria:** Egipto, Suiza, Inglaterra, Argentina.
* **Reglas del Torneo Clasificatorio CAF a Simular:**
  * Grupo único de 6 selecciones en formato ida y vuelta (10 partidos por equipo).
  * Puntuación estándar: 3 puntos por victoria, 1 por empate, 0 por derrota.
  * **Criterio de éxito:** El primer lugar del grupo obtiene la clasificación directa al Mundial (sin considerar repechaje).