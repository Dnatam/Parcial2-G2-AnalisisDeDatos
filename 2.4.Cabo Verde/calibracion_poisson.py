import pandas as pd
import numpy as np
from scipy.optimize import minimize
from scipy.special import gammaln

# Normaliza los nombres de las selecciones para facilitar la coincidencia entre el archivo de resultados y el histórico de ratings Elo.
def limpiar_nombre(nombre):
    if pd.isna(nombre):
        return nombre

    nombre = str(nombre)

    # Sustituye espacios especiales y elimina espacios sobrantes.
    nombre = nombre.replace("\xa0", " ")
    nombre = " ".join(nombre.split())

    return nombre

# Carga los resultados históricos de partidos y los ratings Elo históricos.
# Los resultados proporcionan los goles observados y el histórico Elo proporciona la fuerza relativa de cada selección antes de cada encuentro.
def cargar_datos():
    resultados = pd.read_csv("Data/results.csv")
    elo = pd.read_csv("Data/eloratings.csv")

    # Convierte las fechas a un formato temporal común para realizar posteriormente el cruce entre partidos y ratings Elo.
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

    # Normaliza los nombres antes de comparar ambos conjuntos de datos.
    resultados["home_team"] = resultados["home_team"].apply(limpiar_nombre)
    resultados["away_team"] = resultados["away_team"].apply(limpiar_nombre)
    elo["team"] = elo["team"].apply(limpiar_nombre)

    return resultados, elo


# Construye el conjunto de datos utilizado para calibrar el modelo Poisson.
# Cada partido queda asociado con los goles observados y con el último rating Elo disponible para cada selección antes del encuentro.
def preparar_dataset_calibracion(resultados, elo):

    # Utiliza partidos internacionales entre 2008 y 2025.
    # El límite superior evita incorporar resultados del período que posteriormente será analizado mediante la simulación del Mundial 2026.
    resultados = resultados[
        (resultados["date"] >= "2008-01-01") &
        (resultados["date"] <= "2025-12-31")
    ].copy()

    equipos_elo = set(elo["team"])

    # Conserva únicamente partidos en los que ambas selecciones aparecen en el histórico de ratings Elo.
    mascara_compatibles = (
        resultados["home_team"].isin(equipos_elo) &
        resultados["away_team"].isin(equipos_elo)
    )

    partidos = resultados[mascara_compatibles].copy()

    # Ordena el histórico Elo por selección y fecha para permitir la búsqueda temporal del rating anterior a cada partido.
    elo_ordenado = (
        elo[["date", "team", "rating"]]
        .dropna()
        .sort_values(["team", "date"])
    )

    # Crea una estructura para buscar el Elo previo del equipo local.
    partidos_home = partidos[
        [
            "date",
            "home_team",
            "away_team",
            "home_score",
            "away_score",
            "neutral"
        ]
    ].copy()

    partidos_home["id_partido"] = partidos_home.index
    partidos_home["team"] = partidos_home["home_team"]

    # Crea una estructura equivalente para buscar el Elo previo del equipo visitante.
    partidos_away = partidos[
        [
            "date",
            "home_team",
            "away_team",
            "home_score",
            "away_score",
            "neutral"
        ]
    ].copy()

    partidos_away["id_partido"] = partidos_away.index
    partidos_away["team"] = partidos_away["away_team"]

    # Asigna a cada selección el último rating Elo registrado estrictamente antes de la fecha del partido.
    def asignar_elo_previo(partidos_equipo):
        resultados_cruce = []

        for equipo, grupo in partidos_equipo.groupby("team"):
            historial = elo_ordenado[
                elo_ordenado["team"] == equipo
            ][
                ["date", "rating"]
            ].sort_values("date")

            if historial.empty:
                continue

            grupo = grupo.sort_values("date")

            # merge_asof busca el registro temporal más cercano hacia atrás. 
            # No se permiten coincidencias en la misma fecha para garantizar que el rating utilizado sea anterior al encuentro.
            cruce = pd.merge_asof(
                grupo,
                historial,
                on="date",
                direction="backward",
                allow_exact_matches=False
            )

            resultados_cruce.append(cruce)

        return pd.concat(
            resultados_cruce,
            ignore_index=True
        )

    home_con_elo = asignar_elo_previo(partidos_home)
    away_con_elo = asignar_elo_previo(partidos_away)

    # Conserva el identificador del partido y el rating Elo encontrado para posteriormente incorporarlos al conjunto de calibración.
    home_con_elo = home_con_elo[
        ["id_partido", "rating"]
    ].rename(
        columns={"rating": "elo_home"}
    )

    away_con_elo = away_con_elo[
        ["id_partido", "rating"]
    ].rename(
        columns={"rating": "elo_away"}
    )

    # Une los resultados reales con los ratings Elo previos al partido.
    calibracion = partidos.copy()
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

    # Elimina partidos sin información suficiente para estimar el modelo.
    calibracion = calibracion.dropna(
        subset=[
            "elo_home",
            "elo_away",
            "home_score",
            "away_score"
        ]
    )

    # La diferencia Elo representa la diferencia de fuerza relativa entre las dos selecciones antes del partido.
    calibracion["diferencia_elo"] = (
        calibracion["elo_home"] -
        calibracion["elo_away"]
    )

    # Convierte la condición de sede en una variable numérica.
    # localia = 1 indica que el partido no se disputó en sede neutral.
    # localia = 0 indica un encuentro disputado en sede neutral.
    calibracion["localia"] = (
        ~calibracion["neutral"].astype(bool)
    ).astype(int)
    
    return calibracion

# Calcula la log-verosimilitud negativa del modelo Elo-Poisson.
# alpha representa el nivel base de goles esperados.
# beta representa el efecto de la diferencia Elo.
# gamma representa el efecto de jugar como local en partidos no neutrales.
def loglik_negativa(parametros, calibracion):
    alpha, beta, gamma = parametros

    diferencia = calibracion["diferencia_elo"].values
    localia = calibracion["localia"].values
    goles_home = calibracion["home_score"].values
    goles_away = calibracion["away_score"].values

    # El efecto de localía se aplica únicamente al equipo registrado
    # como local cuando el partido no se disputa en sede neutral.
    eta_home = (
        alpha
        + beta * diferencia
        + gamma * localia
    )

    eta_away = (
        alpha
        - beta * diferencia
    )

    # Convierte los predictores lineales en goles esperados.
    # La función exponencial garantiza valores positivos de lambda.
    lambda_home = np.exp(eta_home)
    lambda_away = np.exp(eta_away)

    # Calcula la log-verosimilitud Poisson para los goles observados.
    loglik_home = (
        goles_home * eta_home
        - lambda_home
        - gammaln(goles_home + 1)
    )

    loglik_away = (
        goles_away * eta_away
        - lambda_away
        - gammaln(goles_away + 1)
    )

    loglik_total = (
        loglik_home.sum()
        + loglik_away.sum()
    )

    return -loglik_total

if __name__ == "__main__":
    print("CALIBRACIÓN DEL MODELO ELO-POISSON")

    resultados, elo = cargar_datos()

    calibracion = preparar_dataset_calibracion(
        resultados,
        elo
    )

    # Presenta estadísticas descriptivas para verificar las características del conjunto de partidos utilizado durante la calibración.
    print(f"\nPartidos utilizados: {len(calibracion):,}")
    print(
    f"Partidos neutrales: "
    f"{calibracion['neutral'].sum():,}"
)
    
    print(
        f"Partidos no neutrales: "
        f"{(~calibracion['neutral']).sum():,}"
    )
    
    print(f"Promedio goles local: "
        f"{calibracion['home_score'].mean():.4f}")

    print(f"Promedio goles visitante: "
        f"{calibracion['away_score'].mean():.4f}")

    goles_totales = (
        calibracion["home_score"] +
        calibracion["away_score"]
    ).mean()

    print(
        f"Promedio goles totales: "
        f"{goles_totales:.4f}"
    )

    # alpha controla el nivel base de goles esperados.
    # beta controla la influencia de la diferencia Elo sobre lambda.
    # Estos valores funcionan únicamente como punto inicial del proceso de optimización y no corresponden a los parámetros finales.
    parametros_iniciales = [
        np.log(1.3),
        0.001,
        0.1
    ]

    # Estima alpha, beta y gamma mediante máxima verosimilitud.
    # Los límites mantienen la búsqueda dentro de valores numéricamente
    # estables y coherentes para los parámetros del modelo.    
    resultado = minimize(
        loglik_negativa,
        parametros_iniciales,
        args=(calibracion,),
        method="L-BFGS-B",
        bounds=[
            (-2.0, 2.0),
            (-0.01, 0.01),
            (-1.0, 1.0)
        ]
    )
    if not resultado.success:
        raise RuntimeError(
            "La calibración Poisson no convergió."
        )

    alpha, beta, gamma = resultado.x

    print("\nPARÁMETROS ESTIMADOS")
    print(f"alpha = {alpha:.8f}")
    print(f"beta = {beta:.8f}")
    print(f"gamma = {gamma:.8f}")
    print(f"exp(alpha) = {np.exp(alpha):.4f}")
    print(f"exp(gamma) = {np.exp(gamma):.4f}")

    # Cuando la diferencia Elo es cero y el partido se disputa en sede neutral,
    # lambda = exp(alpha). Por lo tanto, exp(alpha) representa los goles esperados
    # por equipo entre dos selecciones con el mismo rating Elo en sede neutral.
    print("\nINTERPRETACIÓN")

    print(
        "exp(alpha) representa los goles esperados por equipo cuando ambos tienen el mismo Elo en sede neutral.")
    print("beta representa el efecto de la diferencia Elo sobre la intensidad esperada de goles.")
    print("gamma representa el efecto de localía en partidos que no se disputan en sede neutral.")

    # Evalúa un partido del Mundial en sede neutral.
    # Al no existir localía, el término gamma no interviene.
    elo_cv = 1578
    elo_esp = 2157
    
    diferencia = elo_cv - elo_esp
    
    lambda_cv = np.exp(
        alpha + beta * diferencia
    )
    
    lambda_esp = np.exp(
        alpha - beta * diferencia
    )
    
    print("\nEJEMPLO: CABO VERDE VS ESPAÑA")
    print("Sede neutral: Sí")
    print(f"Diferencia Elo: {diferencia}")
    print(f"Lambda Cabo Verde: {lambda_cv:.4f}")
    print(f"Lambda España: {lambda_esp:.4f}")

    # Los valores lambda representan goles esperados, no probabilidades de victoria, empate o derrota. Las probabilidades de resultado
    # se obtienen posteriormente a partir de las distribuciones Poisson mediante la distribución de Skellam.