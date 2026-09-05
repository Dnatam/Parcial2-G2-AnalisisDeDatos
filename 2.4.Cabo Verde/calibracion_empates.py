import pandas as pd
import numpy as np
from scipy.optimize import minimize_scalar

def limpiar_nombre(nombre):
    if pd.isna(nombre):
        return nombre

    nombre = str(nombre)

    # Reemplaza espacios especiales por espacios normales
    nombre = nombre.replace("\xa0", " ")

    # Elimina espacios sobrantes
    nombre = " ".join(nombre.split())

    return nombre

def cargar_datos():
    resultados = pd.read_csv("Data/results.csv")
    elo = pd.read_csv("Data/eloratings.csv")

    resultados["date"] = pd.to_datetime(
        resultados["date"],
        format="mixed",
        errors="coerce"
    )

    elo["date"] = pd.to_datetime(
        elo["date"],
        format="%m/%d/%Y",
        errors="coerce"
    )

    resultados["home_team"] = resultados["home_team"].apply(limpiar_nombre)
    resultados["away_team"] = resultados["away_team"].apply(limpiar_nombre)
    elo["team"] = elo["team"].apply(limpiar_nombre)

    return resultados, elo

if __name__ == "__main__":
    resultados, elo = cargar_datos()

    # Para calibrar usamos fútbol internacional reciente
    resultados = resultados[
        (resultados["date"] >= "2008-01-01") &
        (resultados["date"] <= "2025-12-31")
    ]

    print("Partidos entre 2008 y 2025:", len(resultados))
    print("Registros históricos Elo:", len(elo))

    print("\nPrimeros partidos:")
    print(resultados.head())

    print("\nPrimeros registros Elo:")
    print(elo.head())

    # Equipos presentes en cada archivo
    equipos_resultados = set(resultados["home_team"]) | set(resultados["away_team"])
    equipos_elo = set(elo["team"])

    equipos_comunes = equipos_resultados & equipos_elo
    equipos_sin_elo = equipos_resultados - equipos_elo

    print("\n--- COMPATIBILIDAD DE EQUIPOS ---")
    print(f"Equipos en resultados: {len(equipos_resultados)}")
    print(f"Equipos en Elo: {len(equipos_elo)}")
    print(f"Equipos con coincidencia: {len(equipos_comunes)}")
    print(f"Equipos sin coincidencia: {len(equipos_sin_elo)}")

    print("\nEjemplos de equipos sin coincidencia:")
    print(sorted(equipos_sin_elo)[:30])

    # Verifica cuántos partidos tienen ambos equipos disponibles en el histórico Elo
    mascara_compatibles = (
        resultados["home_team"].isin(equipos_elo) &
        resultados["away_team"].isin(equipos_elo)
    )

    partidos_compatibles = resultados[mascara_compatibles].copy()

    porcentaje_compatibles = (
        len(partidos_compatibles) / len(resultados) * 100
    )

    print("\n--- COBERTURA DE PARTIDOS ---")
    print(f"Partidos totales: {len(resultados)}")
    print(f"Partidos con ambos equipos en Elo: {len(partidos_compatibles)}")
    print(f"Cobertura: {porcentaje_compatibles:.2f}%")

    # Revisa la estructura temporal del archivo Elo
    print("\n--- ESTRUCTURA DEL HISTÓRICO ELO ---")
    print(f"Fechas Elo distintas: {elo['date'].nunique()}")
    print(f"Fecha Elo más antigua: {elo['date'].min()}")
    print(f"Fecha Elo más reciente: {elo['date'].max()}")

    registros_por_fecha = (
        elo.groupby("date")
        .size()
        .sort_values(ascending=False)
    )

    print("\nFechas con más selecciones registradas:")
    print(registros_por_fecha.head(10))

    # Prepara el histórico Elo para búsquedas temporales
    elo_ordenado = elo[
        ["date", "team", "rating"]
    ].dropna().sort_values(["team", "date"])

    def obtener_elo_anterior(equipo, fecha):
        historial = elo_ordenado[
            (elo_ordenado["team"] == equipo) &
            (elo_ordenado["date"] < fecha)
        ]

        if historial.empty:
            return None

        return historial.iloc[-1]["rating"]

    # Prueba el cruce temporal con una muestra de partidos
    muestra = partidos_compatibles.head(10).copy()

    muestra["elo_home"] = muestra.apply(
        lambda fila: obtener_elo_anterior(
            fila["home_team"],
            fila["date"]
        ),
        axis=1
    )

    muestra["elo_away"] = muestra.apply(
        lambda fila: obtener_elo_anterior(
            fila["away_team"],
            fila["date"]
        ),
        axis=1
    )

    print("\n--- PRUEBA DE ELO PREVIO AL PARTIDO ---")

    print(
        muestra[
            [
                "date",
                "home_team",
                "away_team",
                "elo_home",
                "elo_away"
            ]
        ].to_string(index=False)
    )

    # Construye una fila por equipo y partido
    partidos_home = partidos_compatibles[
        ["date", "home_team", "away_team", "home_score", "away_score"]
    ].copy()

    partidos_home["id_partido"] = partidos_home.index
    partidos_home["team"] = partidos_home["home_team"]

    partidos_away = partidos_compatibles[
        ["date", "home_team", "away_team", "home_score", "away_score"]
    ].copy()

    partidos_away["id_partido"] = partidos_away.index
    partidos_away["team"] = partidos_away["away_team"]

    # Busca el último Elo disponible estrictamente antes del partido
    def asignar_elo_previo(partidos_equipo):
        resultados_cruce = []

        for equipo, grupo in partidos_equipo.groupby("team"):
            historial = elo_ordenado[
                elo_ordenado["team"] == equipo
            ][["date", "rating"]].sort_values("date")

            if historial.empty:
                continue

            grupo = grupo.sort_values("date")

            cruce = pd.merge_asof(
                grupo,
                historial,
                on="date",
                direction="backward",
                allow_exact_matches=False
            )

            resultados_cruce.append(cruce)

        return pd.concat(resultados_cruce, ignore_index=True)

    home_con_elo = asignar_elo_previo(partidos_home)
    away_con_elo = asignar_elo_previo(partidos_away)

    home_con_elo = home_con_elo[
        ["id_partido", "rating"]
    ].rename(columns={"rating": "elo_home"})

    away_con_elo = away_con_elo[
        ["id_partido", "rating"]
    ].rename(columns={"rating": "elo_away"})

    # Une los Elo con los partidos originales
    calibracion = partidos_compatibles.copy()
    calibracion["id_partido"] = calibracion.index

    calibracion = calibracion.merge(
        home_con_elo,
        on="id_partido",
        how="left"
    )

    calibracion = calibracion.merge(
        away_con_elo,
        on="id_partido",
        how="left"
    )

    # Solo conserva partidos con Elo previo para ambos equipos
    calibracion = calibracion.dropna(
        subset=["elo_home", "elo_away"]
    )

    # Diferencia absoluta de Elo
    calibracion["diferencia_elo"] = abs(
        calibracion["elo_home"] - calibracion["elo_away"]
    )

    # 1 = empate, 0 = no empate
    calibracion["empate"] = (
        calibracion["home_score"] == calibracion["away_score"]
    ).astype(int)

    print("\n--- DATASET DE CALIBRACIÓN ---")
    print(f"Partidos disponibles inicialmente: {len(partidos_compatibles)}")
    print(f"Partidos con Elo previo para ambos equipos: {len(calibracion)}")

    cobertura_elo = (
        len(calibracion) / len(partidos_compatibles) * 100
    )

    print(f"Cobertura temporal Elo: {cobertura_elo:.2f}%")
    print(f"Empates observados: {calibracion['empate'].sum()}")
    print(f"Tasa de empate observada: {calibracion['empate'].mean() * 100:.2f}%")

    print("\nPrimeros registros:")
    print(
        calibracion[
            [
                "date",
                "home_team",
                "away_team",
                "elo_home",
                "elo_away",
                "diferencia_elo",
                "empate"
            ]
        ].head(10).to_string(index=False)
    )

    # Calibra k_empate mediante máxima verosimilitud
    def loglik_negativa(k):
        probabilidades = (
            k * np.exp(
                -((calibracion["diferencia_elo"] / 400) ** 2)
            )
        )

        probabilidades = np.clip(
            probabilidades,
            1e-10,
            1 - 1e-10
        )

        y = calibracion["empate"]

        loglik = (
            y * np.log(probabilidades) +
            (1 - y) * np.log(1 - probabilidades)
        ).sum()

        return -loglik

    resultado_opt = minimize_scalar(
        loglik_negativa,
        bounds=(0.01, 0.60),
        method="bounded"
    )

    if not resultado_opt.success:
        raise RuntimeError(
            "La calibración de k_empate no convergió."
        )

    k_calibrado = resultado_opt.x

    print("\n--- CALIBRACIÓN DEL MODELO DE EMPATE ---")
    print(f"k_empate anterior: 0.2800")
    print(f"k_empate calibrado: {k_calibrado:.4f}")