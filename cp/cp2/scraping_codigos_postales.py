print("DEBUG: El script de Python ha comenzado a ejecutarse.")
import requests
from bs4 import BeautifulSoup
import csv
from urllib.parse import urljoin
import time

BASE_URL = "https://codigo-postal.co"

def obtener_provincias():
    url = f"{BASE_URL}/argentina/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    print(f"Intentando acceder a: {url}")
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error al acceder a la página de provincias {url}: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    # print("\n--- HTML recibido de la página de provincias (primeros 2000 caracteres) ---") # Comentado para brevedad
    
    provincias = []
    selector_provincias = "ul.column-list li a"
    print(f"Usando selector para provincias: '{selector_provincias}'")
    elementos_provincia = soup.select(selector_provincias)
    print(f"Elementos 'a' encontrados para provincias: {len(elementos_provincia)}")

    for a in elementos_provincia:
        nombre = a.text.strip()
        enlace_relativo = a.get('href')
        if enlace_relativo:
            enlace_absoluto = urljoin(BASE_URL, enlace_relativo)
            provincias.append((nombre, enlace_absoluto))
    return provincias

'''def obtener_localidades(provincia_url, provincia_nombre):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    print(f"\nIntentando acceder a la página de localidades para {provincia_nombre}: {provincia_url}")
    try:
        response = requests.get(provincia_url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error al acceder a la página de localidades {provincia_url}: {e}")
        return []
        
    soup = BeautifulSoup(response.text, 'html.parser')
    # print(f"\n--- HTML de la página de provincia '{provincia_nombre}' ({provincia_url}) (primeros 3000 caracteres) ---") # Comentado
    
    localidades = []
    selector_localidades = "ul.cities li a"
    print(f"Usando selector para localidades: '{selector_localidades}'")
    elementos_localidad = soup.select(selector_localidades)
    print(f"Elementos 'a' encontrados para localidades en {provincia_nombre}: {len(elementos_localidad)}")

    for a in elementos_localidad:
        nombre = a.text.strip()
        enlace_relativo = a.get('href')
        if enlace_relativo:
            enlace_absoluto = urljoin(BASE_URL, enlace_relativo)
            localidades.append((nombre, enlace_absoluto))
        else:
            print(f"  Advertencia: Elemento 'a' sin href encontrado en lista de localidades de {provincia_nombre}: {a.text}")
    return localidades'''

def obtener_localidades(provincia_url, provincia_nombre):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    print(f"\nIntentando acceder a la página de localidades para {provincia_nombre}: {provincia_url}")
    try:
        response = requests.get(provincia_url, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error al acceder a la página de localidades {provincia_url}: {e}")
        return []
        
    soup = BeautifulSoup(response.text, 'html.parser')
    # print(f"\n--- HTML de la página de provincia '{provincia_nombre}' ({provincia_url}) (primeros 3000 caracteres) ---") # Comentado para no saturar
    
    localidades = []
    selector_localidades = "ul.cities li a" 
    # print(f"Usando selector para localidades: '{selector_localidades}'") # Ya lo sabemos
    
    elementos_localidad_crudos = soup.select(selector_localidades)
    print(f"  Elementos <a> crudos encontrados por el selector en {provincia_nombre}: {len(elementos_localidad_crudos)}")

    valid_links_count = 0
    for a_tag in elementos_localidad_crudos:
        nombre = a_tag.text.strip()
        enlace_relativo = a_tag.get('href')
        if enlace_relativo:
            enlace_absoluto = urljoin(BASE_URL, enlace_relativo)
            localidades.append((nombre, enlace_absoluto))
            valid_links_count += 1
        else:
            # Intentar obtener algo de texto del tag 'a' para identificarlo
            tag_text_debug = ' '.join(a_tag.stripped_strings) if a_tag else 'TAG_A_PROBLEMATICO'
            print(f"  ADVERTENCIA: Elemento <a> sin href encontrado en {provincia_nombre}. Texto del tag: '{tag_text_debug}'")
            
    print(f"  >> Links de localidad válidos (con href) añadidos para {provincia_nombre}: {valid_links_count}")
    return localidades

def obtener_codigos_postales(localidad_url_navegada, nombre_provincia_navegada, nombre_localidad_navegada):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    print(f"\nIntentando acceder a la página de CP para '{nombre_localidad_navegada}' ({nombre_provincia_navegada}): {localidad_url_navegada}")
    try:
        response = requests.get(localidad_url_navegada, headers=headers, timeout=10)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error al acceder a la página de códigos postales {localidad_url_navegada}: {e}")
        return []
        
    soup = BeautifulSoup(response.text, 'html.parser')
    datos_extraidos = [] # Cambiado de 'codigos' a 'datos_extraidos'
    tabla = soup.find("table")
    if not tabla:
        print(f"No se encontró ninguna tabla en {localidad_url_navegada}")
        return []

    rows = tabla.find_all("tr")
    print(f"Filas encontradas en la tabla de '{nombre_localidad_navegada}': {len(rows)}")

    for row in rows[1:]: # Omitir la primera fila (asumimos que es el encabezado de la tabla)
        cols = row.find_all("td")
        # La tabla web tiene: Provincia, Localidad, Código Postal, CPA, Código Telefónico
        # Índices:             0          1          2             3      4
        if len(cols) >= 3: # Necesitamos al menos Provincia, Localidad, Código Postal
            provincia_de_tabla = cols[0].text.strip()
            localidad_de_tabla = cols[1].text.strip() # ¡Esta es la que queremos guardar!
            cp_de_tabla = cols[2].text.strip()
            
            # CPA y Código Telefónico son opcionales para tu necesidad actual
            # cpa_de_tabla = cols[3].text.strip() if len(cols) >= 4 else ""
            # codtel_de_tabla = cols[4].text.strip() if len(cols) >= 5 else ""
            
            datos_extraidos.append((provincia_de_tabla, localidad_de_tabla, cp_de_tabla))
        else:
            print(f"  Advertencia: Fila sin suficientes 'td' (se esperaban >=3) en {localidad_url_navegada}: {row.text.strip()}")
            
    return datos_extraidos

def main():
    print("Iniciando script de scraping...")
    provincias = obtener_provincias()
    
    print(f"\nTotal de provincias encontradas: {len(provincias)}")
    if not provincias:
        print("No se pudieron obtener las provincias. Terminando script.")
        return
   
    '''# --- Bucle completo (comentado por ahora para prueba inicial) ---
    all_data_final = []
    print("\n--- Iniciando extracción completa ---")

    for provincia_iter_nombre, provincia_iter_url in provincias:
            print(f"\nProcesando Provincia: {provincia_iter_nombre}")
            time.sleep(1) 
            localidades_nav = obtener_localidades(provincia_iter_url, provincia_iter_nombre)
            print(f"  Encontrados {len(localidades_nav)} links de localidad para {provincia_iter_nombre}")
            if not localidades_nav: # SI NO SE ENCONTRARON LOCALIDADES PARA ESTA PROVINCIA
                all_data_final.append([provincia_iter_nombre, "NINGUNA_LOCALIDAD_ENCONTRADA_EN_PAG_PROV", "N/A", "N/A", "N/A"])
        # Continuar con la siguiente provincia
                continue # Esto saltará el bucle interno de localidades para esta provincia
    
        
    for localidad_nav_nombre, localidad_nav_url in localidades_nav:
             print(f"    Procesando link de localidad: {localidad_nav_nombre} (de {provincia_iter_nombre})")
             time.sleep(1) 
             filas_tabla = obtener_codigos_postales(localidad_nav_url, provincia_iter_nombre, localidad_nav_nombre)
            
             if filas_tabla:
                 for prov_tabla, loc_tabla, cp_tabla in filas_tabla:
                     all_data_final.append([provincia_iter_nombre, localidad_nav_nombre, prov_tabla, loc_tabla, cp_tabla])
             else:
                 all_data_final.append([provincia_iter_nombre, localidad_nav_nombre, "No encontrado en tabla", "No encontrado en tabla", "No encontrado en tabla"])'''
    # --- Bucle completo ---
    all_data_final = [] 
    print("\n--- Iniciando extracción completa ---")
    for provincia_iter_nombre, provincia_iter_url in provincias:
        print(f"\nProcesando Provincia: {provincia_iter_nombre}")
        time.sleep(1) 
        localidades_nav = obtener_localidades(provincia_iter_url, provincia_iter_nombre)
        # La cuenta de localidades válidas ahora se imprime desde dentro de obtener_localidades()
        
        if not localidades_nav: # Si NO se encontraron links de localidad VÁLIDOS para ESTA provincia
            print(f"  --> No se procesarán sub-localidades para {provincia_iter_nombre} ya que no se encontraron links válidos en su página.")
            all_data_final.append([provincia_iter_nombre, "NINGUNA_LOCALIDAD_VALIDA_ENCONTRADA_EN_PAG_PROV", "N/A", "N/A", "N/A"])
            continue # Saltar al siguiente provincia_iter_nombre
            
        # Si SÍ se encontraron localidades_nav válidas, entonces procesamos cada una:
        for localidad_nav_nombre, localidad_nav_url in localidades_nav:
            # Podrías comentar el siguiente print si la salida es demasiada durante el scrapeo completo:
            print(f"    Procesando link de localidad: {localidad_nav_nombre} (de {provincia_iter_nombre})") 
            time.sleep(1) 
            filas_tabla = obtener_codigos_postales(localidad_nav_url, provincia_iter_nombre, localidad_nav_nombre)
            
            if filas_tabla:
                for prov_tabla, loc_tabla, cp_tabla in filas_tabla:
                    all_data_final.append([provincia_iter_nombre, localidad_nav_nombre, prov_tabla, loc_tabla, cp_tabla])
            else:
                all_data_final.append([provincia_iter_nombre, localidad_nav_nombre, "No encontrado en tabla", "No encontrado en tabla", "No encontrado en tabla"])

    # ... (resto de la función main para escribir el CSV) ...

    if all_data_final:
         with open("todos_los_codigos_postales.csv", mode='w', newline='', encoding='utf-8') as file:
             writer = csv.writer(file)
             writer.writerow(["Provincia_Navegacion", "Localidad_Navegacion_URL", "Provincia_Tabla", "Localidad_Tabla", "CP_Tabla"])
             writer.writerows(all_data_final)
         print("\nProceso completo. Todos los datos guardados en todos_los_codigos_postales.csv")
    else:
         print("\nNo se extrajeron datos para guardar en el archivo completo.")

if __name__ == "__main__":
    main()

