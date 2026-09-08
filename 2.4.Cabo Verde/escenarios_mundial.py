import random
import pandas as pd
import os
import matplotlib.pyplot as plt

from simulacion_base import simular_partido


EQUIPOS_GRUPO = [
    "Cabo Verde",
    "Uruguay",
    "España",
    "Arabia Saudita"
]


# Carga los ratings Elo necesarios para el grupo mundialista
def cargar_elo(ruta="Data/elo_limpio.csv"):
    df_elo = pd.read_csv(ruta)

    elo_dict = dict(
        zip(
            df_elo["equipo"],
            df_elo["elo_rating"]
        )
    )

    faltantes = [
        equipo
        for equipo in EQUIPOS_GRUPO
        if equipo not in elo_dict
    ]

    if faltantes:
        raise ValueError(
            f"Faltan ratings Elo para: {faltantes}"
        )

    return elo_dict


# Crea una tabla vacía para el grupo
def crear_tabla():
    tabla = {}

    for equipo in EQUIPOS_GRUPO:
        tabla[equipo] = {
            "PJ": 0,
            "G": 0,
            "E": 0,
            "P": 0,
            "Pts": 0
        }

    return tabla


# Actualiza la tabla después de un partido
def actualizar_tabla(
    tabla,
    equipo_a,
    equipo_b,
    puntos_a,
    puntos_b
):
    tabla[equipo_a]["PJ"] += 1
    tabla[equipo_b]["PJ"] += 1

    tabla[equipo_a]["Pts"] += puntos_a
    tabla[equipo_b]["Pts"] += puntos_b

    if puntos_a == 3:
        tabla[equipo_a]["G"] += 1
        tabla[equipo_b]["P"] += 1

    elif puntos_b == 3:
        tabla[equipo_b]["G"] += 1
        tabla[equipo_a]["P"] += 1

    else:
        tabla[equipo_a]["E"] += 1
        tabla[equipo_b]["E"] += 1


# Convierte la tabla a DataFrame y la ordena por puntos
def convertir_tabla_dataframe(tabla):
    df_tabla = pd.DataFrame.from_dict(
        tabla,
        orient="index"
    )

    df_tabla.index.name = "Equipo"

    return df_tabla.sort_values(
        by="Pts",
        ascending=False
    )


# Fija los tres empates de Cabo Verde
def aplicar_empates_cabo_verde(tabla):
    rivales = [
        "Uruguay",
        "España",
        "Arabia Saudita"
    ]

    for rival in rivales:
        actualizar_tabla(
            tabla,
            "Cabo Verde",
            rival,
            1,
            1
        )


# Escenario 1: Uruguay empata con España
def escenario_uruguay_empata_espana(elo_dict):
    tabla = crear_tabla()

    # Cabo Verde empata sus tres partidos
    aplicar_empates_cabo_verde(tabla)

    # Uruguay empata con España
    actualizar_tabla(
        tabla,
        "Uruguay",
        "España",
        1,
        1
    )

    # Uruguay vs Arabia Saudita
    puntos_uru, puntos_ars, resultado_uru_ars = simular_partido(
        "Uruguay",
        "Arabia Saudita",
        elo_dict
    )

    actualizar_tabla(
        tabla,
        "Uruguay",
        "Arabia Saudita",
        puntos_uru,
        puntos_ars
    )

    # España vs Arabia Saudita
    puntos_esp, puntos_ars, resultado_esp_ars = simular_partido(
        "España",
        "Arabia Saudita",
        elo_dict
    )

    actualizar_tabla(
        tabla,
        "España",
        "Arabia Saudita",
        puntos_esp,
        puntos_ars
    )

    return (
        tabla,
        resultado_uru_ars,
        resultado_esp_ars
    )


# Escenario 2: Uruguay derrota a España
def escenario_uruguay_gana_espana(elo_dict):
    tabla = crear_tabla()

    # Cabo Verde empata sus tres partidos
    aplicar_empates_cabo_verde(tabla)

    # Uruguay derrota a España
    actualizar_tabla(
        tabla,
        "Uruguay",
        "España",
        3,
        0
    )

    # Uruguay vs Arabia Saudita
    puntos_uru, puntos_ars, resultado_uru_ars = simular_partido(
        "Uruguay",
        "Arabia Saudita",
        elo_dict
    )

    actualizar_tabla(
        tabla,
        "Uruguay",
        "Arabia Saudita",
        puntos_uru,
        puntos_ars
    )

    # España vs Arabia Saudita
    puntos_esp, puntos_ars, resultado_esp_ars = simular_partido(
        "España",
        "Arabia Saudita",
        elo_dict
    )

    actualizar_tabla(
        tabla,
        "España",
        "Arabia Saudita",
        puntos_esp,
        puntos_ars
    )

    return (
        tabla,
        resultado_uru_ars,
        resultado_esp_ars
    )


# Determina la posición de Cabo Verde únicamente por puntos
def clasificar_posicion_cabo_verde(tabla):
    puntos_cv = tabla["Cabo Verde"]["Pts"]

    equipos_superiores = sum(
        1
        for equipo in EQUIPOS_GRUPO
        if tabla[equipo]["Pts"] > puntos_cv
    )

    equipos_igualados = sum(
        1
        for equipo in EQUIPOS_GRUPO
        if tabla[equipo]["Pts"] == puntos_cv
    )

    posicion_minima = equipos_superiores + 1
    posicion_maxima = equipos_superiores + equipos_igualados

    if equipos_igualados == 1:
        return f"{posicion_minima}°"

    return (
        f"Empate {posicion_minima}°-"
        f"{posicion_maxima}°"
    )


# Ejecuta Monte Carlo para uno de los escenarios condicionados
def monte_carlo_escenario(
    elo_dict,
    escenario,
    n_simulaciones=100000
):
    resultados = {}

    for _ in range(n_simulaciones):

        if escenario == "empate":
            tabla, _, _ = escenario_uruguay_empata_espana(
                elo_dict
            )

        elif escenario == "victoria_uruguay":
            tabla, _, _ = escenario_uruguay_gana_espana(
                elo_dict
            )

        else:
            raise ValueError(
                "Escenario no reconocido"
            )

        posicion = clasificar_posicion_cabo_verde(
            tabla
        )

        resultados[posicion] = (
            resultados.get(posicion, 0) + 1
        )

    porcentajes = {
        posicion: cantidad / n_simulaciones * 100
        for posicion, cantidad in resultados.items()
    }

    return porcentajes


# Muestra los resultados del Monte Carlo
def mostrar_resultados_monte_carlo(
    titulo,
    resultados
):
    print(f"\n--- {titulo} ---")

    for posicion, porcentaje in sorted(
        resultados.items()
    ):
        print(
            f"{posicion:<15}: "
            f"{porcentaje:.2f}%"
        )

def graficar_resultados_monte_carlo(
    resultados_empate,
    resultados_victoria,
    ruta="Graficas/escenarios_mundial_cabo_verde.png"
):
    categorias = [
        "2°",
        "3°",
        "4°",
        "Empate 2°-3°",
        "Empate 1°-4°"
    ]

    valores_empate = [
        resultados_empate.get(categoria, 0)
        for categoria in categorias
    ]

    valores_victoria = [
        resultados_victoria.get(categoria, 0)
        for categoria in categorias
    ]

    x = range(len(categorias))
    ancho = 0.35

    plt.figure(figsize=(10, 6))

    barras_empate = plt.bar(
        [i - ancho / 2 for i in x],
        valores_empate,
        width=ancho,
        label="Uruguay empata con España"
    )

    barras_victoria = plt.bar(
        [i + ancho / 2 for i in x],
        valores_victoria,
        width=ancho,
        label="Uruguay derrota a España"
    )

    plt.xticks(
        list(x),
        categorias,
        rotation=15
    )

    plt.ylabel("Probabilidad (%)")
    plt.xlabel("Posición de Cabo Verde")

    plt.title(
        "Posición de Cabo Verde con 3 empates bajo dos escenarios Uruguay-España"
    )

    plt.legend()
    plt.grid(
        axis="y",
        alpha=0.3
    )

    # Mostrar el porcentaje encima de cada barra
    for barras in [barras_empate, barras_victoria]:
        for barra in barras:
            altura = barra.get_height()

            if altura > 0:
                plt.text(
                    barra.get_x() + barra.get_width() / 2,
                    altura + 0.5,
                    f"{altura:.2f}%",
                    ha="center",
                    va="bottom",
                    fontsize=8
                )

    os.makedirs(
        os.path.dirname(ruta),
        exist_ok=True
    )

    plt.tight_layout()
    plt.savefig(
        ruta,
        dpi=300
    )

    plt.close()

    print(
        f"\nGráfica guardada en: {ruta}"
    )

if __name__ == "__main__":
    print("DÍA 7 - CABO VERDE: ESCENARIOS DEL GRUPO MUNDIALISTA")

    elo_dict = cargar_elo()

    print("\nRatings Elo utilizados:")

    for equipo in EQUIPOS_GRUPO:
        print(
            f"{equipo:<15}: "
            f"{elo_dict[equipo]}"
        )

    # Escenario base
    tabla = crear_tabla()

    aplicar_empates_cabo_verde(tabla)

    df_tabla = convertir_tabla_dataframe(
        tabla
    )

    print("\n--- ESCENARIO BASE: CABO VERDE EMPATA SUS 3 PARTIDOS ---")

    print(df_tabla.to_string())

    # Ejemplo individual del escenario 1
    print("\n--- ESCENARIO 1: URUGUAY EMPATA CON ESPAÑA ---")

    random.seed(42)

    tabla_escenario_1, resultado_uru_ars, resultado_esp_ars = (
        escenario_uruguay_empata_espana(
            elo_dict
        )
    )

    print(
        f"Uruguay vs Arabia Saudita -> "
        f"{resultado_uru_ars}"
    )

    print(
        f"España vs Arabia Saudita -> "
        f"{resultado_esp_ars}"
    )

    df_escenario_1 = convertir_tabla_dataframe(
        tabla_escenario_1
    )

    print("\nTabla final:")
    print(df_escenario_1.to_string())

    # Ejemplo individual del escenario 2
    print("\n--- ESCENARIO 2: URUGUAY DERROTA A ESPAÑA ---")

    random.seed(42)

    tabla_escenario_2, resultado_uru_ars, resultado_esp_ars = (
        escenario_uruguay_gana_espana(
            elo_dict
        )
    )

    print(
        f"Uruguay vs Arabia Saudita -> "
        f"{resultado_uru_ars}"
    )

    print(
        f"España vs Arabia Saudita -> "
        f"{resultado_esp_ars}"
    )

    df_escenario_2 = convertir_tabla_dataframe(
        tabla_escenario_2
    )

    print("\nTabla final:")
    print(df_escenario_2.to_string())

    # Monte Carlo
    n_simulaciones = 100000

    print(
        f"\nEJECUTANDO MONTE CARLO "
        f"({n_simulaciones:,} simulaciones por escenario)..."
    )

    random.seed(42)

    resultados_empate = monte_carlo_escenario(
        elo_dict,
        "empate",
        n_simulaciones
    )

    random.seed(42)

    resultados_victoria = monte_carlo_escenario(
        elo_dict,
        "victoria_uruguay",
        n_simulaciones
    )

    mostrar_resultados_monte_carlo(
        "MONTE CARLO: URUGUAY EMPATA CON ESPAÑA",
        resultados_empate
    )

    mostrar_resultados_monte_carlo(
        "MONTE CARLO: URUGUAY DERROTA A ESPAÑA",
        resultados_victoria
    )

    graficar_resultados_monte_carlo(
        resultados_empate,
        resultados_victoria
    )

    print("\nNota: las posiciones empatadas indican que dos o más equipos terminaron con los mismos puntos.\nComo el modelo actual no simula marcadores, no se aplica diferencia de goles como criterio de desempate.")

