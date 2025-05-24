import pandas as pd
import re
from unidecode import unidecode

# --- Configuración de Archivos ---
SCRAPED_DATA_FILE = 'todos_los_cp_scraped_combinado.csv' # El resultado del scrapeo completo
PROVINCIAS_REF_FILE = 'provincias.csv' # Tu archivo maestro de provincias
CLEANED_OUTPUT_FILE = 'datos_scraped_limpios_corregidos_con_id_cp.csv' # Nuevo nombre de salida

# --- Función Auxiliar para Normalizar Nombres ---
from unidecode import unidecode # Asegúrate de que esta importación esté al inicio de ambos scripts

def normalize_name(name):
    if pd.isna(name): 
        return ""
    name_str = str(name).lower().strip()
    # Paso 1: Corregir patrones específicos como 'a+-' a 'ñ'
    name_str = name_str.replace('a+-', 'ñ') 
    # Aquí podrías añadir más reemplazos si encuentras otros patrones (ej. para Á, É, etc.)
    
    # Paso 2: Eliminar contenido entre paréntesis
    name_str = re.sub(r'\s*\(.*\)\s*', '', name_str).strip()
    
    # Paso 3: Aplicar unidecode para quitar tildes estándar (ñ -> n, á -> a, etc.)
    name_str = unidecode(name_str) 
    
    # Paso 4: Normalizar múltiples espacios
    name_str = re.sub(r'\s+', ' ', name_str).strip()
    return name_str

print(f"Iniciando limpieza y corrección de '{SCRAPED_DATA_FILE}' (incluyendo id_cp)...")

try:
    # --- 1. Cargar datos ---
    print(f"Cargando datos scrapeados: '{SCRAPED_DATA_FILE}'...")
    # Leer todas las columnas como string inicialmente para evitar problemas de tipo
    df_scraped = pd.read_csv(SCRAPED_DATA_FILE, delimiter=';', dtype=str, encoding='utf-8')
    print(f"  Filas cargadas: {len(df_scraped)}")
    if df_scraped.empty:
        print("El archivo scrapeado está vacío. No hay nada que procesar.")
        exit()

    # Verificar si la columna 'id_cp' (del scrapeo) está presente
    if 'id_cp' not in df_scraped.columns:
        print(f"ADVERTENCIA: La columna 'id_cp' (esperada del scraping) no se encontró en '{SCRAPED_DATA_FILE}'. No se incluirá.")
        # Si esto pasa, el script continuará sin ella, pero es bueno saberlo.

    print(f"Cargando archivo de referencia de provincias: '{PROVINCIAS_REF_FILE}'...")
    df_provincias_ref = pd.read_csv(PROVINCIAS_REF_FILE, delimiter=',', header=0, dtype=str)
    if 'nom_prov' not in df_provincias_ref.columns:
        print(f"ERROR: La columna 'nom_prov' no se encuentra en '{PROVINCIAS_REF_FILE}'. Verifica el encabezado.")
        exit()
        
    official_province_names_normalized = set(df_provincias_ref['nom_prov'].apply(normalize_name))
    print(f"  Nombres de provincia de referencia cargados y normalizados: {len(official_province_names_normalized)}")
    if not official_province_names_normalized:
        print("ERROR: No se pudieron cargar nombres de provincia de referencia. Verifica el archivo.")
        exit()

    # --- 2. Función para determinar Provincia y Localidad corregidas ---
    def determinar_prov_loc_corregidas(row, valid_prov_names_set):
        prov_nav = normalize_name(row['Provincia_Navegacion'])
        col0_val_orig = row['Provincia_Tabla'] 
        col1_val_orig = row['Localidad_Especifica_Tabla']
        
        col0_norm = normalize_name(col0_val_orig)
        col1_norm = normalize_name(col1_val_orig)

        is_col0_a_province = col0_norm in valid_prov_names_set
        is_col1_a_province = col1_norm in valid_prov_names_set

        if is_col0_a_province:
            if col0_norm == prov_nav:
                return pd.Series([col0_val_orig, col1_val_orig, 'A1_Col0_Prov_Coincide_Nav'])
            elif not is_col1_a_province:
                return pd.Series([col0_val_orig, col1_val_orig, 'A2_Col0_Prov_Col1_NoProv'])
            else: 
                return pd.Series([col0_val_orig, col1_val_orig, 'A3_Col0_Prov_Col1_TambienProv_Col0_NoCoincideNav'])
        elif is_col1_a_province:
            if col1_norm == prov_nav:
                 return pd.Series([col1_val_orig, col0_val_orig, 'B1_Col1_Prov_Coincide_Nav_INTERCAMBIADO'])
            else:
                 return pd.Series([col1_val_orig, col0_val_orig, 'B2_Col1_Prov_Col0_NoProv_INTERCAMBIADO'])
        else:
            return pd.Series([row['Provincia_Navegacion'], col1_val_orig, 'C_Ninguna_Reconocida_Usando_Nav'])

    print("\nAplicando lógica para corregir/identificar Provincia y Localidad...")
    correcciones = df_scraped.apply(
        lambda row: determinar_prov_loc_corregidas(row, official_province_names_normalized), 
        axis=1
    )
    df_scraped[['Provincia_Corregida', 'Localidad_Corregida', 'Regla_Aplicada']] = correcciones
    
    print("\nConteo de reglas aplicadas para la corrección:")
    print(df_scraped['Regla_Aplicada'].value_counts())

    print("\nPrimeras filas con columnas corregidas:")
    print(df_scraped[['Provincia_Navegacion', 'Provincia_Tabla', 'Localidad_Especifica_Tabla', 'Provincia_Corregida', 'Localidad_Corregida', 'Regla_Aplicada', 'CP_Tabla']].head())

    # --- 3. Limpieza final y selección de columnas ---
    print("\nLimpiando nombres en columnas corregidas...")
    df_scraped['Provincia_Final_Limpia'] = df_scraped['Provincia_Corregida'].apply(normalize_name)
    df_scraped['Localidad_Final_Limpia'] = df_scraped['Localidad_Corregida'].apply(normalize_name)
    
    df_scraped['CP_Final'] = df_scraped['CP_Tabla'].astype(str).str.strip()
    df_scraped['CPA_Final'] = df_scraped['CPA_Tabla'].astype(str).str.strip()
    
    # Conservar la columna 'id_cp' del archivo scrapeado si existe
    # Esta columna 'id_cp' es la que vino de 'id_cp_val_source' en el script de scraping
    columnas_a_mantener = ['Provincia_Final_Limpia', 'Localidad_Final_Limpia', 'CP_Final', 'CPA_Final']
    if 'id_cp' in df_scraped.columns:
        df_scraped['id_cp_original_fuente'] = df_scraped['id_cp'].astype(str).str.strip() # Conservar como string
        columnas_a_mantener.append('id_cp_original_fuente')
        print("  Columna 'id_cp' (original de localidades.csv) se conservará como 'id_cp_original_fuente'.")
    else:
        print("  ADVERTENCIA: La columna 'id_cp' no se encontró en el archivo scrapeado combinado. No se incluirá.")

    df_limpio = df_scraped[columnas_a_mantener].copy()
    
    # Renombrar para el output final deseado
    df_limpio.rename(columns={
        'Provincia_Final_Limpia': 'nom_prov',
        'Localidad_Final_Limpia': 'nom_loca',
        'CP_Final': 'cp',
        'CPA_Final': 'cpa',
        'id_cp_original_fuente': 'id_cp_fuente' # Nuevo nombre para el id_cp original
    }, inplace=True)

    print(f"\nFilas antes de la deduplicación final: {len(df_limpio)}")
    # La deduplicación ahora considerará todas las columnas seleccionadas, incluyendo id_cp_fuente si está presente
    df_deduplicado = df_limpio.drop_duplicates()
    print(f"Filas después de la deduplicación final: {len(df_deduplicado)}")

    # --- 4. Guardar resultado ---
    df_deduplicado.to_csv(CLEANED_OUTPUT_FILE, index=False, sep=';', encoding='utf-8')
    print(f"\n¡Proceso de limpieza completado! Archivo guardado en: '{CLEANED_OUTPUT_FILE}'")
    print("Columnas finales:", df_deduplicado.columns.tolist())
    print(df_deduplicado.head())

except FileNotFoundError as e:
    print(f"\nERROR CRÍTICO: No se encontró el archivo: {e.filename}")
except pd.errors.EmptyDataError as e:
    print(f"\nERROR CRÍTICO: Uno de los archivos CSV está vacío o mal formateado: {e}")
except KeyError as e:
    print(f"\nERROR CRÍTICO: Una columna esperada no se encontró. Verifica los encabezados de tus CSVs (especialmente el combinado): {e}")
except Exception as e:
    print(f"\nOcurrió un error inesperado durante el proceso: {e}")
    import traceback
    traceback.print_exc()