import pandas as pd
import re # Para expresiones regulares (limpieza de nombres)

# --- Configuración de Nombres de Archivo ---
# Modifica estos nombres si tus archivos se llaman diferente o están en otra carpeta.
PROVINCIAS_FILE = 'provincias.csv'
DEPTOS_FILE = 'deptos.csv'
LOCA_FILE = 'loca.csv'
LOCALIDADES_CP_FILE = 'localidades.csv' # Este es el archivo que ya tenías con CP

OUTPUT_FILE = 'datos_consolidados_final_diagnostico.csv' # Cambiado para indicar que es para diagnóstico

# --- Función Auxiliar para Limpiar Nombres de Localidad ---
def clean_locality_name(name):
    if pd.isna(name): # Manejar valores nulos
        return ""
    name = str(name).lower().strip()
    # Eliminar contenido entre paréntesis y los paréntesis mismos
    name = re.sub(r'\s*\(.*\)\s*', '', name).strip()
    # Opcional: para una limpieza más profunda, se podría usar unidecode para quitar tildes
    # from unidecode import unidecode
    # name = unidecode(name)
    name = re.sub(r'\s+', ' ', name).strip() # Normalizar múltiples espacios a uno solo
    return name

print("Iniciando el proceso de consolidación de 4 archivos (con diagnóstico de id_prov de CP)...")

try:
    # --- 1. Cargar provincias.csv ---
    print(f"\nCargando '{PROVINCIAS_FILE}'...")
    df_provincias = pd.read_csv(PROVINCIAS_FILE, delimiter=',', header=0, dtype=str)
    df_provincias.rename(columns={'id_prov': 'id_prov_val', 'nom_prov': 'nom_prov_val'}, inplace=True)
    df_provincias['id_prov_val'] = pd.to_numeric(df_provincias['id_prov_val'], errors='coerce')
    df_provincias.dropna(subset=['id_prov_val'], inplace=True)
    df_provincias['id_prov_val'] = df_provincias['id_prov_val'].astype(int)
    print(f"  '{PROVINCIAS_FILE}' cargado: {len(df_provincias)} filas. Columnas: {df_provincias.columns.tolist()}")
    print(df_provincias.head(2))

    # --- 2. Cargar deptos.csv ---
    print(f"\nCargando '{DEPTOS_FILE}'...")
    df_deptos = pd.read_csv(DEPTOS_FILE, delimiter=',', header=0, dtype=str)
    df_deptos.rename(columns={'id_depto': 'id_depto_val', 'id_prov': 'id_prov_val', 'nom_depto': 'nom_depto_val'}, inplace=True)
    df_deptos['id_depto_val'] = pd.to_numeric(df_deptos['id_depto_val'], errors='coerce')
    df_deptos['id_prov_val'] = pd.to_numeric(df_deptos['id_prov_val'], errors='coerce')
    df_deptos.dropna(subset=['id_depto_val', 'id_prov_val'], inplace=True)
    df_deptos['id_depto_val'] = df_deptos['id_depto_val'].astype(int)
    df_deptos['id_prov_val'] = df_deptos['id_prov_val'].astype(int)
    print(f"  '{DEPTOS_FILE}' cargado: {len(df_deptos)} filas. Columnas: {df_deptos.columns.tolist()}")
    print(df_deptos.head(2))

    # --- 3. Cargar loca.csv ---
    print(f"\nCargando '{LOCA_FILE}'...")
    df_loca = pd.read_csv(LOCA_FILE, delimiter=',', header=0, dtype=str)
    df_loca = df_loca[['id_loca', 'id_depto', 'nom_loca']] # Seleccionar solo las columnas necesarias
    df_loca.rename(columns={'id_loca': 'id_loca_val', 'id_depto': 'id_depto_val', 'nom_loca': 'nom_loca_pdl_original'}, inplace=True)
    df_loca['id_loca_val'] = pd.to_numeric(df_loca['id_loca_val'], errors='coerce')
    df_loca['id_depto_val'] = pd.to_numeric(df_loca['id_depto_val'], errors='coerce')
    df_loca.dropna(subset=['id_loca_val', 'id_depto_val'], inplace=True)
    df_loca['id_loca_val'] = df_loca['id_loca_val'].astype(int)
    df_loca['id_depto_val'] = df_loca['id_depto_val'].astype(int)
    print(f"  '{LOCA_FILE}' cargado: {len(df_loca)} filas. Columnas: {df_loca.columns.tolist()}")
    print(df_loca.head(2))

    # --- 4. Cargar localidades.csv (fuente de CP) ---
    print(f"\nCargando '{LOCALIDADES_CP_FILE}'...")
    df_cp_source = pd.read_csv(LOCALIDADES_CP_FILE, delimiter=';', header=0, dtype=str)
    # Renombramos y CONSERVAMOS id_prov de este archivo para diagnóstico
    df_cp_source.rename(columns={
        'id_cp': 'id_cp_val_source',
        'cp': 'cp_val_source',
        'nom_loca': 'nom_loca_cp_original',
        'idProvincia': 'id_prov_cp_source_original' # Columna original de id_prov de localidades.csv
    }, inplace=True)
    
    # Intentamos convertir id_prov_cp_source_original a numérico para facilitar comparaciones
    df_cp_source['id_prov_cp_source_numeric'] = pd.to_numeric(df_cp_source['id_prov_cp_source_original'], errors='coerce')
    # No eliminamos filas si id_prov_cp_source_numeric es NaN aquí, ya que solo es para diagnóstico y la fila aún puede ser útil por su CP.
    print(f"  '{LOCALIDADES_CP_FILE}' cargado: {len(df_cp_source)} filas. Columnas: {df_cp_source.columns.tolist()}")
    print(df_cp_source.head(2))

    # --- Consolidación Parte 1: Provincias, Departamentos, Localidades (de loca.csv) ---
    print("\nRealizando merge: Provincias -> Departamentos...")
    df_prov_depto = pd.merge(df_provincias, df_deptos, on='id_prov_val', how='inner')
    print(f"  Resultado Provincias+Departamentos: {len(df_prov_depto)} filas.")
    print(df_prov_depto.head(2))

    print("\nRealizando merge: (Provincias+Departamentos) -> Localidades (de loca.csv)...")
    df_pdl = pd.merge(df_prov_depto, df_loca, on='id_depto_val', how='inner')
    print(f"  Resultado P-D-L (base): {len(df_pdl)} filas. Columnas: {df_pdl.columns.tolist()}")
    print(df_pdl[['nom_prov_val', 'nom_depto_val', 'nom_loca_pdl_original']].head(2))

    # --- Consolidación Parte 2: Preparar nombres y Unir con datos de CP ---
    print("\nLimpiando nombres de localidad para el cruce...")
    df_pdl['nom_loca_cleaned_pdl'] = df_pdl['nom_loca_pdl_original'].apply(clean_locality_name)
    df_cp_source['nom_loca_cleaned_cp'] = df_cp_source['nom_loca_cp_original'].apply(clean_locality_name)

    print("  Ejemplos de nombres limpios de P-D-L (original de loca.csv):")
    print(df_pdl[['nom_loca_pdl_original', 'nom_loca_cleaned_pdl']].head(3))
    print("  Ejemplos de nombres limpios de la fuente de CP (localidades.csv):")
    print(df_cp_source[['nom_loca_cp_original', 'nom_loca_cleaned_cp', 'id_prov_cp_source_original']].head(3))
    
    print("\nRealizando merge: P-D-L -> Fuente de CP (sobre nombres de localidad limpios)...")
    df_final_merged = pd.merge(
        df_pdl,
        df_cp_source[['nom_loca_cleaned_cp', 'id_cp_val_source', 'cp_val_source', 'id_prov_cp_source_original', 'id_prov_cp_source_numeric']], # Traer las columnas de id_prov de la fuente de CP
        left_on='nom_loca_cleaned_pdl',
        right_on='nom_loca_cleaned_cp',
        how='left'
    )
    print(f"  Resultado del merge final: {len(df_final_merged)} filas.")
    print(df_final_merged.head())

    # --- Preparar Archivo de Salida ---
    df_output = df_final_merged.rename(columns={
        'id_prov_val': 'id_prov',
        'nom_prov_val': 'nom_prov',
        'id_depto_val': 'id_depto',
        'nom_depto_val': 'nom_depto',
        'id_loca_val': 'id_loca',
        'nom_loca_pdl_original': 'nom_loca', 
        'id_cp_val_source': 'id_cp',
        'cp_val_source': 'cp',
        'id_prov_cp_source_original': 'cp_id_prov_csv_original', # id_prov original del archivo localidades.csv
        'id_prov_cp_source_numeric': 'cp_id_prov_csv_num'       # id_prov numérico del archivo localidades.csv
    })

    # Seleccionar y ordenar las columnas finales
    columnas_final_deseadas = ['id_prov', 'nom_prov', 'id_depto', 'nom_depto', 'id_loca', 'nom_loca', 'id_cp', 'cp', 'cp_id_prov_csv_original', 'cp_id_prov_csv_num']
    
    # Asegurarse de que todas las columnas deseadas existan en df_output
    # Especialmente las que vienen del merge (id_cp, cp, y las de diagnóstico de id_prov del CP)
    for col in columnas_final_deseadas:
        if col not in df_output.columns:
            df_output[col] = pd.NA # Añadir como vacía si no existe (ej. si ningun CP coincidió)
            
    df_output = df_output[columnas_final_deseadas]

    print(f"\nPrevisualización de los datos finales (primeras 5 filas):")
    print(df_output.head())

    cp_no_encontrados = df_output['cp'].isnull().sum()
    print(f"\nNúmero total de filas en el archivo de salida: {len(df_output)}")
    print(f"Número de filas SIN código postal asignado: {cp_no_encontrados}")

    # Guardar el resultado
    df_output.to_csv(OUTPUT_FILE, index=False, sep=';', encoding='utf-8')
    print(f"\n¡Proceso completado! Los datos consolidados se han guardado en: '{OUTPUT_FILE}'")

except FileNotFoundError as e:
    print(f"\nERROR CRÍTICO: No se encontró el archivo: {e.filename}")
    print("Por favor, verifica que los nombres y rutas de los archivos CSV (definidos al inicio del script) sean correctos.")
except pd.errors.EmptyDataError as e:
    print(f"\nERROR CRÍTICO: Uno de los archivos CSV está vacío o mal formateado: {e}")
except KeyError as e:
    print(f"\nERROR CRÍTICO: Una columna esperada no se encontró en un CSV. Verifica los encabezados: {e}. Columnas actuales: {e.args[0] if e.args else ''}")
except Exception as e:
    print(f"\nOcurrió un error inesperado durante el proceso: {e}")
    import traceback
    traceback.print_exc()