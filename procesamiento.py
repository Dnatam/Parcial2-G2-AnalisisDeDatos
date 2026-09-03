import math
import os
import pandas as pd

print("=" * 70)
print("PROCESAMIENTO DÍA 3 - PROYECTO 1: ANÁLISIS Y CIENCIA DE DATOS")
print("=" * 70)

# ==============================================================================
# PARTE 1: CHELSEA - TABLA POR TEMPORADA Y RESUMEN HISTÓRICO
# ==============================================================================
ruta_chelsea = "2.2.Chelsea/Data/csv"
ruta_salida_chelsea = "2.2.Chelsea/Data/chelsea_resumen.csv"

print("\n[1/2] Leyendo 31 temporadas de Premier League...")

resumen_temporadas = []

if os.path.exists(ruta_chelsea):
    archivos_csv = sorted([f for f in os.listdir(ruta_chelsea) if f.endswith(".csv")])

    for csv in archivos_csv:
        temporada = csv.replace(".csv", "")
        path = os.path.join(ruta_chelsea, csv)

        try:
            try:
                df = pd.read_csv(path, encoding="utf-8", on_bad_lines="skip")
            except UnicodeDecodeError:
                df = pd.read_csv(path, encoding="latin1", on_bad_lines="skip")

            # Construir tabla por equipo con PJ, GF, GC y Puntos
            equipos = {}

            for _, row in df.iterrows():
                local = str(row["HomeTeam"]).strip()
                visita = str(row["AwayTeam"]).strip()

                try:
                    fthg = int(row["FTHG"])
                    ftag = int(row["FTAG"])
                except (ValueError, TypeError):
                    continue

                ftr = str(row["FTR"]).strip()

                if local not in equipos:
                    equipos[local] = {"PJ": 0, "GF": 0, "GC": 0, "Pts": 0}
                if visita not in equipos:
                    equipos[visita] = {"PJ": 0, "GF": 0, "GC": 0, "Pts": 0}

                # Acumular PJ, GF, GC
                equipos[local]["PJ"] += 1
                equipos[visita]["PJ"] += 1
                equipos[local]["GF"] += fthg
                equipos[visita]["GF"] += ftag
                equipos[local]["GC"] += ftag
                equipos[visita]["GC"] += fthg

                # Acumular Puntos (3 victoria, 1 empate)
                if ftr == "H" or fthg > ftag:
                    equipos[local]["Pts"] += 3
                elif ftr == "A" or ftag > fthg:
                    equipos[visita]["Pts"] += 3
                elif ftr == "D" or fthg == ftag:
                    equipos[local]["Pts"] += 1
                    equipos[visita]["Pts"] += 1

            df_tabla = pd.DataFrame.from_dict(equipos, orient="index")
            df_tabla["DIF"] = df_tabla["GF"] - df_tabla["GC"]

            # Identificar Campeón (Más Pts, desempaña DIF y GF)
            df_campeon = df_tabla.sort_values(
                by=["Pts", "DIF", "GF"], ascending=False
            )
            campeon = df_campeon.index[0]
            gc_campeon = df_campeon.iloc[0]["GC"]

            # Identificar Mejor Defensa (Menos GC)
            df_defensa = df_tabla.sort_values(by=["GC", "Pts"], ascending=[True, False])
            mejor_defensa = df_defensa.index[0]
            gc_mejor_defensa = df_defensa.iloc[0]["GC"]

            resumen_temporadas.append(
                {
                    "temporada": temporada,
                    "campeon": campeon,
                    "gc_campeon": gc_campeon,
                    "mejor_defensa": mejor_defensa,
                    "gc_mejor_defensa": gc_mejor_defensa,
                }
            )

        except Exception as e:
            print(f"   ❌ Error procesando {csv}: {e}")

    # Guardar CSV Resumen
    df_resumen = pd.DataFrame(resumen_temporadas)
    df_resumen.to_csv(ruta_salida_chelsea, index=False, encoding="utf-8-sig")
    print(f"   ✅ Resumen de {len(df_resumen)} temporadas generado:")
    print(f"      📍 Guardado en: {ruta_salida_chelsea}")

# ==============================================================================
# PARTE 2: CABO VERDE - TABLA ELO LIMPIA Y MODELO PROBABILÍSTICO
# ==============================================================================
ruta_elo = "2.4.Cabo Verde/Data/elo rating mundial 2026.csv"
ruta_salida_elo = "2.4.Cabo Verde/Data/elo_limpio.csv"

print("\n" + "-" * 70)
print("[2/2] Limpiando nombres de Elo y definiendo modelo...")

equipos_requeridos = {
    "Cabo Verde": "Cabo Verde",
    "Uruguay": "Uruguay",
    "España": "Espania",
    "Arabia Saudita": "Arabia Saudita",
    "Egipto": "Egipto",
    "Suiza": "Suiza",
    "Inglaterra": "Inglaterra",
    "Argentina": "Argentina",
    "Camerún": "Camerun",
    "Angola": "Angola",
    "Libia": "Libia",
    "Esuatini": "Esuatini",
    "Mauricio": "Mauricio",
}

if os.path.exists(ruta_elo):
    df_elo_raw = pd.read_csv(ruta_elo, sep=";", encoding="utf-8-sig")
    col_eq = df_elo_raw.columns[0]
    col_elo = df_elo_raw.columns[1]

    filas_limpias = []
    for std_name, csv_name in equipos_requeridos.items():
        match = df_elo_raw[
            df_elo_raw[col_eq].astype(str).str.contains(csv_name, case=False, na=False)
        ]
        if not match.empty:
            rating = int(match[col_elo].values[0])
            conf = (
                match[df_elo_raw.columns[2]].values[0]
                if len(df_elo_raw.columns) > 2
                else "N/A"
            )
            filas_limpias.append(
                {"equipo": std_name, "elo_rating": rating, "confederacion": conf}
            )

    df_elo_limpio = pd.DataFrame(filas_limpias)
    df_elo_limpio.to_csv(ruta_salida_elo, index=False, encoding="utf-8-sig")
    print(f"   ✅ Tabla Elo limpia guardada en: {ruta_salida_elo}")


# --- METODOLOGÍA MODELO ELO ---
def calcular_probabilidades_elo(elo_a, elo_b, k_empate=0.28):
    diff = elo_a - elo_b
    e_a = 1 / (1 + 10 ** (-diff / 400))
    p_empate = math.exp(-((diff / 400) ** 2)) * k_empate
    p_gana_a = e_a - (p_empate / 2)
    p_gana_b = (1 - e_a) - (p_empate / 2)

    total = p_gana_a + p_empate + p_gana_b
    return {
        "Victoria_A": round(p_gana_a / total, 4),
        "Empate": round(p_empate / total, 4),
        "Victoria_B": round(p_gana_b / total, 4),
    }


# Probar modelo con enfrentamientos
print("\n--- PRUEBA DE ENFRENTAMIENTOS MODELO ELO ---")
dict_elo = dict(zip(df_elo_limpio["equipo"], df_elo_limpio["elo_rating"]))

enfrentamientos = [
    ("Cabo Verde", "Camerún"),
    ("Cabo Verde", "España"),
    ("Inglaterra", "Egipto"),
]

for eq1, eq2 in enfrentamientos:
    elo1, elo2 = dict_elo[eq1], dict_elo[eq2]
    probs = calcular_probabilidades_elo(elo1, elo2)
    print(
        f"\n⚽ {eq1} ({elo1}) vs {eq2} ({elo2}):"
        f"\n   • Gana {eq1}: {probs['Victoria_A']*100:.2f}%"
        f"\n   • Empate: {probs['Empate']*100:.2f}%"
        f"\n   • Gana {eq2}: {probs['Victoria_B']*100:.2f}%"
    )

print("\n" + "=" * 70)