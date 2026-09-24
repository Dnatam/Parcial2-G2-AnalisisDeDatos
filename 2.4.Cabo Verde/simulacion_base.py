import random
import numpy as np
from scipy.stats import skellam


# PARÁMETROS DEL MODELO

# Parámetros estimados mediante máxima verosimilitud
# utilizando partidos internacionales históricos.
ALPHA = 0.04543275
BETA = 0.00168037
GAMMA = 0.28665411


# PROBABILIDADES ELO-POISSON-SKELLAM

def obtener_lambdas(
    elo_a,
    elo_b,
    neutral=True
):
    """
    Calcula los goles esperados (lambda) de ambos equipos
    utilizando el modelo Elo-Poisson calibrado.
    """

    diferencia = elo_a - elo_b

    # En sede neutral no existe ventaja de localía.
    localia = 0 if neutral else 1

    lambda_a = np.exp(
        ALPHA
        + BETA * diferencia
        + GAMMA * localia
    )

    lambda_b = np.exp(
        ALPHA
        - BETA * diferencia
    )

    return lambda_a, lambda_b


def obtener_probabilidades_partido(
    elo_a,
    elo_b,
    neutral=True
):
    """
    Calcula las probabilidades de victoria, empate y derrota
    mediante la distribución de Skellam.
    """

    lambda_a, lambda_b = obtener_lambdas(
        elo_a,
        elo_b,
        neutral
    )

    # Diferencia de goles:
    # D = Goles A - Goles B

    # Empate: D = 0
    p_empate = skellam.pmf(
        0,
        lambda_a,
        lambda_b
    )

    # Victoria B: D < 0
    p_gana_b = skellam.cdf(
        -1,
        lambda_a,
        lambda_b
    )

    # Victoria A: D > 0
    p_gana_a = 1 - skellam.cdf(
        0,
        lambda_a,
        lambda_b
    )

    return (
        p_gana_a,
        p_empate,
        p_gana_b
    )


# SIMULACIÓN DE MARCADOR

def simular_marcador(
    elo_a,
    elo_b,
    neutral=True
):
    """
    Genera un marcador utilizando dos distribuciones Poisson
    independientes con las lambdas calculadas a partir del
    modelo Elo-Poisson.
    """

    lambda_a, lambda_b = obtener_lambdas(
        elo_a,
        elo_b,
        neutral
    )

    # Generación de goles.
    goles_a = np.random.poisson(lambda_a)
    goles_b = np.random.poisson(lambda_b)

    return (
        int(goles_a),
        int(goles_b),
        lambda_a,
        lambda_b
    )

# SIMULACIÓN COMPLETA DE PARTIDO

def simular_partido(
    equipo_a,
    equipo_b,
    elo_dict,
    neutral=True
):
    """
    Simula un partido completo.

    Devuelve:
        puntos_a
        puntos_b
        goles_a
        goles_b
        resultado
    """

    elo_a = elo_dict[equipo_a]
    elo_b = elo_dict[equipo_b]

    goles_a, goles_b, lambda_a, lambda_b = simular_marcador(
        elo_a,
        elo_b,
        neutral
    )

    # Determinación del resultado.
    if goles_a > goles_b:

        puntos_a = 3
        puntos_b = 0

        resultado = (
            f"Victoria {equipo_a} "
            f"{goles_a}-{goles_b}"
        )

    elif goles_a < goles_b:

        puntos_a = 0
        puntos_b = 3

        resultado = (
            f"Victoria {equipo_b} "
            f"{goles_b}-{goles_a}"
        )

    else:

        puntos_a = 1
        puntos_b = 1

        resultado = (
            f"Empate "
            f"{goles_a}-{goles_b}"
        )

    return (
        puntos_a,
        puntos_b,
        goles_a,
        goles_b,
        resultado
    )


# PROGRAMA DE PRUEBA

if __name__ == "__main__":

    print("=" * 70)
    print("PRUEBA DEL MODELO ELO-POISSON-SKELLAM")
    print("=" * 70)

    elo_dict = {
        "Cabo Verde": 1578,
        "Uruguay": 1892,
        "España": 2157,
        "Arabia Saudita": 1576
    }

    rivales = [
        "Uruguay",
        "España",
        "Arabia Saudita"
    ]

    # Semilla para reproducibilidad.
    random.seed(42)
    np.random.seed(42)

    for rival in rivales:

        print(f"\n{'-' * 60}")
        print(f"Cabo Verde vs {rival}")

        elo_cv = elo_dict["Cabo Verde"]
        elo_rival = elo_dict[rival]

        lambda_cv, lambda_rival = obtener_lambdas(
            elo_cv,
            elo_rival,
            neutral=True
        )

        print(f"Elo Cabo Verde: {elo_cv}")
        print(f"Elo {rival}: {elo_rival}")

        print(
            f"Lambda Cabo Verde: "
            f"{lambda_cv:.4f}"
        )

        print(
            f"Lambda {rival}: "
            f"{lambda_rival:.4f}"
        )

        p_cv, p_empate, p_rival = obtener_probabilidades_partido(
            elo_cv,
            elo_rival,
            neutral=True
        )

        print(
            f"Prob. victoria Cabo Verde: "
            f"{p_cv * 100:.2f}%"
        )

        print(
            f"Prob. empate: "
            f"{p_empate * 100:.2f}%"
        )

        print(
            f"Prob. victoria {rival}: "
            f"{p_rival * 100:.2f}%"
        )

        puntos_cv, puntos_rival, goles_cv, goles_rival, resultado = (
            simular_partido(
                "Cabo Verde",
                rival,
                elo_dict,
                neutral=True
            )
        )

        print(
            f"\nMarcador simulado: "
            f"Cabo Verde {goles_cv}-{goles_rival} {rival}"
        )

        print(f"Resultado: {resultado}")

        print(
            f"Puntos: "
            f"Cabo Verde={puntos_cv}, "
            f"{rival}={puntos_rival}"
        )