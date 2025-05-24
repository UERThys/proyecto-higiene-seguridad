import pandas as pd

# --- Configuración de Archivos ---
# Este es el archivo que generó 'deduplicar_tabla_final.py'
INPUT_FILE = 'tabla_final_deduplicada_por_id_loca.csv' 
# Nombre para el archivo con los nombres corregidos
OUTPUT_FILE = 'tabla_final_corregida_n.csv'

def corregir_caracter_n(texto):
    if isinstance(texto, str):
        # Reemplazar 'a+-' por 'ñ'
        # Como la función normalize_name ya convirtió todo a minúsculas,
        # solo necesitamos preocuparnos por 'a+-'
        texto_corregido = texto.replace('a+-', 'ñ')
        return texto_corregido
    return texto

print(f"Iniciando corrección de caracteres especiales para '{INPUT_FILE}'...")

try:
    # --- 1. Cargar el archivo ---
    print(f"Cargando '{INPUT_FILE}'...")
    df = pd.read_csv(INPUT_FILE, delimiter=';', dtype=str, encoding='utf-8')
    print(f"  Filas cargadas: {len(df)}")
    if df.empty:
        print("El archivo de entrada está vacío. No hay nada que procesar.")
        exit()

    print("  Columnas cargadas:", df.columns.tolist())
    print("Primeras filas ANTES de la corrección:")
    print(df[['nom_prov', 'nom_loca']].head())


    # --- 2. Aplicar la corrección a las columnas de nombres ---
    # Las columnas relevantes son 'nom_prov' y 'nom_loca'
    if 'nom_prov' in df.columns:
        df['nom_prov'] = df['nom_prov'].apply(corregir_caracter_n)
        print("  Corrección de 'a+-' aplicada a 'nom_prov'.")
    else:
        print("ADVERTENCIA: Columna 'nom_prov' no encontrada.")
        
    if 'nom_loca' in df.columns:
        df['nom_loca'] = df['nom_loca'].apply(corregir_caracter_n)
        print("  Corrección de 'a+-' aplicada a 'nom_loca'.")
    else:
        print("ADVERTENCIA: Columna 'nom_loca' no encontrada.")

    print("\nPrimeras filas DESPUÉS de la corrección (si hubo cambios):")
    print(df[['nom_prov', 'nom_loca']].head()) # Mostrar las mismas columnas para comparar

    # --- 3. Guardar el resultado ---
    df.to_csv(OUTPUT_FILE, index=False, sep=';', encoding='utf-8')
    print(f"\n¡Proceso de corrección completado! Archivo guardado en: '{OUTPUT_FILE}'")
    print(f"Este archivo '{OUTPUT_FILE}' es el que deberías usar para la importación a Django.")

except FileNotFoundError:
    print(f"ERROR CRÍTICO: No se encontró el archivo de entrada '{INPUT_FILE}'.")
    print("Asegúrate de que el archivo exista en la misma carpeta que este script, o ajusta la ruta.")
except pd.errors.EmptyDataError:
    print(f"ERROR CRÍTICO: El archivo de entrada '{INPUT_FILE}' está vacío.")
except KeyError as e:
    print(f"ERROR CRÍTICO: Una columna esperada ('nom_prov' o 'nom_loca') no se encontró: {e}.")
except Exception as e:
    print(f"\nOcurrió un error inesperado durante el proceso: {e}")
    import traceback
    traceback.print_exc()