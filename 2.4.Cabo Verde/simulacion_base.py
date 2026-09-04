import math
import random

# Calcula las probabilidades de victoria, empate y derrota a partir del Elo
def obtener_probabilidades_partido(elo_a, elo_b, k_empate=0.28):
    diff = elo_a - elo_b
    e_a = 1 / (1 + 10 ** (-diff / 400))

    p_empate = math.exp(-((diff / 400) ** 2)) * k_empate
    p_gana_a = max(0.001, e_a - (p_empate / 2))
    p_gana_b = max(0.001, (1 - e_a) - (p_empate / 2))

    total = p_gana_a + p_empate + p_gana_b

    return (
        p_gana_a / total,
        p_empate / total,
        p_gana_b / total
    )

# Simula un partido y devuelve los puntos obtenidos por cada equipo
def simular_partido(equipo_a, equipo_b, elo_dict, k_empate=0.28):
    elo_a = elo_dict[equipo_a]
    elo_b = elo_dict[equipo_b]

    p_a, p_empate, p_b = obtener_probabilidades_partido(
        elo_a,
        elo_b,
        k_empate
    )

    aleatorio = random.random()

    if aleatorio < p_a:
        return 3, 0, f"Victoria {equipo_a}"

    elif aleatorio < p_a + p_empate:
        return 1, 1, "Empate"

    else:
        return 0, 3, f"Victoria {equipo_b}"