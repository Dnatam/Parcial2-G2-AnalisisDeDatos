import os
import pandas as pd

# Rutas exactas
ruta_chelsea = "2.2.Chelsea/Data/csv"
ruta_elo = "2.4.Cabo Verde/Data/elo rating mundial 2026.csv"

print("=" * 60)
print("AUDITORÍA DÍA 2 - PROYECTO 1: ANÁLISIS Y CIENCIA DE DATOS")
print("=" * 60)

# 1. VALIDACIÓN CHELSEA (Premier League)
columnas_clave = ["HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR"]

print("\n[1/2] Verificando datos de la Premier League...")
if os.path.exists(ruta_chelsea):
    archivos_csv = [f for f in os.listdir(ruta_chelsea) if f.endswith(".csv")]
    print(f"-> Archivos CSV encontrados: {len(archivos_csv)} de 31 esperados.")

    errores_csv = 0
    for csv in archivos_csv:
        path = os.path.join(ruta_chelsea, csv)
        try:
            try:
                df = pd.read_csv(path, encoding="utf-8", on_bad_lines="skip")
            except UnicodeDecodeError:
                df = pd.read_csv(path, encoding="latin1", on_bad_lines="skip")

            faltantes = [col for col in columnas_clave if col not in df.columns]
            if faltantes:
                print(f"   ❌ {csv}: Faltan columnas -> {faltantes}")
                errores_csv += 1
            else:
                print(f"   ✅ {csv}: Correcto ({len(df)} partidos)")
        except Exception as e:
            print(f"   ❌ {csv}: No se pudo abrir -> {e}")
            errores_csv += 1

    if errores_csv == 0 and len(archivos_csv) == 31:
        print("   ✅ ¡Todos los 31 CSVs de Premier League están validados!")
    else:
        print("   ⚠️ Revisa los archivos indicados arriba.")
else:
    print(f"   ❌ No se encontró la ruta '{ruta_chelsea}'.")

# 2. VALIDACIÓN CABO VERDE (Elo)
equipos_totales = {
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

print("\n[2/2] Verificando Rankings Elo de Selecciones...")
if os.path.exists(ruta_elo):
    try:
        df_elo = pd.read_csv(ruta_elo, sep=";", encoding="utf-8-sig")

        col_equipo = df_elo.columns[0]
        col_elo = df_elo.columns[1]

        faltantes = []
        for std_name, csv_name in equipos_totales.items():
            match = df_elo[
                df_elo[col_equipo]
                .astype(str)
                .str.contains(csv_name, case=False, na=False)
            ]
            if not match.empty:
                val = match[col_elo].values[0]
                print(f"   ✅ {std_name} ('{csv_name}'): Detectado -> Elo = {val}")
            else:
                faltantes.append(std_name)

        if not faltantes:
            print(
                "\n   ✅ ¡Todas las 13 selecciones (Mundial + CAF) están validadas y presentes!"
            )
        else:
            print(f"\n   ❌ Aún faltan por agregar estas selecciones: {faltantes}")

    except Exception as e:
        print(f"   ❌ Error al leer el CSV de Elo: {e}")
else:
    print(f"   ❌ No se encontró el archivo de Elo en '{ruta_elo}'.")

print("\n" + "=" * 60)