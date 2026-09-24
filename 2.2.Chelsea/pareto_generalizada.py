from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import genpareto


# CHELSEA: PARETO GENERALIZADA (GPD)

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "Data"
GRAPH_DIR = BASE_DIR / "Graficas"

GRAPH_DIR.mkdir(exist_ok=True)


print("CHELSEA: PARETO GENERALIZADA (GPD)")


archivo = DATA_DIR / "chelsea_resumen.csv"

df = pd.read_csv(archivo)

gc_mejor_defensa = pd.to_numeric(
    df["gc_mejor_defensa"],
    errors="coerce"
).dropna().to_numpy()


print("\n--- DATOS ---")
print(f"Temporadas: {len(gc_mejor_defensa)}")
print(f"Mínimo GC: {gc_mejor_defensa.min()}")
print(f"Máximo GC: {gc_mejor_defensa.max()}")
print(f"Media GC: {gc_mejor_defensa.mean():.4f}")



# 2. TRANSFORMACIÓN

# Una mejor defensa recibe MENOS goles.
# Transformamos mínimos en máximos mediante:
#
# Y = -GC

y = -gc_mejor_defensa


print("\n--- TRANSFORMACIÓN ---")
print("Se utiliza Y = -GC para convertir los mínimos")
print("de goles recibidos en valores extremos superiores.")


# 3. FUNCIÓN PARA AJUSTAR GPD

def ajustar_gpd(y, cuantile):

    # Umbral
    umbral = np.quantile(y, cuantile)

    # Excedencias sobre el umbral
    excedencias = y[y > umbral] - umbral

    if len(excedencias) < 3:
        return {
            "cuantil": cuantile,
            "umbral_y": umbral,
            "umbral_gc": -umbral,
            "n_excedencias": len(excedencias),
            "xi": np.nan,
            "scale": np.nan,
            "excedencias": excedencias
        }

    # Ajuste GPD
    xi, loc, scale = genpareto.fit(
        excedencias,
        floc=0
    )

    return {
        "cuantil": cuantile,
        "umbral_y": umbral,
        "umbral_gc": -umbral,
        "n_excedencias": len(excedencias),
        "xi": xi,
        "scale": scale,
        "excedencias": excedencias
    }


# 4. AJUSTE PRINCIPAL

# Usamos inicialmente el percentil 75.
cuantil_principal = 0.75

resultado_principal = ajustar_gpd(
    y,
    cuantil_principal
)

umbral = resultado_principal["umbral_y"]
excedencias = resultado_principal["excedencias"]
xi_gpd = resultado_principal["xi"]
scale_gpd = resultado_principal["scale"]


print("\n--- MÉTODO POT ---")
print(f"Cuantil utilizado: {cuantil_principal:.2f}")
print(f"Umbral en escala Y: {umbral:.6f}")
print(f"Umbral equivalente en GC: {-umbral:.6f}")
print(f"Número de excedencias: {len(excedencias)}")

print("\nExcedencias:")
print(excedencias)


# 5. RESULTADOS GPD

print("\n--- AJUSTE PARETO GENERALIZADA ---")
print(f"xi GPD:    {xi_gpd:.6f}")
print(f"scale GPD: {scale_gpd:.6f}")


# 6. COMPARACIÓN CON GEV

# Para la convención habitual de teoría de valores extremos:
#
# xi_GEV = -c
#
# Nuestro resultado del inciso 4 fue:
# c = -0.0788702388
#
# Por tanto:
#
# xi_GEV = 0.0788702388

xi_gev = 0.07887023884049774


print("\n--- COMPARACIÓN GEV VS GPD ---")
print(f"xi GEV: {xi_gev:.6f}")
print(f"xi GPD: {xi_gpd:.6f}")
print(f"Diferencia absoluta: {abs(xi_gev - xi_gpd):.6f}")


# 7. SENSIBILIDAD AL UMBRAL

print("\n--- SENSIBILIDAD AL UMBRAL ---")

cuantiles = [0.70, 0.75, 0.80, 0.85]

resultados_sensibilidad = []

for q in cuantiles:

    resultado = ajustar_gpd(y, q)

    resultados_sensibilidad.append({
        "cuantil": resultado["cuantil"],
        "umbral_Y": resultado["umbral_y"],
        "umbral_GC": resultado["umbral_gc"],
        "n_excedencias": resultado["n_excedencias"],
        "xi_GPD": resultado["xi"],
        "scale_GPD": resultado["scale"]
    })

    print(
        f"q={q:.2f} | "
        f"umbral GC={resultado['umbral_gc']:.2f} | "
        f"excedencias={resultado['n_excedencias']} | "
        f"xi={resultado['xi']:.6f}"
    )


sensibilidad_df = pd.DataFrame(
    resultados_sensibilidad
)


# 8. GUARDAR SENSIBILIDAD

archivo_sensibilidad = (
    DATA_DIR / "sensibilidad_gpd_umbral.csv"
)

sensibilidad_df.to_csv(
    archivo_sensibilidad,
    index=False
)

print("\nSensibilidad guardada en:")
print(archivo_sensibilidad)


# 9. GUARDAR COMPARACIÓN GEV VS GPD

comparacion = pd.DataFrame({
    "metodo": [
        "GEV",
        "GPD"
    ],
    "xi": [
        xi_gev,
        xi_gpd
    ]
})

archivo_comparacion = (
    DATA_DIR / "comparacion_gev_gpd.csv"
)

comparacion.to_csv(
    archivo_comparacion,
    index=False
)

print("\nComparación guardada en:")
print(archivo_comparacion)

# 10. GRÁFICA DEL AJUSTE GPD MEDIANTE CDF

# Ordenar las excedencias observadas
excedencias_ordenadas = np.sort(excedencias)

# CDF empírica
n = len(excedencias_ordenadas)

cdf_empirica = np.arange(
    1,
    n + 1
) / n

# Valores para representar la CDF teórica
x = np.linspace(
    0,
    excedencias_ordenadas.max(),
    300
)

# CDF de la Pareto Generalizada ajustada
cdf_gpd = genpareto.cdf(
    x,
    xi_gpd,
    loc=0,
    scale=scale_gpd
)

plt.figure(figsize=(10, 6))

# Datos observados
plt.step(
    excedencias_ordenadas,
    cdf_empirica,
    where="post",
    linewidth=2,
    label="CDF empírica"
)

plt.scatter(
    excedencias_ordenadas,
    cdf_empirica,
    s=50
)

# Modelo GPD
plt.plot(
    x,
    cdf_gpd,
    linewidth=2,
    label="CDF Pareto Generalizada"
)

plt.xlabel("Excedencia sobre el umbral")
plt.ylabel("Probabilidad acumulada")
plt.title(
    "CDF empírica vs. Pareto Generalizada"
)

plt.ylim(0, 1.05)

plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()

grafica_gpd = (
    GRAPH_DIR / "ajuste_pareto_generalizada.png"
)

plt.savefig(
    grafica_gpd,
    dpi=300
)

plt.close()

print("\nGráfica GPD guardada en:")
print(grafica_gpd)

# 11. GRÁFICA DE SENSIBILIDAD DE XI

plt.figure(figsize=(10, 6))

plt.plot(
    sensibilidad_df["cuantil"],
    sensibilidad_df["xi_GPD"],
    marker="o",
    linewidth=2,
    label="xi GPD"
)

plt.axhline(
    xi_gev,
    linestyle="--",
    linewidth=2,
    label=f"xi GEV = {xi_gev:.4f}"
)

plt.xlabel("Cuantil utilizado como umbral")
plt.ylabel("Parámetro de forma xi")
plt.title(
    "Sensibilidad de xi GPD a la selección del umbral"
)

plt.legend()
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()

grafica_sensibilidad = (
    GRAPH_DIR / "sensibilidad_xi_gpd.png"
)

plt.savefig(
    grafica_sensibilidad,
    dpi=300
)

plt.close()

print("\nGráfica de sensibilidad guardada en:")
print(grafica_sensibilidad)


# 12. GRÁFICA COMPARATIVA GEV VS GPD

plt.figure(figsize=(8, 6))

metodos = ["GEV", "GPD"]
valores_xi = [xi_gev, xi_gpd]

plt.bar(
    metodos,
    valores_xi
)

plt.axhline(
    0,
    linestyle="--",
    linewidth=1
)

plt.ylabel("Parámetro de forma xi")
plt.title(
    "Comparación del parámetro xi: GEV vs GPD"
)

plt.tight_layout()

grafica_comparacion = (
    GRAPH_DIR / "comparacion_xi_gev_gpd.png"
)

plt.savefig(
    grafica_comparacion,
    dpi=300
)

plt.close()

print("\nGráfica comparativa guardada en:")
print(grafica_comparacion)


# 13. RESUMEN FINAL

print("RESUMEN DEL PUNTO EXTRA")

print(f"\nNúmero de temporadas: {len(gc_mejor_defensa)}")
print(f"Umbral principal: {(-umbral):.2f} goles recibidos")
print(f"Excedencias utilizadas: {len(excedencias)}")

print(f"\nxi GEV = {xi_gev:.6f}")
print(f"xi GPD = {xi_gpd:.6f}")

print(
    f"\nDiferencia absoluta = "
    f"{abs(xi_gev - xi_gpd):.6f}"
)

print("\nArchivos generados:")
print("Data/sensibilidad_gpd_umbral.csv")
print("Data/comparacion_gev_gpd.csv")
print("Graficas/ajuste_pareto_generalizada.png")
print("Graficas/sensibilidad_xi_gpd.png")
print("Graficas/comparacion_xi_gev_gpd.png")