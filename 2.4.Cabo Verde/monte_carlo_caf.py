import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from simulador_caf import (
    cargar_elo,
    simular_grupo,
    obtener_ganador
)


# ============================================================
# CONFIGURACIÓN
# ============================================================

N_SIMULACIONES = 100000


# ============================================================
# MONTE CARLO
# ============================================================

def ejecutar_monte_carlo():

    elo_dict = cargar_elo()

    conteo_ganador = {}

    for _ in range(N_SIMULACIONES):

        tabla, _ = simular_grupo(
            elo_dict
        )

        ganador = obtener_ganador(
            tabla
        )

        conteo_ganador[ganador] = (
            conteo_ganador.get(ganador, 0) + 1
        )

    return conteo_ganador


# ============================================================
# RESULTADOS
# ============================================================

if __name__ == "__main__":

    print("=" * 70)
    print("MONTE CARLO - CLASIFICACIÓN DIRECTA DE CABO VERDE")
    print("=" * 70)

    random.seed(42)
    np.random.seed(42)

    conteo = ejecutar_monte_carlo()

    resultados = []

    for equipo, cantidad in conteo.items():

        probabilidad = (
            cantidad / N_SIMULACIONES
        )

        resultados.append({
            "Equipo": equipo,
            "Clasificaciones": cantidad,
            "Probabilidad": probabilidad
        })

    df_resultados = pd.DataFrame(
        resultados
    )

    df_resultados = df_resultados.sort_values(
        by="Probabilidad",
        ascending=False
    )

    print("\nRESULTADOS")

    for _, fila in df_resultados.iterrows():

        print(
            f"{fila['Equipo']}: "
            f"{fila['Probabilidad'] * 100:.2f}%"
        )

    prob_cv = (
        df_resultados.loc[
            df_resultados["Equipo"] == "Cabo Verde",
            "Probabilidad"
        ]
    )

    if len(prob_cv) > 0:

        print(
            "\nProbabilidad de clasificación directa "
            f"de Cabo Verde: "
            f"{prob_cv.iloc[0] * 100:.2f}%"
        )

    # --------------------------------------------------------
    # GRÁFICA
    # --------------------------------------------------------

    plt.figure(
        figsize=(10, 6)
    )

    plt.bar(
        df_resultados["Equipo"],
        df_resultados["Probabilidad"] * 100
    )

    plt.xlabel(
        "Selección"
    )

    plt.ylabel(
        "Probabilidad de ganar el grupo (%)"
    )

    plt.title(
        "Probabilidad de clasificación directa - CAF"
    )

    plt.xticks(
        rotation=45,
        ha="right"
    )

    plt.tight_layout()

    plt.savefig(
        "Graficas/probabilidad_clasificacion_caf.png",
        dpi=300
    )

    plt.close()

    print(
        "\nGráfica guardada en:"
    )

    print(
        "Graficas/probabilidad_clasificacion_caf.png"
    )