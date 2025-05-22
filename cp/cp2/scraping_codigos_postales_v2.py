import requests
from bs4 import BeautifulSoup
import csv
from urllib.parse import urljoin
import time
import os
import re # Para la función clean_locality_name (si la usamos después)

# --- Configuración ---
BASE_URL = "https://codigo-postal.co"
OUTPUT_DIRECTORY = "datos_por_provincia" # Carpeta donde se guardarán los CSVs individuales

REQUEST_TIMEOUT = 20  # Segundos para esperar una respuesta
SLEEP_TIME_PROV = 2   # Segundos de pausa entre provincias
SLEEP_TIME_LOC = 2    # Segundos de pausa entre localidades/CP_pages
MAX_RETRIES = 3       # Máximo de reintentos por URL

# --- Función Auxiliar para Peticiones Web con Reintentos ---
def make_request(url, headers, current_retry=0): # Eliminado retries de los args, usa MAX_RETRIES
    # El print ahora incluye el nombre de la función que llama, para más contexto
    # Se podría añadir un parámetro extra para pasar el nombre de la función llamante
    print(f"    Intentando acceder (intento {current_retry + 1}/{MAX_RETRIES}): {url}")
    try:
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        print(f"    ERROR en intento {current_retry + 1} para {url}: {e}")
        if current_retry < MAX_RETRIES - 1:
            retry_delay = 5 * (current_retry + 1)
            print(f"    Reintentando en {retry_delay} segundos...")
            time.sleep(retry_delay)
            return make_request(url, headers, current_retry + 1) # Pasar current_retry incrementado
        else:
            print(f"    Todos los {MAX_RETRIES} intentos fallaron para {url}.")
            return None

# --- Funciones de Scraping ---
def obtener_provincias():
    url = f"{BASE_URL}/argentina/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"}
    print(f"\nObteniendo lista de provincias desde: {url}")
    
    response = make_request(url, headers)
    if not response:
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    provincias = []
    selector_provincias = "ul.column-list li a" # Selector para los links de provincias
    elementos_provincia = soup.select(selector_provincias)
    print(f"  Provincias: Elementos <a> crudos encontrados: {len(elementos_provincia)}")

    for a in elementos_provincia:
        nombre = a.text.strip()
        enlace_relativo = a.get('href')
        if enlace_relativo:
            enlace_absoluto = urljoin(BASE_URL, enlace_relativo)
            provincias.append((nombre, enlace_absoluto))
    print(f"  >> Provincias: Links válidos (con href) añadidos: {len(provincias)}")
    return provincias

def obtener_localidades(provincia_url, provincia_nombre):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"}
    print(f"  Obteniendo links de localidad para {provincia_nombre} desde: {provincia_url}")
    
    response = make_request(provincia_url, headers)
    if not response:
        return []
        
    soup = BeautifulSoup(response.text, 'html.parser')
    localidades = []
    selector_localidades = "ul.cities li a" # Selector para links de localidades en pág. de provincia
    
    elementos_localidad_crudos = soup.select(selector_localidades)
    print(f"    Localidades en {provincia_nombre}: Elementos <a> crudos encontrados: {len(elementos_localidad_crudos)}")

    valid_links_count = 0
    for a_tag in elementos_localidad_crudos:
        nombre = a_tag.text.strip()
        enlace_relativo = a_tag.get('href')
        if enlace_relativo:
            enlace_absoluto = urljoin(BASE_URL, enlace_relativo)
            localidades.append((nombre, enlace_absoluto))
            valid_links_count += 1
        else:
            tag_text_debug = ' '.join(a_tag.stripped_strings) if a_tag else 'TAG_A_PROBLEMATICO'
            print(f"    ADVERTENCIA: Elemento <a> sin href encontrado en {provincia_nombre}. Texto: '{tag_text_debug}'")
            
    print(f"    >> Localidades en {provincia_nombre}: Links válidos (con href) añadidos: {valid_links_count}")
    return localidades

def obtener_cp_y_cpa_de_tabla(localidad_url_navegada, nombre_provincia_navegada, nombre_localidad_navegada):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"}
    print(f"    Obteniendo CP/CPA para '{nombre_localidad_navegada}' ({nombre_provincia_navegada}) desde: {localidad_url_navegada}")

    response = make_request(localidad_url_navegada, headers)
    if not response:
        print(f"      No se pudo obtener la página de CP para {localidad_url_navegada} después de reintentos.")
        return []
        
    soup = BeautifulSoup(response.text, 'html.parser')
    datos_tabla = []
    tabla = soup.find("table") # Asume que la primera tabla es la correcta
    if not tabla:
        print(f"      No se encontró tabla de CP en {localidad_url_navegada}")
        return []

    rows = tabla.find_all("tr")
    # print(f"      Filas encontradas en tabla de '{nombre_localidad_navegada}': {len(rows)}") # Puede ser muy verboso

    for row in rows[1:]: # Omitir la primera fila (asumimos encabezado)
        cols = row.find_all("td")
        # Estructura esperada de la tabla: Provincia, Localidad, Código Postal, CPA, Código Telefónico
        # Índices:                        0          1          2             3      4
        if len(cols) >= 4: # Necesitamos al menos hasta CPA
            provincia_de_tabla = cols[0].text.strip()
            localidad_de_tabla = cols[1].text.strip()
            cp_de_tabla = cols[2].text.strip()
            cpa_de_tabla = cols[3].text.strip()
            codigo_tel_de_tabla = cols[4].text.strip() if len(cols) >= 5 else ""
            datos_tabla.append((provincia_de_tabla, localidad_de_tabla, cp_de_tabla, cpa_de_tabla, codigo_tel_de_tabla))
        elif len(cols) == 3: # Si solo tenemos Prov, Loc, CP
            provincia_de_tabla = cols[0].text.strip()
            localidad_de_tabla = cols[1].text.strip()
            cp_de_tabla = cols[2].text.strip()
            datos_tabla.append((provincia_de_tabla, localidad_de_tabla, cp_de_tabla, "", "")) # CPA y CodTel vacíos
        # else:
            # print(f"      Advertencia: Fila con <3 columnas en {localidad_url_navegada}")
            
    return datos_tabla

def main():
    print("Iniciando script de scraping v3 (incremental por provincia, con deduplicación y reintentos)...")
    
    if not os.path.exists(OUTPUT_DIRECTORY):
        os.makedirs(OUTPUT_DIRECTORY)
        print(f"Directorio de salida creado: {OUTPUT_DIRECTORY}")

    provincias = obtener_provincias()
    print(f"\nTotal de provincias para chequear/procesar: {len(provincias)}")
    if not provincias:
        print("No se pudieron obtener las provincias. Terminando script.")
        return
    
    # Este set es para deduplicar DENTRO DE UNA MISMA EJECUCIÓN del script.
    # Si el script se detiene y se reinicia, las provincias ya guardadas se saltarán,
    # pero este set se reiniciará. La deduplicación global final se haría al combinar los CSVs.
    seen_data_tuples_this_run = set() 
    
    print("\n--- Iniciando extracción completa por provincia ---")
    for provincia_iter_nombre, provincia_iter_url in provincias:
        
        nombre_archivo_provincia_limpio = re.sub(r'[^\w\.-]', '_', provincia_iter_nombre) # Nombre más seguro para archivo
        nombre_archivo_provincia = f"cp_{nombre_archivo_provincia_limpio}.csv"
        ruta_archivo_provincia = os.path.join(OUTPUT_DIRECTORY, nombre_archivo_provincia)

        if os.path.exists(ruta_archivo_provincia):
            print(f"\nArchivo {ruta_archivo_provincia} ya existe. Saltando provincia: {provincia_iter_nombre}.")
            continue

        print(f"\nProcesando Provincia: {provincia_iter_nombre} ({provincia_iter_url})")
        print(f"  Guardará en: {ruta_archivo_provincia}")
        time.sleep(SLEEP_TIME_PROV) 
        
        localidades_nav = obtener_localidades(provincia_iter_url, provincia_iter_nombre)
        
        datos_para_esta_provincia = []
        if not localidades_nav:
            print(f"  --> No se encontraron links de localidad válidos para {provincia_iter_nombre} en su página de provincia.")
            # Opcional: Si quieres crear un archivo CSV incluso para provincias sin localidades encontradas:
            # with open(ruta_archivo_provincia, mode='w', newline='', encoding='utf-8') as file:
            #     writer = csv.writer(file, delimiter=';')
            #     writer.writerow(["Provincia_Navegacion", "Localidad_Agrupadora_Link", "Provincia_Tabla", "Localidad_Especifica_Tabla", "CP_Tabla", "CPA_Tabla", "CodTel_Tabla"])
            #     writer.writerow([provincia_iter_nombre, "NINGUNA_LOC_LINK_ENCONTRADA", "N/A", "N/A", "N/A", "N/A", "N/A"])
            # print(f"    Archivo de placeholder creado para {provincia_iter_nombre}")
            continue 
            
        for localidad_nav_nombre, localidad_nav_url in localidades_nav:
            print(f"    Procesando link de localidad (pág. agrupadora): {localidad_nav_nombre}")
            time.sleep(SLEEP_TIME_LOC) 
            
            filas_de_tabla = obtener_cp_y_cpa_de_tabla(localidad_nav_url, provincia_iter_nombre, localidad_nav_nombre)
            
            if filas_de_tabla:
                count_nuevos_para_esta_loc_nav = 0
                for prov_tabla, loc_tabla, cp_tabla, cpa_tabla, codtel_tabla in filas_de_tabla:
                    data_tuple_key = (prov_tabla, loc_tabla, cp_tabla, cpa_tabla) 
                    if data_tuple_key not in seen_data_tuples_this_run:
                        seen_data_tuples_this_run.add(data_tuple_key)
                        datos_para_esta_provincia.append([
                            provincia_iter_nombre, localidad_nav_nombre, 
                            prov_tabla, loc_tabla, cp_tabla, cpa_tabla, codtel_tabla
                        ])
                        count_nuevos_para_esta_loc_nav +=1
                if count_nuevos_para_esta_loc_nav > 0:
                     print(f"      De {len(filas_de_tabla)} filas en tabla, {count_nuevos_para_esta_loc_nav} registros únicos (P,L,CP,CPA de tabla) añadidos para esta provincia (en esta ejecución).")
            else:
                print(f"      No se encontraron datos de CP/CPA en la tabla para {localidad_nav_nombre}.")

        if datos_para_esta_provincia:
            with open(ruta_archivo_provincia, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file, delimiter=';')
                writer.writerow([
                    "Provincia_Navegacion", "Localidad_Agrupadora_Link", 
                    "Provincia_Tabla", "Localidad_Especifica_Tabla", 
                    "CP_Tabla", "CPA_Tabla", "CodTel_Tabla"
                ])
                writer.writerows(datos_para_esta_provincia)
            print(f"  Datos de {provincia_iter_nombre} ({len(datos_para_esta_provincia)} filas) guardados en {ruta_archivo_provincia}")
        else:
            print(f"  No se guardaron datos para {provincia_iter_nombre} (no se encontró información nueva de CP/CPA o localidades).")
            # Opcional: Crear un archivo vacío para marcarla como procesada si se desea.
            # with open(ruta_archivo_provincia, mode='w', newline='', encoding='utf-8') as file:
            #     writer = csv.writer(file, delimiter=';') # Crear archivo vacío con encabezados
            #     writer.writerow(["Provincia_Navegacion", "Localidad_Agrupadora_Link", "Provincia_Tabla", "Localidad_Especifica_Tabla", "CP_Tabla", "CPA_Tabla", "CodTel_Tabla"])
            # print(f"    Archivo vacío creado para {provincia_iter_nombre} para marcarla como procesada.")

    print("\n--- Proceso de scraping de todas las provincias (o restantes) completado ---")
    print(f"Los archivos CSV individuales están en la carpeta: {OUTPUT_DIRECTORY}")
    print("El siguiente paso sería combinar estos archivos CSV y realizar una deduplicación final si es necesario.")

if __name__ == "__main__":
    main()