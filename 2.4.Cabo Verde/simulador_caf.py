import random
import numpy as np
import pandas as pd
from itertools import combinations

from simulacion_base import simular_partido


# CONFIGURACIÓN

EQUIPOS_GRUPO = [
    "Cabo Verde",
    "Camerún",
    "Libia",
    "Angola",
    "Mauricio",
    "Esuatini"
]


# CARGAR ELO

def cargar_elo(ruta="Data/elo_limpio.csv"):

    df_elo = pd.read_csv(ruta)

    elo_dict = dict(
        zip(
            df_elo["equipo"],
            df_elo["elo_rating"]
        )
    )

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


# CREAR TABLA

def crear_tabla():

    tabla = {}

    for equipo in EQUIPOS_GRUPO:

        tabla[equipo] = {
            "PJ": 0,
            "G": 0,
            "E": 0,
            "P": 0,
            "GF": 0,
            "GC": 0,
            "DG": 0,
            "Pts": 0
        }

    return tabla


# ACTUALIZAR TABLA

def actualizar_tabla(
    tabla,
    equipo_a,
    equipo_b,
    puntos_a,
    puntos_b,
    goles_a,
    goles_b
):

    tabla[equipo_a]["PJ"] += 1
    tabla[equipo_b]["PJ"] += 1

    tabla[equipo_a]["GF"] += goles_a
    tabla[equipo_a]["GC"] += goles_b

    tabla[equipo_b]["GF"] += goles_b
    tabla[equipo_b]["GC"] += goles_a

    tabla[equipo_a]["DG"] = (
        tabla[equipo_a]["GF"]
        - tabla[equipo_a]["GC"]
    )

    tabla[equipo_b]["DG"] = (
        tabla[equipo_b]["GF"]
        - tabla[equipo_b]["GC"]
    )

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


# SIMULAR GRUPO

def simular_grupo(elo_dict):

    tabla = crear_tabla()
    partidos = []

    # Cada pareja juega dos partidos:
    # ida y vuelta.
    for equipo_a, equipo_b in combinations(
        EQUIPOS_GRUPO,
        2
    ):

        # Primer partido
        resultado = simular_partido(
            equipo_a,
            equipo_b,
            elo_dict,
            neutral=False
        )

        (
            puntos_a,
            puntos_b,
            goles_a,
            goles_b,
            texto
        ) = resultado

        actualizar_tabla(
            tabla,
            equipo_a,
            equipo_b,
            puntos_a,
            puntos_b,
            goles_a,
            goles_b
        )

        partidos.append({
            "Local": equipo_a,
            "Visitante": equipo_b,
            "Goles Local": goles_a,
            "Goles Visitante": goles_b,
            "Resultado": texto
        })

        # Segundo partido
        resultado = simular_partido(
            equipo_b,
            equipo_a,
            elo_dict,
            neutral=False
        )

        (
            puntos_b,
            puntos_a,
            goles_b,
            goles_a,
            texto
        ) = resultado

        actualizar_tabla(
            tabla,
            equipo_b,
            equipo_a,
            puntos_b,
            puntos_a,
            goles_b,
            goles_a
        )

        partidos.append({
            "Local": equipo_b,
            "Visitante": equipo_a,
            "Goles Local": goles_b,
            "Goles Visitante": goles_a,
            "Resultado": texto
        })

    return tabla, partidos


# CONVERTIR TABLA A DATAFRAME

def convertir_tabla_dataframe(tabla):

    df_tabla = pd.DataFrame.from_dict(
        tabla,
        orient="index"
    )

    df_tabla.index.name = "Equipo"

    df_tabla = df_tabla.sort_values(
        by=[
            "Pts",
            "DG",
            "GF"
        ],
        ascending=[
            False,
            False,
            False
        ]
    )

    return df_tabla


# OBTENER GANADOR

def obtener_ganador(tabla):

    equipos_ordenados = sorted(
        tabla.keys(),
        key=lambda equipo: (
            tabla[equipo]["Pts"],
            tabla[equipo]["DG"],
            tabla[equipo]["GF"]
        ),
        reverse=True
    )

    # Identificar si todavía existe empate completo.
    mejor = equipos_ordenados[0]

    candidatos = [
        equipo
        for equipo in equipos_ordenados
        if (
            tabla[equipo]["Pts"],
            tabla[equipo]["DG"],
            tabla[equipo]["GF"]
        )
        == (
            tabla[mejor]["Pts"],
            tabla[mejor]["DG"],
            tabla[mejor]["GF"]
        )
    ]

    return random.choice(candidatos)


# PRUEBA

if __name__ == "__main__":

    print("=" * 70)
    print("CABO VERDE - SIMULACIÓN DE CLASIFICACIÓN CAF")
    print("=" * 70)

    random.seed(42)
    np.random.seed(42)

    elo_dict = cargar_elo()

    tabla, partidos = simular_grupo(
        elo_dict
    )

    df_tabla = convertir_tabla_dataframe(
        tabla
    )

    ganador = obtener_ganador(
        tabla
    )

    print("\nPARTIDOS SIMULADOS")

    for i, partido in enumerate(
        partidos,
        start=1
    ):

        print(
            f"{i:02d}. "
            f"{partido['Local']} "
            f"{partido['Goles Local']}-"
            f"{partido['Goles Visitante']} "
            f"{partido['Visitante']} "
            f"-> {partido['Resultado']}"
        )

    print("\nTABLA FINAL")

    print(
        df_tabla.to_string()
    )

    print("\nCLASIFICACIÓN DIRECTA")

    print(
        f"Ganador del grupo: {ganador}"
    )

    if ganador == "Cabo Verde":

        print(
            "Cabo Verde clasifica directamente."
        )

    else:

        print(
            "Cabo Verde no clasifica directamente."
        )