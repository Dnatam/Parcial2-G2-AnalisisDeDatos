import math
import os
import random
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

print("=" * 75)
print("DÍA 4: EDA COMPLETO Y FUNCIONES BASE DE SIMULACIÓN")
print("=" * 75)

# Carpetas para guardar gráficos
os.makedirs("2.2.Chelsea/Graficas", exist_ok=True)
os.makedirs("2.4.Cabo Verde/Graficas", exist_ok=True)

# 1. CASO CHELSEA: EDA DEL DATASET PROCESADO (31 TEMPORADAS)
ruta_chelsea_csv = "2.2.Chelsea/Data/chelsea_resumen.csv"

if os.path.exists(ruta_chelsea_csv):
    df_chelsea = pd.read_csv(ruta_chelsea_csv)

    print("\n[1/2] CHELSEA: ESTADÍSTICAS DESCRIPTIVAS (GOLES EN CONTRA - GC)")
    print("-" * 65)

    stats_campeon = df_chelsea["gc_campeon"].agg(
        ["mean", "median", "var", "std", "min", "max"]
    )
    stats_defensa = df_chelsea["gc_mejor_defensa"].agg(
        ["mean", "median", "var", "std", "min", "max"]
    )

    df_stats = pd.DataFrame(
        {"GC Campeón": stats_campeon, "GC Mejor Defensa": stats_defensa}
    )
    print(df_stats.round(2).to_string())

    # Chelsea 2004-05 Récord
    chelsea_0405 = df_chelsea[df_chelsea["temporada"] == "2004-2005"].iloc[0]
    print(
        f"\n Destacado Chelsea 2004-05: Campeón = {chelsea_0405['campeon']}, "
        f"GC = {chelsea_0405['gc_campeon']} (Récord Histórico de la Premier League)"
    )

    # GENERACIÓN DE GRÁFICOS CHELSEA
    # Histograma de GC del Campeón
    plt.figure(figsize=(8, 5))
    plt.hist(
        df_chelsea["gc_campeon"],
        bins=10,
        color="#1f77b4",
        edgecolor="black",
        alpha=0.7,
    )
    plt.axvline(
        chelsea_0405["gc_campeon"],
        color="red",
        linestyle="dashed",
        linewidth=2,
        label="Chelsea 04/05 (12 GC)",
    )
    plt.title("Histograma de Goles en Contra del Campeón (31 Temporadas)")
    plt.xlabel("Goles en Contra (GC)")
    plt.ylabel("Frecuencia (Temporadas)")
    plt.legend()
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.savefig("2.2.Chelsea/Graficas/histograma_gc_campeon.png")
    plt.close()

    # Serie Temporal Campeón vs Mejor Defensa
    plt.figure(figsize=(12, 5))
    plt.plot(
        df_chelsea["temporada"],
        df_chelsea["gc_campeon"],
        marker="o",
        label="GC Campeón",
        color="blue",
    )
    plt.plot(
        df_chelsea["temporada"],
        df_chelsea["gc_mejor_defensa"],
        marker="s",
        linestyle="--",
        label="GC Mejor Defensa",
        color="green",
    )
    plt.axhline(
        12,
        color="red",
        linestyle=":",
        label="Récord Mínimo (Chelsea 04/05 = 12 GC)",
    )
    plt.xticks(rotation=90)
    plt.title("Serie Temporal: Goles en Contra (Campeón vs Mejor Defensa)")
    plt.xlabel("Temporada")
    plt.ylabel("Goles en Contra (GC)")
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig("2.2.Chelsea/Graficas/serie_temporal_gc.png")
    plt.close()

    # Boxplot Comparativo
    plt.figure(figsize=(7, 5))
    plt.boxplot(
        [df_chelsea["gc_campeon"], df_chelsea["gc_mejor_defensa"]],
        tick_labels=["GC Campeón", "GC Mejor Defensa"],
        patch_artist=True,
    )
    plt.title("Boxplot Comparativo: GC Campeón vs GC Mejor Defensa")
    plt.ylabel("Goles en Contra (GC)")
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.savefig("2.2.Chelsea/Graficas/boxplot_gc_comparativo.png")
    plt.close()


# 2. CASO CABO VERDE: EDA DE ELO Y FUNCIONES REUTILIZABLES DE SIMULACIÓN
ruta_elo_limpio = "2.4.Cabo Verde/Data/elo_limpio.csv"

if os.path.exists(ruta_elo_limpio):
    df_elo = pd.read_csv(ruta_elo_limpio)

    print("\n[2/2] CABO VERDE: EDA DE RANKINGS ELO")
    print("-" * 65)

    stats_elo = df_elo["elo_rating"].agg(
        ["mean", "median", "var", "std", "min", "max"]
    )
    print("Estadísticas del Ranking Elo (13 Selecciones):")
    print(stats_elo.round(2).to_string())

    # Gráfico Barplot Rankings Elo
    df_elo_sorted = df_elo.sort_values(by="elo_rating", ascending=True)
    plt.figure(figsize=(9, 6))
    colores = [
        "orange" if eq == "Cabo Verde" else "skyblue"
        for eq in df_elo_sorted["equipo"]
    ]
    plt.barh(df_elo_sorted["equipo"], df_elo_sorted["elo_rating"], color=colores)
    plt.title("Ranking Elo de Selecciones Seleccionadas")
    plt.xlabel("Rating Elo")
    plt.grid(axis="x", linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.savefig("2.4.Cabo Verde/Graficas/barplot_elo_selecciones.png")
    plt.close()

    print(
        "\n    Gráfica Elo guardada en '2.4.Cabo Verde/Graficas/barplot_elo_selecciones.png'"
    )


# FUNCIONES BASE REUTILIZABLES PARA SIMULACIÓN 
def obtener_probabilidades_partido(elo_a, elo_b, k_empate=0.28):
    """Retorna las probabilidades normalizadas de (Victoria A, Empate, Victoria B)."""
    diff = elo_a - elo_b
    e_a = 1 / (1 + 10 ** (-diff / 400))
    p_empate = math.exp(-((diff / 400) ** 2)) * k_empate
    p_gana_a = max(0.001, e_a - (p_empate / 2))
    p_gana_b = max(0.001, (1 - e_a) - (p_empate / 2))

    total = p_gana_a + p_empate + p_gana_b
    return (p_gana_a / total, p_empate / total, p_gana_b / total)


def simular_partido(
    equipo_a, equipo_b, elo_dict, semilla=None, k_empate=0.28
):
    """Simula un partido entre dos equipos y asigna 3/1/0 puntos según el resultado probabilístico.

    Retorna: (puntos_a, puntos_b, resultado_str)
    """
    if semilla is not None:
        random.seed(semilla)

    elo_a = elo_dict[equipo_a]
    elo_b = elo_dict[equipo_b]

    p_a, p_emp, p_b = obtener_probabilidades_partido(elo_a, elo_b, k_empate)

    # Generar número aleatorio [0.0, 1.0) para definir el resultado
    r = random.random()

    if r < p_a:
        return 3, 0, f"Victoria {equipo_a}"
    elif r < (p_a + p_emp):
        return 1, 1, "Empate"
    else:
        return 0, 3, f"Victoria {equipo_b}"


# PRUEBA DE FUNCIONES BASE 
print("\n--- PRUEBA DE SIMULACIÓN DE PARTIDO Y ASIGNACIÓN DE PUNTOS ---")
dict_elo = dict(zip(df_elo["equipo"], df_elo["elo_rating"]))

# Simular 5 enfrentamientos de prueba Cabo Verde vs Camerún
print("Simulación de 5 partidos Cabo Verde vs Camerún:")
for i in range(1, 6):
    pts_a, pts_b, res = simular_partido(
        "Cabo Verde", "Camerún", dict_elo, semilla=i * 10
    )
    print(
        f"   Partido {i}: {res} -> Cabo Verde obtiene {pts_a} pts | Camerún obtiene {pts_b} pts"
    )

print("\n" + "=" * 75)