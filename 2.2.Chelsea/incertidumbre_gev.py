import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "Data"
GRAPH_DIR = BASE_DIR / "Graficas"

GRAPH_DIR.mkdir(exist_ok=True)

archivo = DATA_DIR / "chelsea_bootstrap_gev.csv"

df = pd.read_csv(archivo)

# Eliminar filas con valores faltantes en las variables de interés
df = df.dropna(subset=["xi", "R"])


total = len(df)

print("CHELSEA: INCERTIDUMBRE DEL BOOTSTRAP GEV")

print(f"\nSimulaciones válidas encontradas: {total}")

solicitadas = 2000
fallos = solicitadas - total

print(f"Simulaciones solicitadas: {solicitadas}")
print(f"Ajustes válidos: {total}")
print(f"Fallos: {fallos}")
print(f"Porcentaje válido: {100 * total / solicitadas:.2f}%")
print(f"Porcentaje de fallos: {100 * fallos / solicitadas:.2f}%")


# INCERTIDUMBRE DEL PERÍODO DE RETORNO

R_mediana = df["R"].median()
R_P5 = df["R"].quantile(0.05)
R_P95 = df["R"].quantile(0.95)

print("\n--- PERÍODO DE RETORNO R ---")
print(f"Mediana: {R_mediana:.6f}")
print(f"P5:      {R_P5:.6f}")
print(f"P95:     {R_P95:.6f}")


# INCERTIDUMBRE DEL PARÁMETRO XI

xi_mediana = df["xi"].median()
xi_P5 = df["xi"].quantile(0.05)
xi_P95 = df["xi"].quantile(0.95)

print("\n--- PARÁMETRO DE FORMA XI ---")
print(f"Mediana: {xi_mediana:.6f}")
print(f"P5:      {xi_P5:.6f}")
print(f"P95:     {xi_P95:.6f}")


# TABLA RESUMEN

resumen = pd.DataFrame({
    "parametro": ["R", "xi"],
    "mediana": [R_mediana, xi_mediana],
    "P5": [R_P5, xi_P5],
    "P95": [R_P95, xi_P95]
})

salida = DATA_DIR / "chelsea_resumen_gev.csv"
resumen.to_csv(salida, index=False)

print("\nResumen guardado en:")
print(salida)


# GRÁFICA 1 - DISTRIBUCIÓN DEL PERÍODO DE RETORNO

plt.figure(figsize=(10, 6))

plt.hist(df["R"], bins=50)

plt.axvline(
    R_P5,
    linestyle="--",
    label=f"P5 = {R_P5:.2f}"
)

plt.axvline(
    R_mediana,
    linestyle="-",
    label=f"Mediana = {R_mediana:.2f}"
)

plt.axvline(
    R_P95,
    linestyle="--",
    label=f"P95 = {R_P95:.2f}"
)

plt.xlabel("Período de retorno R (temporadas)")
plt.ylabel("Frecuencia")
plt.title("Incertidumbre bootstrap del período de retorno GEV")
plt.legend()
plt.tight_layout()

grafica_R = GRAPH_DIR / "incertidumbre_bootstrap_R.png"
plt.savefig(grafica_R, dpi=300)
plt.close()

print("\nGráfica guardada en:")
print(grafica_R)


# GRÁFICA 2 - DISTRIBUCIÓN DE XI

plt.figure(figsize=(10, 6))

plt.hist(df["xi"], bins=40)

plt.axvline(
    xi_P5,
    linestyle="--",
    label=f"P5 = {xi_P5:.4f}"
)

plt.axvline(
    xi_mediana,
    linestyle="-",
    label=f"Mediana = {xi_mediana:.4f}"
)

plt.axvline(
    xi_P95,
    linestyle="--",
    label=f"P95 = {xi_P95:.4f}"
)

plt.axvline(
    0,
    linestyle=":",
    label="xi = 0"
)

plt.xlabel("Parámetro de forma xi")
plt.ylabel("Frecuencia")
plt.title("Incertidumbre bootstrap del parámetro de forma GEV")
plt.legend()
plt.tight_layout()

grafica_xi = GRAPH_DIR / "incertidumbre_bootstrap_xi.png"
plt.savefig(grafica_xi, dpi=300)
plt.close()

print("\nGráfica guardada en:")
print(grafica_xi)

print("ANÁLISIS DE INCERTIDUMBRE COMPLETADO")