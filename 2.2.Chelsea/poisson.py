import pandas as pd
from scipy.stats import poisson

# Ajusta una distribución Poisson a los goles en contra de los campeones
def ajustar_poisson(gc_campeon):
    media = gc_campeon.mean()
    varianza = gc_campeon.var()

    # Lambda se estima mediante la media muestral
    lambda_poisson = media

    # Romper el récord de Chelsea (15 GC) requiere recibir 14 goles o menos
    p_poisson = poisson.cdf(14, mu=lambda_poisson)

    # Métricas utilizadas posteriormente para comparar modelos
    loglik = poisson.logpmf(gc_campeon, mu=lambda_poisson).sum()
    aic = 2 - 2 * loglik

    return {
        "media": media,
        "varianza": varianza,
        "lambda": lambda_poisson,
        "p_record": p_poisson,
        "loglik": loglik,
        "aic": aic
    }

if __name__ == "__main__":
    print("DÍA 5 - CHELSEA: AJUSTE POISSON")

    # Carga de los goles en contra de los campeones por temporada
    df = pd.read_csv("Data/chelsea_resumen.csv")
    gc_campeon = df["gc_campeon"]

    resultado = ajustar_poisson(gc_campeon)

    print(f"\nNúmero de temporadas analizadas: {len(gc_campeon)}")
    print(f"Media de GC del campeón: {resultado['media']:.4f}")
    print(f"Varianza de GC del campeón: {resultado['varianza']:.4f}")
    print(f"\nParámetro estimado de Poisson (lambda): {resultado['lambda']:.4f}")
    print(f"P(X <= 14) según Poisson: {resultado['p_record']:.8f}")
    print(f"P(X <= 14) según Poisson: {resultado['p_record'] * 100:.6f}%")

    # Esta revisión permite identificar si existe sobredispersión en los datos
    print("\n--- REVISIÓN DE DISPERSIÓN ---")

    if resultado["varianza"] > resultado["media"]:
        print("Hay sobredispersión: Varianza > Media.")
        print("Conviene evaluar una Binomial Negativa.")
    elif resultado["varianza"] < resultado["media"]:
        print("Hay subdispersión: Varianza < Media.")
    else:
        print("Media y varianza son aproximadamente iguales.")
        print("Poisson podría ser un modelo adecuado.")