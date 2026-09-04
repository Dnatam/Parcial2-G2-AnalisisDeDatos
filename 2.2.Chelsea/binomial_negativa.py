import pandas as pd
import numpy as np

from scipy.stats import nbinom
from scipy.optimize import minimize

# Ajusta una Binomial Negativa mediante máxima verosimilitud
def ajustar_binomial_negativa(gc_campeon):
    media = gc_campeon.mean()
    varianza = gc_campeon.var()

    if varianza <= media:
        return None

    # Valores iniciales obtenidos mediante método de momentos
    mu_inicial = media
    r_inicial = (media ** 2) / (varianza - media)

    # Log-verosimilitud negativa que será minimizada
    def loglik_negativa(parametros):
        log_mu, log_r = parametros

        mu = np.exp(log_mu)
        r = np.exp(log_r)

        p = r / (r + mu)

        return -nbinom.logpmf(
            gc_campeon,
            n=r,
            p=p
        ).sum()

    resultado_opt = minimize(
        loglik_negativa,
        [np.log(mu_inicial), np.log(r_inicial)],
        method="L-BFGS-B"
    )

    mu = np.exp(resultado_opt.x[0])
    r = np.exp(resultado_opt.x[1])
    p = r / (r + mu)

    # Romper el récord de Chelsea (15 GC) requiere recibir 14 goles o menos
    p_record = nbinom.cdf(14, n=r, p=p)

    # Métricas utilizadas posteriormente para comparar modelos
    loglik = nbinom.logpmf(gc_campeon, n=r, p=p).sum()
    aic = 4 - 2 * loglik

    return {
        "media": media,
        "varianza": varianza,
        "mu": mu,
        "r": r,
        "p": p,
        "p_record": p_record,
        "loglik": loglik,
        "aic": aic
    }

if __name__ == "__main__":
    print("DÍA 5 - CHELSEA: AJUSTE BINOMIAL NEGATIVA")

    df = pd.read_csv("Data/chelsea_resumen.csv")
    gc_campeon = df["gc_campeon"]

    resultado = ajustar_binomial_negativa(gc_campeon)

    print(f"\nNúmero de temporadas analizadas: {len(gc_campeon)}")

    if resultado is None:
        print("No hay sobredispersión.")
        print("No se puede ajustar la Binomial Negativa con este planteamiento.")
    else:
        print(f"Media de GC del campeón: {resultado['media']:.4f}")
        print(f"Varianza de GC del campeón: {resultado['varianza']:.4f}")

        print("\n--- PARÁMETROS BINOMIAL NEGATIVA ---")
        print(f"Mu: {resultado['mu']:.4f}")
        print(f"r: {resultado['r']:.4f}")
        print(f"p: {resultado['p']:.4f}")

        print("\n--- PROBABILIDAD DE ROMPER EL RÉCORD ---")
        print(f"P(X <= 14) según Binomial Negativa: {resultado['p_record']:.8f}")
        print(f"P(X <= 14) según Binomial Negativa: {resultado['p_record'] * 100:.6f}%")