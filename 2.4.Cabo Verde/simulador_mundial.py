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
    """Convierte la tabla a DataFrame y la ordena solo por Puntos."""
    df_tabla = pd.DataFrame.from_dict(tabla, orient="index")
    df_tabla.index.name = "Equipo"
    return df_tabla.sort_values(
        by="Pts", ascending=False
    ).reset_index()

def clasificar_posicion_cabo_verde(tabla):
    """Determina la posición de Cabo Verde únicamente por puntos."""
    puntos_cv = tabla["Cabo Verde"]["Pts"]

    equipos_superiores = sum(
        1
        for equipo in EQUIPOS_GRUPO
        if tabla[equipo]["Pts"] > puntos_cv
    )

    equipos_igualados = sum(
        1
        for equipo in EQUIPOS_GRUPO
        if tabla[equipo]["Pts"] == puntos_cv
    )

    posicion_minima = equipos_superiores + 1
    posicion_maxima = equipos_superiores + equipos_igualados

    if equipos_igualados == 1:
        return f"{posicion_minima}°"

    return f"Empate {posicion_minima}°-{posicion_maxima}°"


def monte_carlo_grupo(elo_dict, n_simulaciones=100000):
    """Simula el grupo completo muchas veces y registra la posición de Cabo Verde."""
    resultados = {}

    for _ in range(n_simulaciones):
        tabla, _ = simular_grupo_mundial(elo_dict)

        posicion = clasificar_posicion_cabo_verde(tabla)

        resultados[posicion] = resultados.get(posicion, 0) + 1

    porcentajes = {
        posicion: cantidad / n_simulaciones * 100
        for posicion, cantidad in resultados.items()
    }

    return porcentajes

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

        print(
            "\nNota: si dos o más equipos terminan con los mismos puntos, "
            "el modelo no aplica criterios de desempate porque no simula marcadores."
        )

            # Monte Carlo del grupo completo
        n_simulaciones = 100000

        print(
            f"\nEJECUTANDO MONTE CARLO DEL GRUPO "
            f"({n_simulaciones:,} simulaciones)..."
        )

        random.seed(42)

        resultados_mc = monte_carlo_grupo(
            elo_dict,
            n_simulaciones
        )

        print("\nPROBABILIDAD DE POSICIÓN DE CABO VERDE:")

        for posicion, porcentaje in sorted(resultados_mc.items()):
            print(
                f"{posicion:<20}: "
                f"{porcentaje:.2f}%"
            )

    except Exception as e:
        print(f"\nError durante la ejecución: {e}")