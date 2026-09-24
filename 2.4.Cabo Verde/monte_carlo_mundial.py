import random
import numpy as np
import pandas as pd

from simulador_mundial import (
    GRUPOS,
    cargar_elo,
    verificar_equipos,
    simular_mundial,
    ordenar_grupo,
    ordenar_terceros
)


# CONFIGURACIÓN

N_SIMULACIONES = 100000
SEMILLA = 42


# FUNCIÓN PRINCIPAL DE MONTE CARLO

def ejecutar_monte_carlo(elo_dict, n_simulaciones=N_SIMULACIONES):

    resultados_posicion_grupo_h = {
        1: 0,
        2: 0,
        3: 0,
        4: 0
    }

    veces_tercero = 0
    veces_mejores_ocho = 0
    veces_clasifica = 0

    resultados_terceros = []

    for i in range(n_simulaciones):

        resultados_grupos, terceros = simular_mundial(elo_dict)

        # Posición de Cabo Verde en el Grupo H

        tabla_h = resultados_grupos["H"]["tabla"]

        orden_h = ordenar_grupo(
            tabla_h,
            elo_dict
        )

        posicion_cv = orden_h.index("Cabo Verde") + 1

        resultados_posicion_grupo_h[posicion_cv] += 1

        # Si Cabo Verde terminó tercero

        if posicion_cv == 3:

            veces_tercero += 1

            # Ordenamos los 12 terceros
            terceros_ordenados = ordenar_terceros(
                terceros,
                elo_dict
            )

            # Buscamos la posición de Cabo Verde
            posicion_tercero_cv = None

            for posicion, tercero in enumerate(
                terceros_ordenados,
                start=1
            ):

                if tercero["Equipo"] == "Cabo Verde":
                    posicion_tercero_cv = posicion
                    break

            # Cabo Verde está entre los 8 mejores terceros

            if posicion_tercero_cv <= 8:

                veces_mejores_ocho += 1
                veces_clasifica += 1

            # Guardamos información para análisis posterior

            tercero_cv = next(
                tercero
                for tercero in terceros
                if tercero["Equipo"] == "Cabo Verde"
            )

            resultados_terceros.append({
                "posicion_tercero": posicion_tercero_cv,
                "puntos": tercero_cv["Pts"],
                "diferencia_goles": tercero_cv["DG"],
                "goles_favor": tercero_cv["GF"],
                "goles_contra": tercero_cv["GC"]
            })

        # Progreso

        if (i + 1) % 10000 == 0:

            print(
                f"Simulaciones completadas: "
                f"{i + 1:,}/{n_simulaciones:,}"
            )

    return (
        resultados_posicion_grupo_h,
        veces_tercero,
        veces_mejores_ocho,
        veces_clasifica,
        resultados_terceros
    )


# PROGRAMA PRINCIPAL

if __name__ == "__main__":

    print("=" * 75)
    print("MONTE CARLO - MUNDIAL 2026")
    print("CABO VERDE Y LOS 12 TERCEROS LUGARES")
    print("=" * 75)

    # Semillas para reproducibilidad

    random.seed(SEMILLA)
    np.random.seed(SEMILLA)

    # Cargar Elo

    elo_dict = cargar_elo()

    verificar_equipos(elo_dict)

    # Ejecutar Monte Carlo

    print("\n")
    print("=" * 75)
    print("INICIANDO SIMULACIÓN")
    print("=" * 75)

    (
        posiciones_h,
        veces_tercero,
        veces_mejores_ocho,
        veces_clasifica,
        resultados_terceros
    ) = ejecutar_monte_carlo(
        elo_dict,
        N_SIMULACIONES
    )

    # RESULTADOS DEL GRUPO H

    print("\n")
    print("=" * 75)
    print("RESULTADOS DE CABO VERDE EN EL GRUPO H")
    print("=" * 75)

    for posicion in range(1, 5):

        cantidad = posiciones_h[posicion]

        porcentaje = (
            cantidad / N_SIMULACIONES
        ) * 100

        print(
            f"{posicion}° lugar: "
            f"{cantidad:,} simulaciones "
            f"({porcentaje:.2f}%)"
        )

    # PROBABILIDAD DE TERMINAR TERCERO

    prob_tercero = (
        veces_tercero / N_SIMULACIONES
    ) * 100

    print("\n")
    print("=" * 75)
    print("CABO VERDE COMO TERCER LUGAR")
    print("=" * 75)

    print(
        f"Veces que terminó 3°: "
        f"{veces_tercero:,}"
    )

    print(
        f"Probabilidad estimada de terminar 3°: "
        f"{prob_tercero:.2f}%"
    )

    # PROBABILIDAD DE ESTAR ENTRE LOS 8 MEJORES TERCEROS

    print("\n")
    print("=" * 75)
    print("LOS 8 MEJORES TERCEROS")
    print("=" * 75)

    if veces_tercero > 0:

        prob_mejores_ocho_condicional = (
            veces_mejores_ocho / veces_tercero
        ) * 100

        print(
            f"Veces que Cabo Verde terminó entre los "
            f"8 mejores terceros: "
            f"{veces_mejores_ocho:,}"
        )

        print(
            f"Probabilidad de estar entre los 8 mejores "
            f"terceros dado que terminó 3°: "
            f"{prob_mejores_ocho_condicional:.2f}%"
        )

    else:

        prob_mejores_ocho_condicional = 0

        print(
            "Cabo Verde no terminó tercero en ninguna "
            "simulación."
        )

    # PROBABILIDAD TOTAL DE CLASIFICAR

    prob_clasifica = (
        veces_clasifica / N_SIMULACIONES
    ) * 100

    print("\n")
    print("=" * 75)
    print("CLASIFICACIÓN DE CABO VERDE")
    print("=" * 75)

    print(
        f"Simulaciones donde Cabo Verde clasificó: "
        f"{veces_clasifica:,}"
    )

    print(
        f"Probabilidad estimada de clasificar: "
        f"{prob_clasifica:.2f}%"
    )

    # DISTRIBUCIÓN DE CABO VERDE ENTRE LOS TERCEROS

    if resultados_terceros:

        df_terceros = pd.DataFrame(
            resultados_terceros
        )

        print("\n")
        print("=" * 75)
        print("DISTRIBUCIÓN DE CABO VERDE ENTRE LOS TERCEROS")
        print("=" * 75)

        print(
            "\nPosición promedio entre los terceros:",
            f"{df_terceros['posicion_tercero'].mean():.2f}"
        )

        print(
            "Puntos promedio cuando termina tercero:",
            f"{df_terceros['puntos'].mean():.2f}"
        )

        print(
            "Diferencia de goles promedio:",
            f"{df_terceros['diferencia_goles'].mean():.2f}"
        )

        # Frecuencia de cada posición

        frecuencia_posiciones = (
            df_terceros["posicion_tercero"]
            .value_counts()
            .sort_index()
        )

        print("\nFrecuencia de posiciones:")

        for posicion, cantidad in frecuencia_posiciones.items():

            porcentaje = (
                cantidad / veces_tercero
            ) * 100

            print(
                f"{int(posicion)}°: "
                f"{cantidad:,} "
                f"({porcentaje:.2f}%)"
            )

        # Guardar resultados

        df_terceros.to_csv(
            "Data/monte_carlo_terceros_cabo_verde.csv",
            index=False
        )

        print("\nArchivo generado:")
        print(
            "Data/monte_carlo_terceros_cabo_verde.csv"
        )

    # GUARDAR RESUMEN

    resumen = pd.DataFrame({
        "resultado": [
            "1er lugar Grupo H",
            "2do lugar Grupo H",
            "3er lugar Grupo H",
            "4to lugar Grupo H",
            "Entre los 8 mejores terceros",
            "Clasifica como tercero"
        ],
        "cantidad": [
            posiciones_h[1],
            posiciones_h[2],
            posiciones_h[3],
            posiciones_h[4],
            veces_mejores_ocho,
            veces_clasifica
        ],
        "porcentaje": [
            posiciones_h[1] / N_SIMULACIONES * 100,
            posiciones_h[2] / N_SIMULACIONES * 100,
            posiciones_h[3] / N_SIMULACIONES * 100,
            posiciones_h[4] / N_SIMULACIONES * 100,
            veces_mejores_ocho / N_SIMULACIONES * 100,
            prob_clasifica
        ]
    })

    resumen.to_csv(
        "Data/monte_carlo_mundial_resumen.csv",
        index=False
    )

    print("\nArchivo generado:")
    print("Data/monte_carlo_mundial_resumen.csv")

    print("\n")
    print("=" * 75)
    print("MONTE CARLO FINALIZADO")
    print("=" * 75)