import os
import sys
import random
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Permite importar las funciones de simulación del proyecto Cabo Verde
sys.path.append("2.4.Cabo Verde")

from simulacion_base import simular_partido

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
        label=f"Chelsea 04/05 ({chelsea_0405['gc_campeon']} GC)",
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
        chelsea_0405["gc_campeon"],
        color="red",
        linestyle=":",
        label=f"Récord Mínimo (Chelsea 04/05 = {chelsea_0405['gc_campeon']} GC)",
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
    print("Estadísticas del Ranking Elo:")
    print(stats_elo.round(2).to_string())

    # Gráfico Barplot Rankings Elo
    # Selecciones directamente relacionadas con los análisis de Cabo Verde: eliminatorias CAF y Grupo H del Mundial.
    equipos_seleccionados = [
        "Cabo Verde",
        "Camerún",
        "Libia",
        "Angola",
        "Mauricio",
        "Esuatini",
        "España",
        "Uruguay",
        "Arabia Saudita"
    ]

    df_elo_grafica = df_elo[
        df_elo["equipo"].isin(equipos_seleccionados)
    ].copy()

    df_elo_sorted = df_elo_grafica.sort_values(
        by="elo_rating",
        ascending=True
    )
    plt.figure(figsize=(9, 6))
    colores = [
        "orange" if eq == "Cabo Verde" else "skyblue"
        for eq in df_elo_sorted["equipo"]
    ]
    plt.barh(
        df_elo_sorted["equipo"],
        df_elo_sorted["elo_rating"],
        color=colores
    )
    plt.title("Ranking Elo de Selecciones Analizadas")
    plt.xlabel("Rating Elo")
    plt.grid(
        axis="x",
        linestyle="--",
        alpha=0.7
    )
    plt.tight_layout()
    plt.savefig("2.4.Cabo Verde/Graficas/barplot_elo_selecciones.png")
    plt.close()

    print(
        "\n    Gráfica Elo guardada en '2.4.Cabo Verde/Graficas/barplot_elo_selecciones.png'"
    )


# PRUEBA DE FUNCIONES BASE

if os.path.exists(ruta_elo_limpio):

    print(
        "\n--- PRUEBA DE SIMULACIÓN "
        "DE PARTIDO Y ASIGNACIÓN DE PUNTOS ---"
    )

    dict_elo = dict(
        zip(
            df_elo["equipo"],
            df_elo["elo_rating"]
        )
    )

    # Semillas para reproducibilidad
    random.seed(42)
    np.random.seed(42)

    # Simular 5 enfrentamientos de prueba Cabo Verde vs Camerún
    print(
        "Simulación de 5 partidos "
        "Cabo Verde vs Camerún:"
    )

    for i in range(1, 6):

        (
            pts_a,
            pts_b,
            goles_a,
            goles_b,
            res
        ) = simular_partido(
            "Cabo Verde",
            "Camerún",
            dict_elo,
            neutral=True
        )

        print(
            f"   Partido {i}: "
            f"Cabo Verde {goles_a}-{goles_b} Camerún "
            f"-> {res} "
            f"-> Cabo Verde obtiene {pts_a} pts | "
            f"Camerún obtiene {pts_b} pts"
        )
