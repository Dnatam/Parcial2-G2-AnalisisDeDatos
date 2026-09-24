import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from simulacion_base import (
    obtener_lambdas,
    simular_partido
)


# CONFIGURACIÓN

EQUIPOS_GRUPO = [
    "Cabo Verde",
    "Uruguay",
    "España",
    "Arabia Saudita"
]

N_SIMULACIONES = 100000


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


# SIMULAR UN EMPATE CONDICIONADO

def simular_empate(
    equipo_a,
    equipo_b,
    elo_dict,
    neutral=True
):
    """
    Genera un marcador de empate utilizando las distribuciones
    Poisson del modelo.

    Se repite la generación hasta obtener el mismo número
    de goles para ambos equipos.

    Esto permite representar un empate forzado sin elegir
    arbitrariamente 0-0, 1-1, 2-2, etc.
    """

    elo_a = elo_dict[equipo_a]
    elo_b = elo_dict[equipo_b]

    lambda_a, lambda_b = obtener_lambdas(
        elo_a,
        elo_b,
        neutral
    )

    while True:

        goles_a = np.random.poisson(
            lambda_a
        )

        goles_b = np.random.poisson(
            lambda_b
        )

        if goles_a == goles_b:

            return (
                1,
                1,
                int(goles_a),
                int(goles_b),
                f"Empate {goles_a}-{goles_b}"
            )


# ============================================================
# SIMULAR UNA VICTORIA CONDICIONADA
# ============================================================

def simular_victoria(
    equipo_a,
    equipo_b,
    elo_dict,
    neutral=True
):
    """
    Genera un marcador condicionado a que el equipo A gane.
    """

    elo_a = elo_dict[equipo_a]
    elo_b = elo_dict[equipo_b]

    lambda_a, lambda_b = obtener_lambdas(
        elo_a,
        elo_b,
        neutral
    )

    while True:

        goles_a = np.random.poisson(
            lambda_a
        )

        goles_b = np.random.poisson(
            lambda_b
        )

        if goles_a > goles_b:

            return (
                3,
                0,
                int(goles_a),
                int(goles_b),
                f"Victoria {equipo_a} {goles_a}-{goles_b}"
            )


# SIMULAR EL RESTO DE PARTIDOS DEL GRUPO

def simular_partido_normal(
    tabla,
    equipo_a,
    equipo_b,
    elo_dict
):

    resultado = simular_partido(
        equipo_a,
        equipo_b,
        elo_dict,
        neutral=True
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

    return texto


# APLICAR LOS TRES EMPATES DE CABO VERDE

def aplicar_empates_cabo_verde(
    tabla,
    elo_dict
):

    rivales = [
        "Uruguay",
        "España",
        "Arabia Saudita"
    ]

    resultados = {}

    for rival in rivales:

        (
            puntos_cv,
            puntos_rival,
            goles_cv,
            goles_rival,
            texto
        ) = simular_empate(
            "Cabo Verde",
            rival,
            elo_dict,
            neutral=True
        )

        actualizar_tabla(
            tabla,
            "Cabo Verde",
            rival,
            puntos_cv,
            puntos_rival,
            goles_cv,
            goles_rival
        )

        resultados[
            f"Cabo Verde-{rival}"
        ] = texto

    return resultados


# ESCENARIO 1:
# URUGUAY EMPATA CON ESPAÑA

def escenario_uruguay_empata_espana(
    elo_dict
):

    tabla = crear_tabla()

    resultados = aplicar_empates_cabo_verde(
        tabla,
        elo_dict
    )

    (
        puntos_uru,
        puntos_esp,
        goles_uru,
        goles_esp,
        resultado_uru_esp
    ) = simular_empate(
        "Uruguay",
        "España",
        elo_dict,
        neutral=True
    )

    actualizar_tabla(
        tabla,
        "Uruguay",
        "España",
        puntos_uru,
        puntos_esp,
        goles_uru,
        goles_esp
    )

    resultados[
        "Uruguay-España"
    ] = resultado_uru_esp

    # Uruguay vs Arabia Saudita
    resultado_1 = simular_partido_normal(
        tabla,
        "Uruguay",
        "Arabia Saudita",
        elo_dict
    )

    resultados[
        "Uruguay-Arabia Saudita"
    ] = resultado_1

    # España vs Arabia Saudita
    resultado_2 = simular_partido_normal(
        tabla,
        "España",
        "Arabia Saudita",
        elo_dict
    )

    resultados[
        "España-Arabia Saudita"
    ] = resultado_2

    return tabla, resultados


# ESCENARIO 2:
# URUGUAY VENCE A ESPAÑA

def escenario_uruguay_gana_espana(
    elo_dict
):

    tabla = crear_tabla()

    resultados = aplicar_empates_cabo_verde(
        tabla,
        elo_dict
    )

    (
        puntos_uru,
        puntos_esp,
        goles_uru,
        goles_esp,
        resultado_uru_esp
    ) = simular_victoria(
        "Uruguay",
        "España",
        elo_dict,
        neutral=True
    )

    actualizar_tabla(
        tabla,
        "Uruguay",
        "España",
        puntos_uru,
        puntos_esp,
        goles_uru,
        goles_esp
    )

    resultados[
        "Uruguay-España"
    ] = resultado_uru_esp

    # Uruguay vs Arabia Saudita
    resultado_1 = simular_partido_normal(
        tabla,
        "Uruguay",
        "Arabia Saudita",
        elo_dict
    )

    resultados[
        "Uruguay-Arabia Saudita"
    ] = resultado_1

    # España vs Arabia Saudita
    resultado_2 = simular_partido_normal(
        tabla,
        "España",
        "Arabia Saudita",
        elo_dict
    )

    resultados[
        "España-Arabia Saudita"
    ] = resultado_2

    return tabla, resultados


# ORDENAR TABLA

def ordenar_tabla(tabla):

    equipos = sorted(
        tabla.keys(),
        key=lambda equipo: (
            tabla[equipo]["Pts"],
            tabla[equipo]["DG"],
            tabla[equipo]["GF"]
        ),
        reverse=True
    )

    return equipos


# OBTENER POSICIÓN DE CABO VERDE

def clasificar_posicion_cabo_verde(
    tabla
):

    equipos_ordenados = ordenar_tabla(
        tabla
    )

    posicion_cv = (
        equipos_ordenados.index(
            "Cabo Verde"
        )
        + 1
    )

    return f"{posicion_cv}°"


# CONVERTIR TABLA

def convertir_tabla_dataframe(
    tabla
):

    df = pd.DataFrame.from_dict(
        tabla,
        orient="index"
    )

    df.index.name = "Equipo"

    df = df.sort_values(
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

    return df


# MONTE CARLO - ESCENARIO 1

def monte_carlo_escenario(
    funcion_escenario,
    elo_dict
):

    conteo_posiciones = {
        "1°": 0,
        "2°": 0,
        "3°": 0,
        "4°": 0
    }

    for _ in range(
        N_SIMULACIONES
    ):

        tabla, _ = funcion_escenario(
            elo_dict
        )

        posicion = clasificar_posicion_cabo_verde(
            tabla
        )

        conteo_posiciones[
            posicion
        ] += 1

    resultados = {}

    for posicion, cantidad in conteo_posiciones.items():

        resultados[posicion] = (
            cantidad
            / N_SIMULACIONES
        )

    return resultados


# MOSTRAR RESULTADOS

def imprimir_resultados(
    nombre_escenario,
    resultados
):

    print(
        f"\n{'=' * 70}"
    )

    print(
        nombre_escenario
    )

    print(
        f"{'=' * 70}"
    )

    for posicion in [
        "1°",
        "2°",
        "3°",
        "4°"
    ]:

        probabilidad = (
            resultados[posicion]
            * 100
        )

        print(
            f"Cabo Verde termina {posicion}: "
            f"{probabilidad:.2f}%"
        )


# PROGRAMA PRINCIPAL

if __name__ == "__main__":

    print("=" * 70)
    print("CABO VERDE - ESCENARIOS DEL MUNDIAL")
    print("=" * 70)

    random.seed(42)
    np.random.seed(42)

    elo_dict = cargar_elo()

    # EJEMPLO DE UNA SIMULACIÓN INDIVIDUAL

    print(
        "\nEJEMPLO DE SIMULACIÓN:"
    )

    tabla_ejemplo, resultados_ejemplo = (
        escenario_uruguay_empata_espana(
            elo_dict
        )
    )

    print(
        "\nPARTIDOS"
    )

    for partido, resultado in resultados_ejemplo.items():

        print(
            f"{partido}: {resultado}"
        )

    print(
        "\nTABLA FINAL"
    )

    df_ejemplo = convertir_tabla_dataframe(
        tabla_ejemplo
    )

    print(
        df_ejemplo.to_string()
    )

    print(
        "\nPOSICIÓN DE CABO VERDE:"
    )

    print(
        clasificar_posicion_cabo_verde(
            tabla_ejemplo
        )
    )

    # MONTE CARLO ESCENARIO 1

    print(
        "\n\nEJECUTANDO MONTE CARLO..."
    )

    resultados_escenario_1 = (
        monte_carlo_escenario(
            escenario_uruguay_empata_espana,
            elo_dict
        )
    )

    resultados_escenario_2 = (
        monte_carlo_escenario(
            escenario_uruguay_gana_espana,
            elo_dict
        )
    )

    # MOSTRAR RESULTADOS

    imprimir_resultados(
        "ESCENARIO 1: URUGUAY EMPATA CON ESPAÑA",
        resultados_escenario_1
    )

    imprimir_resultados(
        "ESCENARIO 2: URUGUAY VENCE A ESPAÑA",
        resultados_escenario_2
    )

    # GUARDAR RESULTADOS

    df_resultados = pd.DataFrame({
        "Posición": [
            "1°",
            "2°",
            "3°",
            "4°"
        ],
        "Uruguay empata con España": [
            resultados_escenario_1["1°"],
            resultados_escenario_1["2°"],
            resultados_escenario_1["3°"],
            resultados_escenario_1["4°"]
        ],
        "Uruguay vence a España": [
            resultados_escenario_2["1°"],
            resultados_escenario_2["2°"],
            resultados_escenario_2["3°"],
            resultados_escenario_2["4°"]
        ]
    })

    df_resultados.to_csv(
        "Data/resultados_escenarios_mundial.csv",
        index=False
    )

    # --------------------------------------------------------
    # GRÁFICA
    # --------------------------------------------------------

    x = np.arange(4)

    ancho = 0.35

    plt.figure(
        figsize=(10, 6)
    )

    plt.bar(
        x - ancho / 2,
        df_resultados[
            "Uruguay empata con España"
        ] * 100,
        width=ancho,
        label="Uruguay empata con España"
    )

    plt.bar(
        x + ancho / 2,
        df_resultados[
            "Uruguay vence a España"
        ] * 100,
        width=ancho,
        label="Uruguay vence a España"
    )

    plt.xticks(
        x,
        df_resultados["Posición"]
    )

    plt.xlabel(
        "Posición final de Cabo Verde"
    )

    plt.ylabel(
        "Probabilidad (%)"
    )

    plt.title(
        "Escenarios de clasificación de Cabo Verde"
    )

    plt.legend()

    plt.tight_layout()

    plt.savefig(
        "Graficas/escenarios_mundial.png",
        dpi=300
    )

    plt.close()

    print(
        "\nResultados guardados en:"
    )

    print(
        "Data/resultados_escenarios_mundial.csv"
    )

    print(
        "Graficas/escenarios_mundial.png"
    )