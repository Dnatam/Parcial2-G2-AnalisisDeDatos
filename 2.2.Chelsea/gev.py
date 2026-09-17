from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import genextreme


# CHELSEA: GEV Y BOOTSTRAP
BASE_DIR = Path(__file__).resolve().parent
RUTA_DATOS = BASE_DIR / "Data" / "chelsea_resumen.csv"
RUTA_GRAFICAS = BASE_DIR / "Graficas"

RUTA_GRAFICAS.mkdir(exist_ok=True)


# CARGAR DATOS
df = pd.read_csv(RUTA_DATOS)

print("CHELSEA: GEV Y BOOTSTRAP")

print(f"\nTemporadas encontradas: {len(df)}")

print("\nColumnas:")
print(df.columns.tolist())


# EXTRAER GC DE LA MEJOR DEFENSA
gc_mejor_defensa = pd.to_numeric(
    df["gc_mejor_defensa"],
    errors="coerce"
).dropna().to_numpy()

print("\n--- DATOS UTILIZADOS ---")
print(f"Observaciones: {len(gc_mejor_defensa)}")
print(f"Mínimo: {gc_mejor_defensa.min()}")
print(f"Máximo: {gc_mejor_defensa.max()}")
print(f"Media: {gc_mejor_defensa.mean():.4f}")


# TRANSFORMACIÓN DE MÍNIMOS A MÁXIMOS
y = -gc_mejor_defensa


# AJUSTE GEV
# SciPy devuelve c; la interpretación teórica de forma es xi = -c
c, loc, scale = genextreme.fit(y)
xi = -c

print("\n--- AJUSTE GEV ---")
print(f"c (SciPy): {c:.6f}")
print(f"xi (forma teórica = -c): {xi:.6f}")
print(f"loc (localización): {loc:.6f}")
print(f"scale (escala): {scale:.6f}")


# PROBABILIDAD DE ROMPER EL RÉCORD
# Se evalúa pasando el parámetro c a SciPy
p_record = genextreme.sf(
    -14,
    c,
    loc=loc,
    scale=scale
)

R = 1 / p_record

print("\n--- PROBABILIDAD Y PERÍODO DE RETORNO ---")
print(f"P(X <= 14): {p_record:.8f}")
print(f"P(X <= 14): {p_record * 100:.6f}%")
print(f"Período de retorno R: {R:.6f} temporadas")


# GRÁFICA DEL AJUSTE
x = np.linspace(y.min(), y.max(), 200)

pdf = genextreme.pdf(
    x,
    c,
    loc=loc,
    scale=scale
)

plt.figure(figsize=(10, 6))

plt.hist(
    y,
    bins=10,
    density=True,
    alpha=0.7,
    label="Datos transformados"
)

plt.plot(
    x,
    pdf,
    linewidth=2,
    label="GEV"
)

plt.xlabel("GC transformado (-GC mejor defensa)")
plt.ylabel("Densidad")
plt.title("Ajuste GEV a los mínimos de GC mejor defensa")
plt.legend()
plt.grid(axis="y", alpha=0.3)
plt.tight_layout()

plt.savefig(
    RUTA_GRAFICAS / "ajuste_gev.png",
    dpi=300
)

plt.show()


# BOOTSTRAP
np.random.seed(42)

n_bootstrap = 2000

resultados_bootstrap = []

fallos = 0

for i in range(n_bootstrap):

    # Remuestreo con reemplazo
    muestra = np.random.choice(
        gc_mejor_defensa,
        size=len(gc_mejor_defensa),
        replace=True
    )

    # Transformación de mínimos a máximos
    y_boot = -muestra

    try:

        # Ajustar GEV
        c_boot, loc_boot, scale_boot = genextreme.fit(y_boot)
        xi_boot = -c_boot

        # Calcular probabilidad de romper el récord pasando c_boot
        p_boot = genextreme.sf(
            -14,
            c_boot,
            loc=loc_boot,
            scale=scale_boot
        )

        # Validar que el resultado sea utilizable
        if not np.isfinite(p_boot) or p_boot <= 0 or p_boot > 1:
            fallos += 1
            continue

        # Período de retorno
        R_boot = 1 / p_boot

        resultados_bootstrap.append({
            "c": c_boot,
            "xi": xi_boot,
            "loc": loc_boot,
            "scale": scale_boot,
            "p": p_boot,
            "R": R_boot
        })

    except Exception:
        fallos += 1


bootstrap_df = pd.DataFrame(resultados_bootstrap)

porcentaje_fallos = (fallos / n_bootstrap) * 100

print("\n--- BOOTSTRAP ---")
print(f"Simulaciones solicitadas: {n_bootstrap}")
print(f"Ajustes válidos: {len(bootstrap_df)}")
print(f"Fallos: {fallos}")
print(f"Porcentaje de fallos: {porcentaje_fallos:.2f}%")


# RESUMEN DE INCERTIDUMBRE
if len(bootstrap_df) > 0:

    R_mediana = bootstrap_df["R"].median()
    R_p5 = bootstrap_df["R"].quantile(0.05)
    R_p95 = bootstrap_df["R"].quantile(0.95)

    xi_mediana = bootstrap_df["xi"].median()
    xi_p5 = bootstrap_df["xi"].quantile(0.05)
    xi_p95 = bootstrap_df["xi"].quantile(0.95)

    print("\n--- INTERVALO DE INCERTIDUMBRE 90% ---")

    print("\nPeríodo de retorno R:")
    print(f"Mediana: {R_mediana:.6f}")
    print(f"P5: {R_p5:.6f}")
    print(f"P95: {R_p95:.6f}")

    print("\nParámetro xi:")
    print(f"Mediana: {xi_mediana:.6f}")
    print(f"P5: {xi_p5:.6f}")
    print(f"P95: {xi_p95:.6f}")

    # GUARDAR RESULTADOS
    bootstrap_df.to_csv(
        BASE_DIR / "Data" / "chelsea_bootstrap_gev.csv",
        index=False
    )

    resumen_gev = pd.DataFrame({
        "parametro": ["R", "xi"],
        "mediana": [R_mediana, xi_mediana],
        "P5": [R_p5, xi_p5],
        "P95": [R_p95, xi_p95]
    })

    resumen_gev.to_csv(
        BASE_DIR / "Data" / "chelsea_resumen_gev.csv",
        index=False
    )

    print("\nResultados guardados en:")
    print("Data/chelsea_bootstrap_gev.csv")
    print("Data/chelsea_resumen_gev.csv")

    # GRÁFICA DEL BOOTSTRAP DE R (Recortada al percentil 95 para visualización)
    plt.figure(figsize=(10, 6))

    limite_R = bootstrap_df["R"].quantile(0.95)

    plt.hist(
        bootstrap_df.loc[
            bootstrap_df["R"] <= limite_R,
            "R"
        ],
        bins=40,
        alpha=0.7
    )

    plt.axvline(
        R_mediana,
        linestyle="--",
        linewidth=2,
        label="Mediana"
    )

    plt.xlabel("Período de retorno R")
    plt.ylabel("Frecuencia")
    plt.title("Distribución bootstrap del período de retorno (hasta P95)")
    plt.legend()
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        RUTA_GRAFICAS / "bootstrap_R.png",
        dpi=300
    )

    plt.show()

    # GRÁFICA DEL BOOTSTRAP DE XI
    plt.figure(figsize=(10, 6))

    # Se limita únicamente la visualización para evitar que valores bootstrap extremos distorsionen la escala
    limite_inferior_xi = bootstrap_df["xi"].quantile(0.01)
    limite_superior_xi = bootstrap_df["xi"].quantile(0.99)

    xi_visualizacion = bootstrap_df[
        (bootstrap_df["xi"] >= limite_inferior_xi) &
        (bootstrap_df["xi"] <= limite_superior_xi)
    ]["xi"]

    plt.hist(
        xi_visualizacion,
        bins=40,
        alpha=0.7
    )

    plt.axvline(
        xi_mediana,
        linestyle="--",
        linewidth=2,
        label="Mediana"
    )

    plt.xlabel("Parámetro de forma xi")
    plt.ylabel("Frecuencia")
    plt.title("Distribución bootstrap del parámetro xi (P1-P99)")
    plt.legend()
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()

    plt.savefig(
        RUTA_GRAFICAS / "bootstrap_xi.png",
        dpi=300
    )

    plt.show()

else:

    print("\nNo se obtuvieron ajustes bootstrap válidos.")