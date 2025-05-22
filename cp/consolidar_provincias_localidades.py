import pandas as pd

# --- Configuración de Nombres de Archivo ---
PROVINCIAS_FILE = 'provincias.csv'
LOCALIDADES_CP_FILE = 'localidades.csv' # Este es el archivo que ya tenías
OUTPUT_FILE = 'provincia_localidad_cp_consolidado.csv'

print(f"Iniciando la consolidación de Provincias, Localidades y CP...")
print(f"Archivo de Provincias: {PROVINCIAS_FILE}")
print(f"Archivo de Localidades y CP: {LOCALIDADES_CP_FILE}")

try:
    # --- 1. Cargar provincias.csv ---
    print(f"\nCargando '{PROVINCIAS_FILE}'...")
    df_provincias = pd.read_csv(
        PROVINCIAS_FILE,
        delimiter=',',
        header=0, # La primera fila es el encabezado
        dtype={'id_prov': str, 'nombre_prov': str} # Leer como string inicialmente
    )
    print("Primeras filas de provincias.csv:")
    print(df_provincias.head())

    # Convertir id_prov a numérico (entero)
    df_provincias['id_prov'] = pd.to_numeric(df_provincias['id_prov'], errors='coerce')
    if df_provincias['id_prov'].isnull().any():
        print("\nADVERTENCIA: Se encontraron valores no numéricos en la columna 'id_prov' de provincias.csv.")
        print("Filas con problemas de ID (serán eliminadas de este DataFrame):")
        print(df_provincias[df_provincias['id_prov'].isnull()])
        df_provincias.dropna(subset=['id_prov'], inplace=True)
    df_provincias['id_prov'] = df_provincias['id_prov'].astype(int)
    print(f"'{PROVINCIAS_FILE}' cargado. Filas: {len(df_provincias)}")

    # --- 2. Cargar localidades.csv ---
    print(f"\nCargando '{LOCALIDADES_CP_FILE}'...")
    # Columnas originales esperadas: id, cp, localidad, idProvincia
    df_localidades = pd.read_csv(
        LOCALIDADES_CP_FILE,
        delimiter=';',
        header=0, # La primera fila es el encabezado
        dtype={ # Leer todo como string inicialmente para manejar diversos formatos de CP y IDs
            'id': str,
            'cp': str,
            'localidad': str,
            'idProvincia': str
        }
    )
    print("Primeras filas de localidades.csv (original):")
    print(df_localidades.head())

    # Renombrar columnas para claridad y consistencia
    df_localidades.rename(columns={
        'id': 'id_localidad_ref',
        'localidad': 'nombre_localidad',
        'idProvincia': 'id_provincia_ref'
        # 'cp' se mantiene como 'cp'
    }, inplace=True)
    print("Primeras filas de localidades.csv (columnas renombradas):")
    print(df_localidades.head())


    # Convertir columnas de ID a numérico (entero)
    id_cols_localidades = ['id_localidad_ref', 'id_provincia_ref']
    for col in id_cols_localidades:
        df_localidades[col] = pd.to_numeric(df_localidades[col], errors='coerce')

    if df_localidades[id_cols_localidades].isnull().any().any():
        print("\nADVERTENCIA: Se encontraron valores no numéricos en las columnas ID de localidades.csv.")
        print("Filas con problemas de ID (serán eliminadas de este DataFrame):")
        print(df_localidades[df_localidades[id_cols_localidades].isnull().any(axis=1)])
        df_localidades.dropna(subset=id_cols_localidades, inplace=True)

    for col in id_cols_localidades:
        df_localidades[col] = df_localidades[col].astype(int)
    print(f"'{LOCALIDADES_CP_FILE}' cargado y procesado. Filas: {len(df_localidades)}")


    # --- 3. Consolidar (Merge) los datos ---
    print("\nRealizando el merge de los datos (localidades con provincias)...")
    # Hacemos un 'left' merge desde df_localidades para mantener todas las localidades
    # y añadirles el nombre de la provincia.
    df_consolidado = pd.merge(
        df_localidades,
        df_provincias,
        left_on='id_provincia_ref', # Columna de ID de provincia en localidades.csv
        right_on='id_prov',         # Columna de ID de provincia en provincias.csv
        how='left'                  # Mantener todas las localidades, agregar nombre de provincia si hay match
    )

    print("Primeras filas del resultado consolidado:")
    print(df_consolidado.head())

    # Verificar cuántas localidades no encontraron un nombre de provincia
    provincias_no_encontradas = df_consolidado['nombre_prov'].isnull().sum()
    if provincias_no_encontradas > 0:
        print(f"\nADVERTENCIA: {provincias_no_encontradas} localidades no encontraron un nombre de provincia correspondiente.")
        # Opcional: mostrar algunas de estas filas
        # print("Ejemplo de localidades sin nombre de provincia encontrado:")
        # print(df_consolidado[df_consolidado['nombre_prov'].isnull()].head())

    # Seleccionar y ordenar las columnas para el archivo final
    # Columnas deseadas: nombre_prov, nombre_localidad, cp
    # También incluiremos los IDs por referencia, puedes eliminarlos si no los necesitas
    columnas_finales = ['id_prov', 'nombre_prov', 'id_localidad_ref', 'nombre_localidad', 'cp', 'id_provincia_ref']
    # Filtrar para que solo existan las columnas que están presentes, por si 'id_prov' no existe (si todas las provincias no encontraron match)
    columnas_finales_existentes = [col for col in columnas_finales if col in df_consolidado.columns]
    df_final = df_consolidado[columnas_finales_existentes]


    print(f"\nTotal de filas en el archivo consolidado: {len(df_final)}")


    # --- 4. Guardar el resultado ---
    df_final.to_csv(OUTPUT_FILE, index=False, sep=';')
    print(f"\n¡Proceso completado! Los datos consolidados se han guardado en: '{OUTPUT_FILE}'")
    print(f"Columnas en el archivo de salida: {df_final.columns.tolist()}")

except FileNotFoundError as e:
    print(f"\nERROR: No se encontró el archivo: {e.filename}")
    print("Por favor, verifica que los nombres y rutas de los archivos CSV sean correctos y estén en la misma carpeta que el script, o modifica las rutas en el script.")
except pd.errors.EmptyDataError as e:
    print(f"\nERROR: Uno de los archivos CSV ({e}) está vacío o no tiene el formato esperado.")
except Exception as e:
    print(f"\nOcurrió un error inesperado durante el proceso: {e}")
    import traceback
    traceback.print_exc() # Imprime el traceback completo para más detalles del error