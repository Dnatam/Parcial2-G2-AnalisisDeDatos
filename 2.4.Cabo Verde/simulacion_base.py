import random
import numpy as np
from scipy.stats import skellam

# Parámetros estimados mediante máxima verosimilitud utilizando el histórico de partidos internacionales.
ALPHA = 0.04543275
BETA = 0.00168037
GAMMA = 0.28665411

# Calcula las probabilidades de victoria, empate y derrota mediante un modelo Elo-Poisson y la distribución de Skellam.
def obtener_probabilidades_partido(
    elo_a,
    elo_b,
    neutral=True
):
    diferencia = elo_a - elo_b

    # En sede neutral no se aplica ventaja de localía.
    # En partidos no neutrales, el efecto gamma incrementa la intensidad esperada de goles del equipo A.
    localia = 0 if neutral else 1

    # Calcula los goles esperados de cada selección.
    lambda_a = np.exp(
        ALPHA
        + BETA * diferencia
        + GAMMA * localia
    )

    lambda_b = np.exp(
        ALPHA
        - BETA * diferencia
    )

    # Si X_A y X_B son variables Poisson independientes, la diferencia D = X_A - X_B sigue una distribución
    # de Skellam con parámetros lambda_a y lambda_b.
    # D > 0: victoria del equipo A
    # D = 0: empate
    # D < 0: victoria del equipo B
    p_empate = skellam.pmf(
        0,
        lambda_a,
        lambda_b
    )

    p_gana_b = skellam.cdf(
        -1,
        lambda_a,
        lambda_b
    )

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


# Simula el resultado de un partido utilizando las probabilidades obtenidas con el modelo Elo-Poisson-Skellam.
def simular_partido(
    equipo_a,
    equipo_b,
    elo_dict,
    neutral=True
):
    elo_a = elo_dict[equipo_a]
    elo_b = elo_dict[equipo_b]

    p_a, p_empate, p_b = obtener_probabilidades_partido(
        elo_a,
        elo_b,
        neutral
    )

    aleatorio = random.random()

    # Asigna el resultado mediante una variable uniforme U(0,1) y los intervalos definidos por las probabilidades calculadas.
    if aleatorio < p_a:
        return (
            3,
            0,
            f"Victoria {equipo_a}"
        )

    elif aleatorio < p_a + p_empate:
        return (
            1,
            1,
            "Empate"
        )

    else:
        return (
            0,
            3,
            f"Victoria {equipo_b}"
        )

if __name__ == "__main__":
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

    for rival in rivales:
        p_cv, p_empate, p_rival = obtener_probabilidades_partido(
            elo_dict["Cabo Verde"],
            elo_dict[rival],
            neutral=True
        )

        print(f"\nCabo Verde vs {rival}")
        print(f"Victoria Cabo Verde: {p_cv * 100:.2f}%")
        print(f"Empate: {p_empate * 100:.2f}%")
        print(f"Victoria {rival}: {p_rival * 100:.2f}%")
        print(
            f"Total: "
            f"{(p_cv + p_empate + p_rival) * 100:.2f}%"
        )