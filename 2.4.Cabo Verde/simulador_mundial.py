import os
import random
import pandas as pd
from simulacion_base import simular_partido


# DÍA 7 - INTEGRANTE 1: SIMULADOR GENERAL INCONDICIONAL DEL GRUPO MUNDIALISTA
EQUIPOS_GRUPO = ["Cabo Verde", "Uruguay", "España", "Arabia Saudita"]


def cargar_elo_mundial(
    ruta="2.4.Cabo Verde/Data/elo_limpio.csv", ruta_alt="Data/elo_limpio.csv"
):
    """Carga los ratings Elo verificando la presencia de los 4 equipos del grupo."""
    path = ruta if os.path.exists(ruta) else ruta_alt
    if not os.path.exists(path):
        raise FileNotFoundError(f"No se encontró el archivo de Elo en: {path}")

    df_elo = pd.read_csv(path)
    dict_elo = dict(zip(df_elo["equipo"], df_elo["elo_rating"]))

    faltantes = [eq for eq in EQUIPOS_GRUPO if eq not in dict_elo]
    if faltantes:
        raise ValueError(
            f"Faltan ratings Elo para los siguientes equipos: {faltantes}"
        )

    return {eq: dict_elo[eq] for eq in EQUIPOS_GRUPO}


def crear_tabla():
    """Inicializa la estructura de la tabla de posiciones."""
    return {
        eq: {"PJ": 0, "G": 0, "E": 0, "P": 0, "Pts": 0} for eq in EQUIPOS_GRUPO
    }


def actualizar_tabla(tabla, equipo_a, equipo_b, pts_a, pts_b):
    """Actualiza la tabla con los puntos y estadísticas de un partido."""
    tabla[equipo_a]["PJ"] += 1
    tabla[equipo_b]["PJ"] += 1
    tabla[equipo_a]["Pts"] += pts_a
    tabla[equipo_b]["Pts"] += pts_b

    if pts_a == 3:
        tabla[equipo_a]["G"] += 1
        tabla[equipo_b]["P"] += 1
    elif pts_b == 3:
        tabla[equipo_b]["G"] += 1
        tabla[equipo_a]["P"] += 1
    else:
        tabla[equipo_a]["E"] += 1
        tabla[equipo_b]["E"] += 1


def simular_grupo_mundial(elo_dict, semilla=None):
    """Simula los 6 partidos incondicionales del grupo mundialista."""
    if semilla is not None:
        random.seed(semilla)

    tabla = crear_tabla()
    partidos = [
        ("Cabo Verde", "Uruguay"),
        ("Cabo Verde", "España"),
        ("Cabo Verde", "Arabia Saudita"),
        ("Uruguay", "España"),
        ("Uruguay", "Arabia Saudita"),
        ("España", "Arabia Saudita"),
    ]

    resultados_partidos = []
    for eq_a, eq_b in partidos:
        pts_a, pts_b, res_str = simular_partido(eq_a, eq_b, elo_dict)
        actualizar_tabla(tabla, eq_a, eq_b, pts_a, pts_b)
        resultados_partidos.append(f"{eq_a} vs {eq_b} -> {res_str}")

    return tabla, resultados_partidos


def convertir_tabla_dataframe(tabla):
    """Convierte la tabla a DataFrame y la ordena por Puntos y Victorias."""
    df_tabla = pd.DataFrame.from_dict(tabla, orient="index")
    df_tabla.index.name = "Equipo"
    return df_tabla.sort_values(
        by=["Pts", "G"], ascending=[False, False]
    ).reset_index()


# EJECUCIÓN PRINCIPAL
if __name__ == "__main__":
    print("SIMULADOR GENERAL DEL GRUPO MUNDIALISTA")

    try:
        elo_dict = cargar_elo_mundial()
        print("\nRatings Elo del Grupo Mundialista cargados:")
        for equipo, rating in elo_dict.items():
            print(f"   • {equipo:<15}: {rating} Elo")

        # Simulación única de prueba
        tabla, partidos_res = simular_grupo_mundial(elo_dict, semilla=42)

        print("\nResultados de los 6 Partidos Simulados (Semilla 42):")
        for p in partidos_res:
            print(f"   {p}")

        df_final = convertir_tabla_dataframe(tabla)

        print("\nTabla Final del Grupo:")
        print(df_final.to_string(index=False))

    except Exception as e:
        print(f"\nError durante la ejecución: {e}")
