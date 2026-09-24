import random
import numpy as np
import pandas as pd

from simulador_mundial import (
    GRUPOS,
    cargar_elo,
    verificar_equipos,
    simular_grupo,
    simular_grupos_sin_h,
    ordenar_grupo,
    ordenar_terceros
)


# CONFIGURACIÓN

N_SIMULACIONES = 100000
SEMILLA = 42


# Simula el Grupo H hasta obtener un escenario donde Cabo Verde termine tercero con exactamente tres puntos.
def simular_grupo_h_condicionado(elo_dict):
    equipos_h = GRUPOS["H"]

    # Repite la simulación hasta encontrar un resultado que cumpla las condiciones del escenario analizado.
    while True:
        tabla_h, _ = simular_grupo(
            equipos_h,
            elo_dict
        )

        orden_h = ordenar_grupo(
            tabla_h,
            elo_dict
        )

        posicion_cv = (
            orden_h.index("Cabo Verde") + 1
        )

        puntos_cv = tabla_h[
            "Cabo Verde"
        ]["Pts"]

        if (
            posicion_cv == 3
            and puntos_cv == 3
        ):
            return tabla_h


# Estima mediante Monte Carlo la probabilidad de que Cabo Verde clasifique entre los ocho mejores terceros, condicionado a que termine tercero del Grupo H con exactamente tres puntos.
def ejecutar_monte_carlo(
    elo_dict,
    n_simulaciones=N_SIMULACIONES
):
    veces_mejores_ocho = 0
    resultados_terceros = []

    for i in range(n_simulaciones):

        # Genera un Grupo H donde Cabo Verde termina tercero con exactamente tres puntos.
        tabla_h = simular_grupo_h_condicionado(
            elo_dict
        )

        # Obtiene las estadísticas de Cabo Verde en el escenario generado.
        datos_cv = tabla_h[
            "Cabo Verde"
        ].copy()

        datos_cv["Equipo"] = "Cabo Verde"
        datos_cv["Grupo"] = "H"

        # Simula los otros once grupos del Mundial y obtiene el tercer lugar de cada uno.
        terceros = simular_grupos_sin_h(
            elo_dict
        )

        # Incorpora a Cabo Verde como el tercer lugar correspondiente al Grupo H.
        terceros.append(
            datos_cv
        )

        # Ordena los doce terceros utilizando los mismos criterios de clasificación del modelo.
        terceros_ordenados = ordenar_terceros(
            terceros,
            elo_dict
        )

        # Determina la posición de Cabo Verde entre los doce terceros.
        posicion_tercero_cv = next(
            posicion
            for posicion, tercero in enumerate(
                terceros_ordenados,
                start=1
            )
            if tercero["Equipo"] == "Cabo Verde"
        )

        # Si Cabo Verde se encuentra entre las primeras ocho posiciones, clasifica como uno de los mejores terceros.
        if posicion_tercero_cv <= 8:
            veces_mejores_ocho += 1

        # Guarda las estadísticas de Cabo Verde para analizar posteriormente su comportamiento entre los terceros lugares.
        resultados_terceros.append({
            "posicion_tercero": posicion_tercero_cv,
            "puntos": datos_cv["Pts"],
            "diferencia_goles": datos_cv["DG"],
            "goles_favor": datos_cv["GF"],
            "goles_contra": datos_cv["GC"]
        })

        # Muestra el progreso cada diez mil simulaciones.
        if (i + 1) % 10000 == 0:
            print(
                f"Simulaciones completadas: "
                f"{i + 1:,}/{n_simulaciones:,}"
            )

    return (
        veces_mejores_ocho,
        resultados_terceros
    )


# PROGRAMA PRINCIPAL

if __name__ == "__main__":

    print("MONTE CARLO - MUNDIAL 2026")
    print(
        "CABO VERDE COMO TERCERO "
        "DEL GRUPO H CON 3 PUNTOS"
    )

    # Fija las semillas para que los resultados de la simulación puedan reproducirse.
    random.seed(SEMILLA)
    np.random.seed(SEMILLA)

    # Carga los ratings Elo y verifica que estén disponibles las 48 selecciones utilizadas en la simulación.
    elo_dict = cargar_elo()

    verificar_equipos(
        elo_dict
    )

    # Ejecuta el escenario condicionado cien mil veces.
    print("\nINICIANDO SIMULACIÓN")

    (
        veces_mejores_ocho,
        resultados_terceros
    ) = ejecutar_monte_carlo(
        elo_dict,
        N_SIMULACIONES
    )

    # Calcula la frecuencia relativa con la que Cabo Verde queda entre los ocho mejores terceros.
    prob_mejores_ocho = (
        veces_mejores_ocho
        / N_SIMULACIONES
        * 100
    )

    veces_fuera_ocho = (
        N_SIMULACIONES
        - veces_mejores_ocho
    )

    print("\nRESULTADO DEL ESCENARIO CONDICIONADO")

    print(
        "Condición analizada: Cabo Verde termina "
        "3° del Grupo H con exactamente 3 puntos."
    )

    print(
        f"\nNúmero de simulaciones: "
        f"{N_SIMULACIONES:,}"
    )

    print(
        f"Veces que Cabo Verde quedó entre los "
        f"8 mejores terceros: "
        f"{veces_mejores_ocho:,}"
    )

    print(
        f"Veces que Cabo Verde quedó fuera de los "
        f"8 mejores terceros: "
        f"{veces_fuera_ocho:,}"
    )

    print(
        f"Probabilidad estimada de clasificar "
        f"como uno de los 8 mejores terceros: "
        f"{prob_mejores_ocho:.2f}%"
    )

    # Convierte los resultados individuales en un DataFrame para analizar la distribución de Cabo Verde entre los doce terceros.
    if resultados_terceros:

        df_terceros = pd.DataFrame(
            resultados_terceros
        )

        print(
            "\nDISTRIBUCIÓN DE CABO VERDE "
            "ENTRE LOS 12 TERCEROS"
        )

        print(
            "\nPosición promedio entre los terceros: "
            f"{df_terceros['posicion_tercero'].mean():.2f}"
        )

        print(
            "Puntos promedio: "
            f"{df_terceros['puntos'].mean():.2f}"
        )

        print(
            "Diferencia de goles promedio: "
            f"{df_terceros['diferencia_goles'].mean():.2f}"
        )

        print(
            "Goles a favor promedio: "
            f"{df_terceros['goles_favor'].mean():.2f}"
        )

        print(
            "Goles en contra promedio: "
            f"{df_terceros['goles_contra'].mean():.2f}"
        )

        # Calcula la frecuencia con la que Cabo Verde ocupa cada posición entre los doce terceros.
        frecuencia_posiciones = (
            df_terceros[
                "posicion_tercero"
            ]
            .value_counts()
            .sort_index()
        )

        print("\nFrecuencia de posiciones:")

        for posicion, cantidad in (
            frecuencia_posiciones.items()
        ):

            porcentaje = (
                cantidad
                / N_SIMULACIONES
                * 100
            )

            if posicion <= 8:
                estado = "CLASIFICA"
            else:
                estado = "NO CLASIFICA"

            print(
                f"{int(posicion)}°: "
                f"{cantidad:,} "
                f"({porcentaje:.2f}%) "
                f"- {estado}"
            )

        # Guarda los resultados de las simulaciones para su análisis posterior.
        df_terceros.to_csv(
            "Data/monte_carlo_terceros_cabo_verde.csv",
            index=False
        )

        print(
            "\nArchivo generado: "
            "Data/monte_carlo_terceros_cabo_verde.csv"
        )

    # Guarda un resumen con la cantidad y porcentaje de simulaciones en las que Cabo Verde clasifica o queda eliminado como tercer lugar.
    resumen = pd.DataFrame({
        "resultado": [
            "Entre los 8 mejores terceros",
            "Fuera de los 8 mejores terceros"
        ],
        "cantidad": [
            veces_mejores_ocho,
            veces_fuera_ocho
        ],
        "porcentaje": [
            prob_mejores_ocho,
            100 - prob_mejores_ocho
        ]
    })

    resumen.to_csv(
        "Data/monte_carlo_mundial_resumen.csv",
        index=False
    )

    print(
        "\nArchivo generado: "
        "Data/monte_carlo_mundial_resumen.csv"
    )

    print("\nMONTE CARLO FINALIZADO")