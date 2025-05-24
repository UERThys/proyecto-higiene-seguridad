import pandas as pd

# --- Configuración de Archivos ---
INPUT_FILE = 'tabla_final_cruces_exitosos.csv' # El resultado del script cruzar_con_maestros_v3.py
OUTPUT_FILE = 'tabla_final_deduplicada_por_id_loca.csv'

print(f"Iniciando proceso de deduplicación para '{INPUT_FILE}'...")

try:
    # --- 1. Cargar el archivo ---
    print(f"Cargando '{INPUT_FILE}'...")
    df = pd.read_csv(INPUT_FILE, delimiter=';', dtype=str, encoding='utf-8')
    print(f"  Filas cargadas: {len(df)}")
    if df.empty:
        print("El archivo de entrada está vacío. No hay nada que procesar.")
        exit()

    print("  Columnas cargadas:", df.columns.tolist())
    print(df.head())

    # --- 2. Preparar datos para la deduplicación ---
    # Asegurarse de que id_loca sea numérico para poder ordenarlo correctamente.
    # También los otros IDs por si acaso, aunque deberían estar bien en este archivo.
    id_columns = ['id_prov', 'id_depto', 'id_loca']
    for col in id_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce') # Coerce pondrá NaT/NaN si no es convertible
        else:
            print(f"ADVERTENCIA: La columna ID '{col}' no se encontró y no se convertirá a numérico.")

    # Verificar si hay NaNs en id_loca después de la conversión, lo que podría afectar la lógica de 'menor id_loca'
    if 'id_loca' in df.columns and df['id_loca'].isnull().any():
        print(f"ADVERTENCIA: Se encontraron {df['id_loca'].isnull().sum()} valores nulos en 'id_loca' después de convertir a numérico.")
        print("  Estos podrían ser de filas donde el cruce no fue completo o hubo un problema de datos.")
        print("  Las filas con id_loca nulo podrían comportarse de manera inesperada en la deduplicación si son parte de un grupo.")
        # Decisión: ¿Eliminar filas con id_loca nulo antes de deduplicar o dejarlas?
        # Por ahora, las dejaremos y el sort las manejará (NaNs suelen ir al final o principio).
        # Si todas las columnas de agrupación son iguales y algunos id_loca son NaN y otros no, se mantendría el primer no-NaN si NaN va al final.
        # Si todos los id_loca en un grupo son NaN, se mantendría el primero de ellos.

    # --- 3. Aplicar criterio de deduplicación ---
    # Columnas que definen un "grupo de duplicados" (todas excepto id_loca)
    # Asegúrate que estos nombres de columna coincidan exactamente con tu CSV
    cols_para_agrupar = ['id_prov', 'nom_prov', 'id_depto', 'nom_depto', 'nom_loca', 'cp', 'cpa']
    
    # Verificar que todas las columnas para agrupar realmente existan en el DataFrame
    missing_group_cols = [col for col in cols_para_agrupar if col not in df.columns]
    if missing_group_cols:
        print(f"ERROR: Faltan las siguientes columnas necesarias para agrupar: {missing_group_cols}")
        print(f"Columnas disponibles: {df.columns.tolist()}")
        exit()

    print(f"\nColumnas usadas para identificar grupos de duplicados: {cols_para_agrupar}")
    print(f"Se conservará la fila con el menor 'id_loca' dentro de cada grupo.")

    # Ordenar: primero por las columnas de agrupación, luego por id_loca (ascendente)
    # Las filas con id_loca NaN se pueden manejar; sort_values las pone al final por defecto (o al principio con na_position='first')
    if 'id_loca' in df.columns:
        print("Ordenando datos para la deduplicación (por id_loca ascendente dentro de los grupos)...")
        df_sorted = df.sort_values(by=cols_para_agrupar + ['id_loca'], ascending=True, na_position='last')
    else:
        print("ADVERTENCIA: 'id_loca' no está presente, no se puede ordenar por ella. Se usará el orden actual dentro de los grupos.")
        df_sorted = df.sort_values(by=cols_para_agrupar, ascending=True, na_position='last')


    # Eliminar duplicados en base a las columnas de agrupación, conservando la primera aparición
    # (que, debido al ordenamiento, será la que tenga el menor id_loca, o la primera si id_loca es NaN o no existe)
    df_deduplicado = df_sorted.drop_duplicates(subset=cols_para_agrupar, keep='first')
    
    num_filas_original = len(df)
    num_filas_deduplicado = len(df_deduplicado)
    print(f"\nFilas antes de la deduplicación específica: {num_filas_original}")
    print(f"Filas después de la deduplicación específica: {num_filas_deduplicado}")
    print(f"Se eliminaron {num_filas_original - num_filas_deduplicado} filas duplicadas según el criterio.")

    # --- 4. Guardar el resultado ---
    # Volver a convertir las columnas ID a string para el CSV si se prefiere, o dejarlas como números (con decimales si eran Int64)
    # Por consistencia con los CSV anteriores, podemos convertir a string, manejando <NA> si son Int64 y tienen nulos.
    for col in id_columns:
        if col in df_deduplicado.columns and pd.api.types.is_integer_dtype(df_deduplicado[col]):
             # Si se usa Int64, .astype(str) puede convertir <NA> a '<NA>'. Para evitarlo si son ints puros:
             # df_deduplicado[col] = df_deduplicado[col].astype(pd.Int64Dtype()).astype(str).replace('<NA>', '')
             # O más simple si no hay NaNs o no importa que se conviertan a string 'nan':
             df_deduplicado[col] = df_deduplicado[col].astype(str).replace('nan', '').replace('<NA>','')


    df_deduplicado.to_csv(OUTPUT_FILE, index=False, sep=';', encoding='utf-8')
    print(f"\n¡Proceso de deduplicación completado! Archivo guardado en: '{OUTPUT_FILE}'")
    print("Columnas finales:", df_deduplicado.columns.tolist())
    print(df_deduplicado.head())

except FileNotFoundError:
    print(f"ERROR CRÍTICO: No se encontró el archivo de entrada '{INPUT_FILE}'.")
    print("Asegúrate de que el archivo exista en la misma carpeta que este script, o ajusta la ruta.")
except pd.errors.EmptyDataError:
    print(f"ERROR CRÍTICO: El archivo de entrada '{INPUT_FILE}' está vacío.")
except KeyError as e:
    print(f"ERROR CRÍTICO: Una columna esperada para la deduplicación no se encontró: {e}. Verifica los encabezados del CSV de entrada.")
except Exception as e:
    print(f"\nOcurrió un error inesperado durante el proceso: {e}")
    import traceback
    traceback.print_exc()