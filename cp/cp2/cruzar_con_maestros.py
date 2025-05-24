import pandas as pd
import re
import os # Necesario para el nuevo script

# --- Configuración de Archivos ---
SCRAPED_CLEAN_FILE = 'datos_scraped_limpios_corregidos_con_id_cp.csv' 
PROVINCIAS_MASTER_FILE = 'provincias.csv'
DEPTOS_MASTER_FILE = 'deptos.csv'
LOCA_MASTER_FILE = 'loca.csv'

# Nombres para los archivos de salida
MATCHED_OUTPUT_FILE = 'tabla_final_cruces_exitosos.csv'
UNMATCHED_OUTPUT_FILE = 'scraped_cp_sin_match_en_maestro.csv'

def normalize_name(name):
    if pd.isna(name): return ""
    name_str = str(name).lower().strip()
    name_str = re.sub(r'\s*\(.*\)\s*', '', name_str).strip()
    name_str = re.sub(r'\s+', ' ', name_str).strip()
    return name_str

print("Iniciando el proceso de cruce final con datos maestros (v3, salidas separadas)...")

try:
    print(f"\nCargando datos scrapeados y limpios: '{SCRAPED_CLEAN_FILE}'...")
    df_scraped = pd.read_csv(SCRAPED_CLEAN_FILE, delimiter=';', dtype=str, encoding='utf-8')
    print(f"  Filas cargadas de datos scrapeados: {len(df_scraped)}")
    if df_scraped.empty:
        print("El archivo de datos scrapeados y limpios está vacío.")
        exit()
    # Se espera que df_scraped tenga: 'nom_prov', 'nom_loca', 'cp', 'cpa' (y 'id_cp_fuente' si se incluyó)
    # Renombramos las columnas de df_scraped que se usarán para el cruce para evitar sufijos de Pandas
    df_scraped.rename(columns={'nom_prov': 'scraped_nom_prov_norm', 
                               'nom_loca': 'scraped_nom_loca_norm'}, inplace=True)

    print(f"\nCargando archivo maestro de provincias: '{PROVINCIAS_MASTER_FILE}'...")
    df_provincias_master = pd.read_csv(PROVINCIAS_MASTER_FILE, delimiter=',', header=0, dtype=str)
    df_provincias_master.rename(columns={'id_prov': 'master_id_prov', 'nom_prov': 'master_nom_prov'}, inplace=True)
    df_provincias_master['master_id_prov'] = pd.to_numeric(df_provincias_master['master_id_prov'], errors='coerce').astype('Int64')
    df_provincias_master['master_nom_prov_norm'] = df_provincias_master['master_nom_prov'].apply(normalize_name)
    df_provincias_master.dropna(subset=['master_id_prov', 'master_nom_prov_norm'], inplace=True)

    print(f"\nCargando archivo maestro de departamentos: '{DEPTOS_MASTER_FILE}'...")
    df_deptos_master = pd.read_csv(DEPTOS_MASTER_FILE, delimiter=',', header=0, dtype=str)
    df_deptos_master.rename(columns={'id_depto': 'master_id_depto', 'id_prov': 'master_id_prov', 'nom_depto': 'master_nom_depto'}, inplace=True)
    df_deptos_master['master_id_depto'] = pd.to_numeric(df_deptos_master['master_id_depto'], errors='coerce').astype('Int64')
    df_deptos_master['master_id_prov'] = pd.to_numeric(df_deptos_master['master_id_prov'], errors='coerce').astype('Int64')
    df_deptos_master.dropna(subset=['master_id_depto', 'master_id_prov'], inplace=True)

    print(f"\nCargando archivo maestro de localidades: '{LOCA_MASTER_FILE}'...")
    df_loca_master = pd.read_csv(LOCA_MASTER_FILE, delimiter=',', header=0, dtype=str)
    df_loca_master = df_loca_master[['id_loca', 'id_depto', 'nom_loca']]
    df_loca_master.rename(columns={'id_loca': 'master_id_loca', 'id_depto': 'master_id_depto', 'nom_loca': 'master_nom_loca'}, inplace=True)
    df_loca_master['master_id_loca'] = pd.to_numeric(df_loca_master['master_id_loca'], errors='coerce').astype('Int64')
    df_loca_master['master_id_depto'] = pd.to_numeric(df_loca_master['master_id_depto'], errors='coerce').astype('Int64')
    df_loca_master['master_nom_loca_norm'] = df_loca_master['master_nom_loca'].apply(normalize_name)
    df_loca_master.dropna(subset=['master_id_loca', 'master_id_depto', 'master_nom_loca_norm'], inplace=True)

    print("\nConstruyendo DataFrame maestro P-D-L...")
    df_master_pd = pd.merge(df_provincias_master, df_deptos_master, on='master_id_prov', how='inner')
    df_master_pdl = pd.merge(df_master_pd, df_loca_master, on='master_id_depto', how='inner')
    print(f"  DataFrame maestro P-D-L construido. Filas: {len(df_master_pdl)}")
    
    print("\nCruzando datos scrapeados limpios con el DataFrame maestro P-D-L...")
    # indicator=True nos dirá qué filas tuvieron match
    df_merged_all = pd.merge(
        df_scraped,
        df_master_pdl,
        left_on=['scraped_nom_prov_norm', 'scraped_nom_loca_norm'],
        right_on=['master_nom_prov_norm', 'master_nom_loca_norm'],
        how='left', # Mantener todos los datos scrapeados
        indicator=True # Añade una columna '_merge' que indica si el match fue 'left_only', 'right_only', or 'both'
    )
    print(f"  Filas totales después del cruce (antes de separar): {len(df_merged_all)}")

    # --- Separar Matched y Unmatched ---
    df_matched = df_merged_all[df_merged_all['_merge'] == 'both'].copy()
    df_unmatched = df_merged_all[df_merged_all['_merge'] == 'left_only'].copy()
    
    print(f"\nFilas con match encontradas: {len(df_matched)}")
    print(f"Filas sin match (solo en datos scrapeados): {len(df_unmatched)}")

    # --- Procesar y Guardar Filas CON MATCH ---
    if not df_matched.empty:
        df_output_matched = pd.DataFrame()
        df_output_matched['id_prov'] = df_matched['master_id_prov']
        df_output_matched['nom_prov'] = df_matched['master_nom_prov']
        df_output_matched['id_depto'] = df_matched['master_id_depto']
        df_output_matched['nom_depto'] = df_matched['master_nom_depto']
        df_output_matched['id_loca'] = df_matched['master_id_loca']
        df_output_matched['nom_loca'] = df_matched['master_nom_loca']
        df_output_matched['cp'] = df_matched['cp']
        df_output_matched['cpa'] = df_matched['cpa']
        if 'id_cp_fuente' in df_matched.columns:
             df_output_matched['id_cp_fuente'] = df_matched['id_cp_fuente']

        print(f"\nPrevisualización del archivo de cruces exitosos (primeras 5 filas):")
        print(df_output_matched.head())
        df_output_matched.to_csv(MATCHED_OUTPUT_FILE, index=False, sep=';', encoding='utf-8')
        print(f"  Archivo de cruces exitosos guardado en: '{MATCHED_OUTPUT_FILE}'")
        print(f"  Columnas: {df_output_matched.columns.tolist()}")
    else:
        print("No se encontraron cruces exitosos para guardar.")

    # --- Procesar y Guardar Filas SIN MATCH ---
    if not df_unmatched.empty:
        # Para las no coincidentes, queremos las columnas scrapeadas originales (ya renombradas con _scraped_norm)
        # y su cp/cpa.
        cols_for_unmatched_output = ['scraped_nom_prov_norm', 'scraped_nom_loca_norm', 'cp', 'cpa']
        if 'id_cp_fuente' in df_unmatched.columns: # si esta columna existe en el df_scraped
            cols_for_unmatched_output.append('id_cp_fuente')
        
        # Asegurarse de que las columnas existan antes de seleccionarlas
        actual_cols_for_unmatched = [col for col in cols_for_unmatched_output if col in df_unmatched.columns]
        df_output_unmatched = df_unmatched[actual_cols_for_unmatched].copy()
        
        # Renombrar para más claridad en el archivo de no-matches
        df_output_unmatched.rename(columns={
            'scraped_nom_prov_norm': 'nom_prov_scraped_no_match',
            'scraped_nom_loca_norm': 'nom_loca_scraped_no_match',
            # cp y cpa ya tienen nombres simples
        }, inplace=True)

        print(f"\nPrevisualización del archivo de CP scrapeados sin match en maestros (primeras 5 filas):")
        print(df_output_unmatched.head())
        df_output_unmatched.to_csv(UNMATCHED_OUTPUT_FILE, index=False, sep=';', encoding='utf-8')
        print(f"  Archivo de CP scrapeados sin match guardado en: '{UNMATCHED_OUTPUT_FILE}'")
        print(f"  Columnas: {df_output_unmatched.columns.tolist()}")
    else:
        print("No se encontraron datos scrapeados sin match para guardar.")

    print(f"\n¡Proceso de cruce final completado!")

except FileNotFoundError as e:
    print(f"\nERROR CRÍTICO: No se encontró el archivo: {e.filename}")
    print("Asegúrate de que todos los archivos CSV de entrada estén en la misma carpeta que este script, o ajusta las rutas.")
except pd.errors.EmptyDataError as e:
    print(f"\nERROR CRÍTICO: Uno de los archivos CSV está vacío o mal formateado: {e}")
except KeyError as e:
    print(f"\nERROR CRÍTICO: Una columna esperada no se encontró. Verifica los encabezados de tus CSVs: {e}")
except Exception as e:
    print(f"\nOcurrió un error inesperado durante el proceso: {e}")
    import traceback
    traceback.print_exc()