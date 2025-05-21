import requests
from bs4 import BeautifulSoup
import csv
from urllib.parse import urljoin

BASE_URL = "https://codigo-postal.co"

'''def obtener_provincias():
    url = f"{BASE_URL}/argentina/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    provincias = []
    for a in soup.select("ul.listado li a"):
        nombre = a.text.strip()
        enlace = BASE_URL + a['href']
        provincias.append((nombre, enlace))
    return provincias'''

'''def obtener_provincias():
    url = f"{BASE_URL}/argentina/"
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Error al acceder a la página: {response.status_code}")
        return []
    soup = BeautifulSoup(response.text, 'html.parser')
    print("HTML recibido:")
    print(soup.prettify()[:2000])  # Mostramos solo los primeros 2000 caracteres para no saturar
    provincias = []
    for a in soup.select("ul.listado li a"):
        nombre = a.text.strip()
        enlace = BASE_URL + a['href']
        provincias.append((nombre, enlace))
    return provincias'''

def obtener_provincias():
    url = f"{BASE_URL}/argentina/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error al acceder a la página: {response.status_code}")
        return []
    soup = BeautifulSoup(response.text, 'html.parser')
    print("HTML recibido:")
    print(soup.prettify()[:2000])  # Sólo para depurar
    provincias = []
    for a in soup.select("ul.column-list li a"):
        nombre = a.text.strip()
        enlace = urljoin(BASE_URL, a['href'])
        provincias.append((nombre, enlace))
    return provincias

def obtener_localidades(provincia_url):
    response = requests.get(provincia_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    localidades = []
    for a in soup.select("ul.listado li a"):
        nombre = a.text.strip()
        enlace = urljoin(BASE_URL, a['href'])
        localidades.append((nombre, enlace))
    return localidades

def obtener_codigos_postales(localidad_url):
    response = requests.get(localidad_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    codigos = []
    rows = soup.select("table tr")
    for row in rows[1:]:
        cols = row.find_all("td")
        if len(cols) >= 4:
            calle = cols[0].text.strip()
            cp = cols[1].text.strip()
            cpa = cols[2].text.strip()
            coords = cols[3].text.strip()
            codigos.append((calle, cp, cpa, coords))
    return codigos

def main():
    provincias = obtener_provincias()
    primera_provincia = provincias[0]
    localidades = obtener_localidades(primera_provincia[1])
    primera_localidad = localidades[0]
    codigos_postales = obtener_codigos_postales(primera_localidad[1])

    with open("codigos_postales_ejemplo.csv", mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Provincia", "Localidad", "Calle", "CP", "CPA", "Coordenadas"])
        for calle, cp, cpa, coords in codigos_postales:
            writer.writerow([primera_provincia[0], primera_localidad[0], calle, cp, cpa, coords])
    print("Archivo CSV guardado como codigos_postales_ejemplo.csv")

if __name__ == "__main__":
    main()
