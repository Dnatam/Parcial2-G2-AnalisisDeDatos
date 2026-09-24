import os
import random
import pandas as pd

from simulacion_base import simular_partido

# Selecciones que conforman el grupo mundialista de Cabo Verde.
EQUIPOS_GRUPO = [
    "Cabo Verde",
    "Uruguay",
    "España",
    "Arabia Saudita"
]

# Carga los ratings Elo y verifica que estén disponibles las cuatro selecciones que conforman el grupo.
def cargar_elo_mundial(
    ruta="2.4.Cabo Verde/Data/elo_limpio.csv",
    ruta_alt="Data/elo_limpio.csv"
):
    path = ruta if os.path.exists(ruta) else ruta_alt

    if not os.path.exists(path):
        raise FileNotFoundError(
            f"No se encontró el archivo de Elo en: {path}"
        )

    df_elo = pd.read_csv(path)

    dict_elo = dict(
        zip(
            df_elo["equipo"],
            df_elo["elo_rating"]
        )
    )

    faltantes = [
        equipo
        for equipo in EQUIPOS_GRUPO
        if equipo not in dict_elo
    ]

    if faltantes:
        raise ValueError(
            f"Faltan ratings Elo para los siguientes equipos: {faltantes}"
        )

    return {
        equipo: dict_elo[equipo]
        for equipo in EQUIPOS_GRUPO
    }

# Inicializa la tabla de posiciones del grupo.
def crear_tabla():
    return {
        equipo: {
            "PJ": 0,
            "G": 0,
            "E": 0,
            "P": 0,
            "Pts": 0
        }
        for equipo in EQUIPOS_GRUPO
    }

# Actualiza la tabla de posiciones después de cada partido.
def actualizar_tabla(
    tabla,
    equipo_a,
    equipo_b,
    puntos_a,
    puntos_b
):
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


# Simula los seis partidos del grupo mundialista.
# Todos los encuentros se consideran en sede neutral, por lo que no se aplica el efecto de localía gamma.
def simular_grupo_mundial(
    elo_dict,
    semilla=None
):
    if semilla is not None:
        random.seed(semilla)

    tabla = crear_tabla()

    partidos = [
        ("Cabo Verde", "Uruguay"),
        ("Cabo Verde", "España"),
        ("Cabo Verde", "Arabia Saudita"),
        ("Uruguay", "España"),
        ("Uruguay", "Arabia Saudita"),
        ("España", "Arabia Saudita")
    ]

    resultados_partidos = []

    for equipo_a, equipo_b in partidos:
        puntos_a, puntos_b, resultado = simular_partido(
            equipo_a,
            equipo_b,
            elo_dict,
            neutral=True
        )

        actualizar_tabla(
            tabla,
            equipo_a,
            equipo_b,
            puntos_a,
            puntos_b
        )

        resultados_partidos.append(
            f"{equipo_a} vs {equipo_b} -> {resultado}"
        )

    return tabla, resultados_partidos


# Convierte la tabla del grupo en un DataFrame y la ordena de mayor a menor cantidad de puntos.
def convertir_tabla_dataframe(tabla):
    df_tabla = pd.DataFrame.from_dict(
        tabla,
        orient="index"
    )

    df_tabla.index.name = "Equipo"

    return df_tabla.sort_values(
        by="Pts",
        ascending=False
    ).reset_index()

# Determina el intervalo de posiciones posibles de Cabo Verde utilizando únicamente los puntos obtenidos.
# Si existen equipos empatados en puntos, no se fuerza un desempate porque el modelo no simula marcadores ni diferencia de goles.
def clasificar_posicion_cabo_verde(tabla):
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
    posicion_maxima = (
        equipos_superiores +
        equipos_igualados
    )

    if equipos_igualados == 1:
        return f"{posicion_minima}°"

    return (
        f"Empate "
        f"{posicion_minima}°-{posicion_maxima}°"
    )

# Repite la simulación completa del grupo para estimar la distribución de posiciones de Cabo Verde mediante Monte Carlo.
def monte_carlo_grupo(
    elo_dict,
    n_simulaciones=100000
):
    resultados = {}

    for _ in range(n_simulaciones):
        tabla, _ = simular_grupo_mundial(
            elo_dict
        )

        posicion = clasificar_posicion_cabo_verde(
            tabla
        )

        resultados[posicion] = (
            resultados.get(posicion, 0) + 1
        )

    porcentajes = {
        posicion:
        cantidad / n_simulaciones * 100
        for posicion, cantidad
        in resultados.items()
    }

    return porcentajes


if __name__ == "__main__":
    print(
        "SIMULADOR GENERAL DEL GRUPO MUNDIALISTA"
    )

    try:
        elo_dict = cargar_elo_mundial()

        print(
            "\nRatings Elo del Grupo Mundialista cargados:"
        )

        for equipo, rating in elo_dict.items():
            print(
                f"   • {equipo:<15}: "
                f"{rating} Elo"
            )

        # Ejecuta una simulación individual reproducible para verificar el funcionamiento del grupo.
        tabla, partidos_res = simular_grupo_mundial(
            elo_dict,
            semilla=42
        )

        print(
            "\nResultados de los 6 Partidos Simulados "
            "(Semilla 42):"
        )

        for partido in partidos_res:
            print(f"   {partido}")

        df_final = convertir_tabla_dataframe(
            tabla
        )

        print("\nTabla Final del Grupo:")
        print(
            df_final.to_string(
                index=False
            )
        )

        print(
            "\nNota: si dos o más equipos terminan con los mismos puntos, el modelo no aplica criterios de desempate porque no simula marcadores.")

        # Repite el grupo completo para estimar la distribución de posiciones de Cabo Verde.
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

        for posicion, porcentaje in sorted(
            resultados_mc.items()
        ):
            print(
                f"{posicion:<20}: "
                f"{porcentaje:.2f}%"
            )

    except Exception as e:
        print(
            f"\nError durante la ejecución: {e}"
        )