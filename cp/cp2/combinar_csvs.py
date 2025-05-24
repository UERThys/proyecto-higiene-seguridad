import pandas as pd
import os
import glob # Para encontrar archivos que coincidan con un patrón

# Nombre del directorio donde están los CSVs individuales de las provincias
INPUT_DIRECTORY = "datos_por_provincia" 
# Nombre del archivo CSV combinado que se generará
COMBINED_OUTPUT_FILE = "todos_los_cp_scraped_combinado.csv"

def combinar_csvs_de_directorio(directorio_entrada, archivo_salida):
    """
    Lee todos los archivos CSV de un directorio, los combina y guarda el resultado.
    """
    # Patrón para encontrar todos los archivos CSV en el directorio de entrada
    patron_csv = os.path.join(directorio_entrada, "*.csv")
    lista_archivos_csv = glob.glob(patron_csv)

    if not lista_archivos_csv:
        print(f"No se encontraron archivos CSV en el directorio '{directorio_entrada}'.")
        return

    print(f"Se encontraron {len(lista_archivos_csv)} archivos CSV para combinar.")

    lista_de_dataframes = []
    for nombre_archivo in lista_archivos_csv:
        try:
            print(f"  Cargando {nombre_archivo}...")
            # Asumimos que todos los CSVs de provincia se guardaron con delimitador ';' y encoding 'utf-8'
            df_prov = pd.read_csv(nombre_archivo, delimiter=';', dtype=str, encoding='utf-8')
            lista_de_dataframes.append(df_prov)
        except pd.errors.EmptyDataError:
            print(f"  ADVERTENCIA: El archivo {nombre_archivo} está vacío y será omitido.")
        except Exception as e:
            print(f"  ERROR al cargar {nombre_archivo}: {e}")
            
    if not lista_de_dataframes:
        print("No se pudieron cargar datos de ningún archivo CSV.")
        return

    print("\nCombinando DataFrames...")
    df_combinado = pd.concat(lista_de_dataframes, ignore_index=True)
    
    print(f"Total de filas en el DataFrame combinado: {len(df_combinado)}")
    print("Primeras filas del DataFrame combinado:")
    print(df_combinado.head())

    # Opcional: Realizar una deduplicación global aquí si lo deseas,
    # basado en las columnas que definen una entrada única (ej. Prov_Tabla, Loc_Tabla, CP, CPA)
    # print("\nRealizando deduplicación global...")
    # cols_para_deduplicar = ['Provincia_Tabla', 'Localidad_Especifica_Tabla', 'CP_Tabla', 'CPA_Tabla']
    # # Asegurarse que todas las columnas para deduplicar existan
    # cols_existentes_para_deduplicar = [col for col in cols_para_deduplicar if col in df_combinado.columns]
    # if len(cols_existentes_para_deduplicar) == len(cols_para_deduplicar):
    #     df_combinado_deduplicado = df_combinado.drop_duplicates(subset=cols_existentes_para_deduplicar, keep='first')
    #     print(f"Filas después de la deduplicación global: {len(df_combinado_deduplicado)}")
    # else:
    #     print("Faltan columnas necesarias para la deduplicación global, se omite este paso.")
    #     df_combinado_deduplicado = df_combinado # Usar el combinado sin deduplicar globalmente por ahora

    # df_combinado_a_guardar = df_combinado_deduplicado # o df_combinado si no se deduplicó
    df_combinado_a_guardar = df_combinado # Por ahora guardamos sin deduplicación global aquí.

    try:
        df_combinado_a_guardar.to_csv(archivo_salida, index=False, sep=';', encoding='utf-8')
        print(f"\n¡Archivos combinados! Resultado guardado en: '{archivo_salida}'")
    except Exception as e:
        print(f"ERROR al guardar el archivo combinado: {e}")

if __name__ == "__main__":
    combinar_csvs_de_directorio(INPUT_DIRECTORY, COMBINED_OUTPUT_FILE)