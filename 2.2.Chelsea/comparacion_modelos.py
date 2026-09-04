import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from scipy.stats import poisson, nbinom

from poisson import ajustar_poisson
from binomial_negativa import ajustar_binomial_negativa

print("DÍA 5 - CHELSEA: COMPARACIÓN DE MODELOS")

# Carga de los goles en contra de los campeones
df = pd.read_csv("Data/chelsea_resumen.csv")
gc_campeon = df["gc_campeon"]

# Ajuste de ambos modelos reutilizando sus funciones
resultado_poisson = ajustar_poisson(gc_campeon)
resultado_nb = ajustar_binomial_negativa(gc_campeon)

print("\n--- POISSON ---")
print(f"Lambda: {resultado_poisson['lambda']:.4f}")
print(f"Log-verosimilitud: {resultado_poisson['loglik']:.4f}")
print(f"AIC: {resultado_poisson['aic']:.4f}")
print(f"P(X <= 14): {resultado_poisson['p_record']:.8f}")
print(f"P(X <= 14): {resultado_poisson['p_record'] * 100:.6f}%")

print("\n--- BINOMIAL NEGATIVA ---")
print(f"Mu: {resultado_nb['mu']:.4f}")
print(f"r: {resultado_nb['r']:.4f}")
print(f"p: {resultado_nb['p']:.4f}")
print(f"Log-verosimilitud: {resultado_nb['loglik']:.4f}")
print(f"AIC: {resultado_nb['aic']:.4f}")
print(f"P(X <= 14): {resultado_nb['p_record']:.8f}")
print(f"P(X <= 14): {resultado_nb['p_record'] * 100:.6f}%")

# Un AIC menor indica mejor equilibrio entre ajuste y complejidad
print("\n--- COMPARACIÓN ---")

if resultado_nb["aic"] < resultado_poisson["aic"]:
    diferencia_aic = resultado_poisson["aic"] - resultado_nb["aic"]

    print("La Binomial Negativa presenta un AIC menor.")
    print(f"Diferencia de AIC: {diferencia_aic:.4f}")
    print("La diferencia es pequeña, por lo que no existe una ventaja contundente según AIC.")
else:
    diferencia_aic = resultado_nb["aic"] - resultado_poisson["aic"]

    print("Poisson presenta un AIC menor.")
    print(f"Diferencia de AIC: {diferencia_aic:.4f}")
    print("La diferencia es pequeña, por lo que no existe una ventaja contundente según AIC.")

# Comparación visual de las frecuencias observadas con ambos modelos
x = np.arange(14, gc_campeon.max() + 1)

frecuencia_observada = (
    gc_campeon.value_counts()
    .reindex(x, fill_value=0)
    .sort_index()
)

# Las probabilidades se multiplican por 31 temporadas para compararlas con las frecuencias observadas
esperado_poisson = poisson.pmf(
    x,
    mu=resultado_poisson["lambda"]
) * len(gc_campeon)

esperado_nb = nbinom.pmf(
    x,
    n=resultado_nb["r"],
    p=resultado_nb["p"]
) * len(gc_campeon)

plt.figure(figsize=(10, 6))

plt.bar(
    x,
    frecuencia_observada,
    alpha=0.5,
    label="Datos observados"
)

plt.plot(
    x,
    esperado_poisson,
    marker="o",
    label="Poisson"
)

plt.plot(
    x,
    esperado_nb,
    marker="s",
    label="Binomial Negativa"
)

# Umbral necesario para superar el récord de Chelsea
plt.axvline(
    14,
    linestyle="--",
    alpha=0.7,
    label="Umbral para romper el récord (≤14)"
)

plt.xlabel("Goles en contra del campeón")
plt.ylabel("Número de temporadas")
plt.title("Ajuste Poisson vs. Binomial Negativa")
plt.legend()
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()

plt.savefig(
    "Graficas/ajuste_poisson_binomial_negativa.png",
    dpi=300
)

plt.show()