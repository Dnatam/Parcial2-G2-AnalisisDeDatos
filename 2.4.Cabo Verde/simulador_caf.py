import random
import pandas as pd

from itertools import combinations
from simulacion_base import simular_partido

# Selecciones del grupo clasificatorio de Cabo Verde
EQUIPOS_GRUPO = [
    "Cabo Verde",
    "Camerún",
    "Libia",
    "Angola",
    "Mauricio",
    "Esuatini"
]

# Carga los ratings Elo necesarios para la simulación
def cargar_elo(ruta="Data/elo_limpio.csv"):
    df_elo = pd.read_csv(ruta)

    elo_dict = dict(
        zip(
            df_elo["equipo"],
            df_elo["elo_rating"]
        )
    )

    # Verificar que todas las selecciones del grupo tengan Elo disponible
    faltantes = [
        equipo
        for equipo in EQUIPOS_GRUPO
        if equipo not in elo_dict
    ]

    if faltantes:
        raise ValueError(
            f"Faltan ratings Elo para: {faltantes}"
        )

    return elo_dict

# Crea una tabla vacía para registrar el rendimiento de cada selección
def crear_tabla():
    tabla = {}

    for equipo in EQUIPOS_GRUPO:
        tabla[equipo] = {
            "PJ": 0,
            "G": 0,
            "E": 0,
            "P": 0,
            "Pts": 0
        }

    return tabla

# Actualiza la tabla después de cada partido
def actualizar_tabla(tabla, equipo_a, equipo_b, puntos_a, puntos_b):
    tabla[equipo_a]["PJ"] += 1
    tabla[equipo_b]["PJ"] += 1

    tabla[equipo_a]["Pts"] += puntos_a
    tabla[equipo_b]["Pts"] += puntos_b

    if puntos_a == 3:
        tabla[equipo_a]["G"] += 1
        tabla[equipo_b]["P"] += 1

    elif puntos_b == 3:
        tabla[equipo_b]["G"] += 1
        tabla[equipo_a]["P"] += 1

    else:
        tabla[equipo_a]["E"] += 1
        tabla[equipo_b]["E"] += 1

# Simula todos los partidos del grupo en formato ida y vuelta
def simular_grupo(elo_dict, k_empate=0.3237):
    tabla = crear_tabla()
    partidos = []

    # Cada pareja se enfrenta dos veces
    for equipo_a, equipo_b in combinations(EQUIPOS_GRUPO, 2):

        # Partido de ida
        puntos_a, puntos_b, resultado = simular_partido(
            equipo_a,
            equipo_b,
            elo_dict,
            k_empate
        )

        actualizar_tabla(
            tabla,
            equipo_a,
            equipo_b,
            puntos_a,
            puntos_b
        )

        partidos.append({
            "Local": equipo_a,
            "Visitante": equipo_b,
            "Resultado": resultado
        })

        # Partido de vuelta
        puntos_b, puntos_a, resultado = simular_partido(
            equipo_b,
            equipo_a,
            elo_dict,
            k_empate
        )

        actualizar_tabla(
            tabla,
            equipo_b,
            equipo_a,
            puntos_b,
            puntos_a
        )

        partidos.append({
            "Local": equipo_b,
            "Visitante": equipo_a,
            "Resultado": resultado
        })

    return tabla, partidos

# Convierte el diccionario de resultados en una tabla ordenada por puntos
def convertir_tabla_dataframe(tabla):
    df_tabla = pd.DataFrame.from_dict(
        tabla,
        orient="index"
    )

    df_tabla.index.name = "Equipo"

    df_tabla = df_tabla.sort_values(
        by="Pts",
        ascending=False
    )

    return df_tabla

# Determina al ganador del grupo
def obtener_ganador(tabla):
    max_puntos = max(
        datos["Pts"]
        for datos in tabla.values()
    )

    lideres = [
        equipo
        for equipo, datos in tabla.items()
        if datos["Pts"] == max_puntos
    ]

    return random.choice(lideres)


if __name__ == "__main__":
    print("DÍA 5 - CABO VERDE: SIMULACIÓN DEL GRUPO CAF")

    elo_dict = cargar_elo()

    # Semilla para poder reproducir esta simulación de ejemplo
    random.seed(42)

    tabla, partidos = simular_grupo(elo_dict)
    df_tabla = convertir_tabla_dataframe(tabla)

    ganador = obtener_ganador(tabla)

    print("\n--- PARTIDOS SIMULADOS ---")

    for i, partido in enumerate(partidos, start=1):
        print(
            f"{i:02d}. "
            f"{partido['Local']} vs {partido['Visitante']} "
            f"-> {partido['Resultado']}"
        )

    print("\n--- TABLA FINAL DEL GRUPO ---")
    print(df_tabla.to_string())

    print("\n--- CLASIFICACIÓN DIRECTA ---")
    print(f"Ganador del grupo: {ganador}")

    if ganador == "Cabo Verde":
        print("Cabo Verde clasifica directamente.")
    else:
        print("Cabo Verde no clasifica directamente.")