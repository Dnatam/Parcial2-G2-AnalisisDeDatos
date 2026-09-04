import pandas as pd
import matplotlib.pyplot as plt

from poisson import ajustar_poisson
from binomial_negativa import ajustar_binomial_negativa

# Calcula la probabilidad de observar al menos una ruptura del récord dentro de N temporadas
def probabilidad_en_horizonte(p, n_temporadas):
    return 1 - (1 - p) ** n_temporadas

if __name__ == "__main__":
    print("DÍA 6 - CHELSEA: PROBABILIDAD EN DISTINTOS HORIZONTES")

    df = pd.read_csv("Data/chelsea_resumen.csv")
    gc_campeon = df["gc_campeon"]

    resultado_poisson = ajustar_poisson(gc_campeon)
    resultado_nb = ajustar_binomial_negativa(gc_campeon)

    p_poisson = resultado_poisson["p_record"]
    p_nb = resultado_nb["p_record"]

    horizontes = [20, 50, 100, 200, 1000]

    print("\n--- PROBABILIDAD POR TEMPORADA ---")
    print(f"Poisson: {p_poisson:.8f} ({p_poisson * 100:.6f}%)")
    print(f"Binomial Negativa: {p_nb:.8f} ({p_nb * 100:.6f}%)")

    resultados = []

    print("\n--- PROBABILIDAD DE ROMPER EL RÉCORD AL MENOS UNA VEZ ---")

    for n in horizontes:
        prob_poisson = probabilidad_en_horizonte(
            p_poisson,
            n
        )

        prob_nb = probabilidad_en_horizonte(
            p_nb,
            n
        )

        resultados.append({
            "Temporadas": n,
            "Poisson": prob_poisson,
            "Binomial Negativa": prob_nb
        })

        print(
            f"{n:>4} temporadas | "
            f"Poisson: {prob_poisson * 100:>7.2f}% | "
            f"Binomial Negativa: {prob_nb * 100:>7.2f}%"
        )

    df_resultados = pd.DataFrame(resultados)

    print("\n--- TABLA DE RESULTADOS ---")
    print(df_resultados.to_string(index=False))

    # Gráfica de probabilidad acumulada según el horizonte
    plt.figure(figsize=(9, 6))

    plt.plot(
        df_resultados["Temporadas"],
        df_resultados["Poisson"] * 100,
        marker="o",
        label="Poisson"
    )

    plt.plot(
        df_resultados["Temporadas"],
        df_resultados["Binomial Negativa"] * 100,
        marker="s",
        label="Binomial Negativa"
    )

    plt.title(
        "Probabilidad de Romper el Récord de Chelsea"
    )
    plt.xlabel("Número de temporadas")
    plt.ylabel(
        "Probabilidad de al menos una ruptura (%)"
    )

    plt.grid(
        linestyle="--",
        alpha=0.5
    )

    plt.legend()
    plt.tight_layout()

    plt.savefig(
        "Graficas/probabilidad_horizontes.png",
        dpi=300
    )

    plt.close()

    print(
        "\nGráfica guardada en "
        "'Graficas/probabilidad_horizontes.png'"
    )