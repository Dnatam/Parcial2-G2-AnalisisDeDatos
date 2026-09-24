import random
import numpy as np
import pandas as pd

from simulacion_base import (
    obtener_probabilidades_partido,
    simular_partido
)

from simulador_mundial import (
    cargar_elo,
    verificar_equipos
)

# CONFIGURACIÓN
N_SIMULACIONES = 100000
SEMILLA = 42

RIVALES = [
    "Egipto",
    "Suiza",
    "Inglaterra",
    "España"
]

# Calcula la probabilidad de que Cabo Verde avance contra un rival.
# Como el escenario supone que Cabo Verde avanza en penales si empata, se consideran favorables tanto la victoria como el empate.
def calcular_probabilidad_avance(
    elo_cv,
    elo_rival
):
    p_victoria, p_empate, p_derrota = (
        obtener_probabilidades_partido(
            elo_cv,
            elo_rival,
            neutral=True
        )
    )

    p_avance = (
        p_victoria
        + p_empate
    )

    return (
        p_victoria,
        p_empate,
        p_derrota,
        p_avance
    )

# Calcula analíticamente la probabilidad de que Cabo Verde supere consecutivamente a Egipto, Suiza, Inglaterra y España.
def calcular_camino_analitico(
    elo_dict
):
    resultados = []

    probabilidad_campeon = 1.0

    elo_cv = elo_dict[
        "Cabo Verde"
    ]

    for rival in RIVALES:

        elo_rival = elo_dict[
            rival
        ]

        (
            p_victoria,
            p_empate,
            p_derrota,
            p_avance
        ) = calcular_probabilidad_avance(
            elo_cv,
            elo_rival
        )

        probabilidad_campeon *= (
            p_avance
        )

        resultados.append({
            "Rival": rival,
            "Elo Cabo Verde": elo_cv,
            "Elo Rival": elo_rival,
            "P Victoria": p_victoria,
            "P Empate": p_empate,
            "P Derrota": p_derrota,
            "P Avance": p_avance
        })

    return (
        resultados,
        probabilidad_campeon
    )

# Simula una trayectoria completa de Cabo Verde hacia el título.
# Si Cabo Verde gana o empata, avanza a la siguiente ronda. Si pierde algún partido, queda eliminado inmediatamente.
def simular_camino_titulo(
    elo_dict
):
    partidos_superados = 0

    for rival in RIVALES:

        (
            puntos_cv,
            puntos_rival,
            goles_cv,
            goles_rival,
            resultado
        ) = simular_partido(
            "Cabo Verde",
            rival,
            elo_dict,
            neutral=True
        )

        # Si Cabo Verde pierde el partido, su trayectoria hacia el título termina.
        if puntos_cv == 0:
            return (
                False,
                partidos_superados,
                rival
            )

        # Una victoria permite avanzar directamente. 
        # Un empate también permite avanzar porque el escenario supone que Cabo Verde gana la definición por penales.
        partidos_superados += 1

    # Si supera los cuatro partidos, Cabo Verde termina como campeón.
    return (
        True,
        partidos_superados,
        None
    )

# Ejecuta muchas trayectorias completas para estimar mediante Monte Carlo la probabilidad de que Cabo Verde gane el Mundial.
def ejecutar_monte_carlo(
    elo_dict,
    n_simulaciones=N_SIMULACIONES
):
    veces_campeon = 0

    eliminaciones = {
        rival: 0
        for rival in RIVALES
    }

    for i in range(
        n_simulaciones
    ):

        (
            campeon,
            partidos_superados,
            rival_eliminacion
        ) = simular_camino_titulo(
            elo_dict
        )

        if campeon:

            veces_campeon += 1

        else:

            eliminaciones[
                rival_eliminacion
            ] += 1

        # Muestra el avance de la simulación cada 10,000 iteraciones.
        if (i + 1) % 10000 == 0:

            print(
                f"Simulaciones completadas: "
                f"{i + 1:,}/"
                f"{n_simulaciones:,}"
            )

    probabilidad_campeon = (
        veces_campeon
        /
        n_simulaciones
    )

    return (
        veces_campeon,
        probabilidad_campeon,
        eliminaciones
    )

# PROGRAMA PRINCIPAL
if __name__ == "__main__":

    print(
        "CABO VERDE - CAMINO AL TÍTULO MUNDIAL 2026"
    )

    print(
        "ESCENARIO: LOS EMPATES SE RESUELVEN A FAVOR DE CABO VERDE EN PENALES"
    )

    # Fija las semillas para que los resultados de Monte Carlo puedan reproducirse.
    random.seed(
        SEMILLA
    )

    np.random.seed(
        SEMILLA
    )

    # Carga los ratings Elo utilizados en las simulaciones del Mundial.
    elo_dict = cargar_elo()

    verificar_equipos(
        elo_dict
    )

    # Verifica específicamente que todos los rivales necesarios para este escenario estén disponibles.
    equipos_necesarios = [
        "Cabo Verde"
    ] + RIVALES

    faltantes = [
        equipo
        for equipo in equipos_necesarios
        if equipo not in elo_dict
    ]

    if faltantes:

        raise ValueError(
            f"Faltan ratings Elo para: "
            f"{faltantes}"
        )

    print("\nRATINGS ELO UTILIZADOS")

    for equipo in equipos_necesarios:

        print(
            f"{equipo:<15}: "
            f"{elo_dict[equipo]:.0f}"
        )

    # Calcula las probabilidades teóricas de cada partido utilizando el modelo Elo-Poisson-Skellam.
    (
        resultados_analiticos,
        probabilidad_analitica_campeon
    ) = calcular_camino_analitico(
        elo_dict
    )

    print("\n")
    print("PROBABILIDADES POR PARTIDO")

    for datos in resultados_analiticos:

        print("\n")
        print(
            f"Cabo Verde vs "
            f"{datos['Rival']}"
        )

        print(
            f"Victoria Cabo Verde: "
            f"{datos['P Victoria'] * 100:.2f}%"
        )

        print(
            f"Empate: "
            f"{datos['P Empate'] * 100:.2f}%"
        )

        print(
            f"Derrota Cabo Verde: "
            f"{datos['P Derrota'] * 100:.2f}%"
        )

        print(
            f"Probabilidad de avanzar: "
            f"{datos['P Avance'] * 100:.2f}%"
        )

    # La probabilidad analítica de ser campeón corresponde al producto de las probabilidades de superar las cuatro rondas.
    print("\n")
    print(
        "PROBABILIDAD ANALÍTICA DE GANAR EL MUNDIAL"
    )

    print(
        f"Probabilidad: "
        f"{probabilidad_analitica_campeon:.8f}"
    )

    print(
        f"Probabilidad porcentual: "
        f"{probabilidad_analitica_campeon * 100:.6f}%"
    )

    # Ejecuta Monte Carlo para contrastar la probabilidad analítica con una estimación obtenida por simulación.
    print("\n")
    print(
        f"EJECUTANDO MONTE CARLO "
        f"({N_SIMULACIONES:,} simulaciones)"
    )

    (
        veces_campeon,
        probabilidad_mc,
        eliminaciones
    ) = ejecutar_monte_carlo(
        elo_dict,
        N_SIMULACIONES
    )

    print("\n")
    print(
        "RESULTADO MONTE CARLO"
    )

    print(
        f"Veces que Cabo Verde ganó "
        f"el Mundial: "
        f"{veces_campeon:,}"
    )

    print(
        f"Probabilidad estimada: "
        f"{probabilidad_mc:.8f}"
    )

    print(
        f"Probabilidad porcentual: "
        f"{probabilidad_mc * 100:.6f}%"
    )

    # Muestra en qué rival terminó la trayectoria de Cabo Verde dentro de cada simulación.
    print("\n")
    print(
        "ELIMINACIONES POR RIVAL"
    )

    for rival in RIVALES:

        cantidad = eliminaciones[
            rival
        ]

        porcentaje = (
            cantidad
            /
            N_SIMULACIONES
            *
            100
        )

        print(
            f"{rival:<15}: "
            f"{cantidad:>7,} "
            f"({porcentaje:.2f}%)"
        )

    # Guarda las probabilidades individuales de cada partido para utilizarlas posteriormente.
    df_partidos = pd.DataFrame(
        resultados_analiticos
    )

    df_partidos[
        "P Victoria (%)"
    ] = (
        df_partidos[
            "P Victoria"
        ] * 100
    )

    df_partidos[
        "P Empate (%)"
    ] = (
        df_partidos[
            "P Empate"
        ] * 100
    )

    df_partidos[
        "P Derrota (%)"
    ] = (
        df_partidos[
            "P Derrota"
        ] * 100
    )

    df_partidos[
        "P Avance (%)"
    ] = (
        df_partidos[
            "P Avance"
        ] * 100
    )

    df_partidos.to_csv(
        "Data/probabilidades_fase_final.csv",
        index=False
    )

    print("\nArchivo generado:")
    print(
        "Data/probabilidades_fase_final.csv"
    )

    # Guarda un resumen con las dos estimaciones de la probabilidad final de ganar el Mundial.
    resumen = pd.DataFrame({
        "metodo": [
            "Analítico",
            "Monte Carlo"
        ],
        "probabilidad": [
            probabilidad_analitica_campeon,
            probabilidad_mc
        ],
        "porcentaje": [
            probabilidad_analitica_campeon * 100,
            probabilidad_mc * 100
        ]
    })

    resumen.to_csv(
        "Data/probabilidad_campeon_cabo_verde.csv",
        index=False
    )

    print("\nArchivo generado:")
    print(
        "Data/probabilidad_campeon_cabo_verde.csv"
    )

    print("\n")
    print(
        "SIMULACIÓN FINALIZADA"
    )