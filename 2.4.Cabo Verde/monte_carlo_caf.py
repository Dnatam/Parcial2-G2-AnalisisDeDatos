import random
import matplotlib.pyplot as plt

from simulador_caf import (
    cargar_elo,
    simular_grupo,
    obtener_ganador
)

# Repite la clasificación CAF para estimar la probabilidad de que Cabo Verde termine primero y clasifique directamente
def monte_carlo_clasificacion(n_simulaciones=100000, semilla=42):
    random.seed(semilla)

    elo_dict = cargar_elo()

    clasificaciones = 0
    ganadores = {
        equipo: 0
        for equipo in [
            "Cabo Verde",
            "Camerún",
            "Libia",
            "Angola",
            "Mauricio",
            "Esuatini"
        ]
    }

    for _ in range(n_simulaciones):
        tabla, _ = simular_grupo(elo_dict)

        ganador = obtener_ganador(tabla)

        ganadores[ganador] += 1

        if ganador == "Cabo Verde":
            clasificaciones += 1

    probabilidad = clasificaciones / n_simulaciones

    return probabilidad, clasificaciones, ganadores

if __name__ == "__main__":
    print("DÍA 5 - CABO VERDE: MONTE CARLO CLASIFICACIÓN CAF")

    n_simulaciones = 100000

    probabilidad, clasificaciones, ganadores = monte_carlo_clasificacion(
        n_simulaciones=n_simulaciones,
        semilla=42
    )

    print(f"\nNúmero de simulaciones: {n_simulaciones:,}")

    print("\n--- CLASIFICACIÓN DIRECTA DE CABO VERDE ---")
    print(
        f"Clasificaciones: "
        f"{clasificaciones:,} de {n_simulaciones:,}"
    )
    print(
        f"Probabilidad estimada: "
        f"{probabilidad:.6f}"
    )
    print(
        f"Probabilidad estimada: "
        f"{probabilidad * 100:.2f}%"
    )

    print("\n--- PROBABILIDAD DE GANAR EL GRUPO ---")

    for equipo, cantidad in sorted(
        ganadores.items(),
        key=lambda x: x[1],
        reverse=True
    ):
        porcentaje = cantidad / n_simulaciones * 100

        print(
            f"{equipo:<12}: "
            f"{cantidad:>6,} "
            f"({porcentaje:>6.2f}%)"
        )

    # Gráfica de probabilidades de ganar el grupo
    ganadores_ordenados = sorted(
        ganadores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    equipos = [
        equipo
        for equipo, _ in ganadores_ordenados
    ]

    probabilidades = [
        cantidad / n_simulaciones * 100
        for _, cantidad in ganadores_ordenados
    ]

    colores = [
        "orange" if equipo == "Cabo Verde" else "skyblue"
        for equipo in equipos
    ]

    plt.figure(figsize=(9, 6))

    barras = plt.bar(
        equipos,
        probabilidades,
        color=colores
    )

    # Mostrar el porcentaje sobre cada barra
    for barra, porcentaje in zip(barras, probabilidades):
        plt.text(
            barra.get_x() + barra.get_width() / 2,
            barra.get_height() + 0.5,
            f"{porcentaje:.2f}%",
            ha="center",
            va="bottom"
        )

    plt.title("Probabilidad de Clasificación Directa al Mundial")
    plt.xlabel("Selección")
    plt.ylabel("Probabilidad de ganar el grupo (%)")
    plt.ylim(0, max(probabilidades) + 7)
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.xticks(rotation=20)
    plt.tight_layout()

    plt.savefig(
        "Graficas/probabilidad_clasificacion_caf.png",
        dpi=300
    )

    plt.close()

    print(
        "\nGráfica guardada en "
        "'Graficas/probabilidad_clasificacion_caf.png'"
    )