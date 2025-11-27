from selenium import webdriver
from selenium.webdriver import Chrome
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import time
import pandas as pd

#Lista de categorías a recorrer
lista_categorias = ["Importacion", "Exportacion", "Comercio"]

#Navegador
service = Service(ChromeDriverManager().install())
option = webdriver.ChromeOptions()
#option.add_argument("--headless") #para ocultar el navegador
option.add_argument("--window-size=1366,768")
driver = Chrome(service=service, options=option)
wait = WebDriverWait(driver, 10)

todos_los_datos = []

#Recorrer cada categoría
for categoria in lista_categorias:

    print(f"--- Buscando categoría: {categoria} ---")

    #Ir al sitio web
    driver.get("https://www.amarillas.cl/")

    #Buscar categoría
    campo_buscar = wait.until(EC.visibility_of_element_located((By.XPATH,
        "/html/body/div[1]/div/main/div[1]/div[2]/div/div[2]/div[2]/form/div/div[1]/div/div[3]/input"
    )))
    campo_buscar.clear()
    campo_buscar.send_keys(categoria)

    button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'BUSCAR')]")))
    button.click()

    time.sleep(2)

    #PAGINACIÓN
    while True:
        time.sleep(1)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        # Obtener nombre de categoría en título página
        try:
            categoria_texto = driver.find_element(By.XPATH,
                "//h1[contains(@class, 'title-category')]").text.strip()
        except:
            categoria_texto = categoria

        # Extraer datos por resultado
        resultados = driver.find_elements(By.XPATH, "//div[contains(@class, 'advertise')]")

        for resu in resultados:
            try:
                nombre = resu.find_element(By.XPATH, ".//div[contains(@class, 'title')]/a").text
            except:
                nombre = ""

            try:
                link = resu.find_element(By.XPATH, ".//div[contains(@class, 'title')]/a").get_attribute("href")
            except:
                link = ""

            try:
                texto_elem = resu.find_elements(By.XPATH, ".//div[contains(@class,'text')]/p")
                texto = " ".join([t.text.strip() for t in texto_elem]) if texto_elem else ""
            except:
                texto = ""

            try:
                celular = resu.find_element(By.XPATH, ".//div[contains(@class,'contact')]/a").get_attribute("title")
            except:
                celular = ""

            # Guardar todo en una fila
            todos_los_datos.append([categoria_texto, nombre, link, texto, celular])

        # Botón siguiente
        try:
            next_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//li[contains(@class,'page-item-next')]/a")))

            if "disabled" in next_btn.get_attribute("class"):
                print("No hay más páginas para:", categoria)
                break

            driver.execute_script("arguments[0].click();", next_btn)
            time.sleep(2)

        except:
            print("No se encontró botón de siguiente para:", categoria)
            break

print("Total general de registros capturados:", len(todos_los_datos))

#GUARDAR DATOS EN EXCEL
#HOJA 1
df = pd.DataFrame(todos_los_datos, columns=["Categoria", "Nombre Empresa", "URL", "Informacion", "Celular"])


def celular_valido(numero):
    if pd.isna(numero) or not isinstance(numero, str):
        return False
    numero = numero.strip()  # limpiar espacios
    return numero.startswith("(+")

#Calculamos el scoring por campo
df["Score Nombre"] = df["Nombre Empresa"].apply(lambda x: 30 if pd.notna(x) and str(x).strip() != "" else 0)
df["Score Celular"] = df["Celular"].apply(lambda x: 30 if celular_valido(x) else 0)
df["celular_valido"] = df["Celular"].apply(lambda x: 1 if celular_valido(x) else 0)
df["Score Info"] = df["Informacion"].apply(lambda x: 20 if pd.notna(x) and str(x).strip() != "" else 0)
df["Score URL"] = df["URL"].apply(lambda x: 20 if pd.notna(x) and str(x).strip() != "" else 0)

#SUMA DEL SCORING
df["Lead Scoring"] = df[["Score Nombre","Score Celular","Score Info","Score URL"]].sum(axis=1)

def generar_razon(row):
    razones = []

    # Nombre Empresa
    if isinstance(row["Nombre Empresa"], str) and row["Nombre Empresa"].strip() != "":
        razones.append("Nombre válido (+30)")
    else:
        razones.append("Sin nombre (+0)")

    # Celular
    if row["celular_valido"] == 1:
        razones.append("Celular válido (+30)")
    else:
        razones.append("Celular inválido (+0)")

    # Informacion
    if isinstance(row["Informacion"], str) and row["Informacion"].strip() != "":
        razones.append("Información presente (+20)")
    else:
        razones.append("Sin información (+0)")

    # URL
    if isinstance(row["URL"], str) and row["URL"].startswith("http"):
        razones.append("URL válida (+20)")
    else:
        razones.append("URL inválida (+0)")

    return "; ".join(razones)

# Crear columna
df["Razon score"] = df.apply(generar_razon, axis=1)

top25 = df.sort_values(by="Lead Scoring", ascending=False).head(25)
print(top25)

df = df.drop(columns=["celular_valido"])

#HOJA 2
diccionario = pd.DataFrame([
    {
        "Columna": "Categoria",
        "Descripción": "Tipo de búsqueda realizada (Importación, Exportación, Comercio).",
        "Origen": "Variable enviada al buscador de Amarillas.cl",
        "Formato esperado": "Texto"
    },
    {
        "Columna": "Nombre",
        "Descripción": "Nombre de la empresa encontrada.",
        "Origen": "Texto dentro del div 'title' de cada resultado.",
        "Formato esperado": "Texto"
    },
    {
        "Columna": "Link",
        "Descripción": "URL de la ficha de la empresa.",
        "Origen": "Atributo href en el enlace del título.",
        "Formato esperado": "URL válida"
    },
    {
        "Columna": "Informacion",
        "Descripción": "parrafo argumentativo de la empresa.",
        "Origen": "Texto dentro del div 'text' de cada resultado.",
        "Formato esperado": "Texto"
    },
    {
        "Columna": "Celular",
        "Descripción": "Número de contacto de la empresa.",
        "Origen": "Atributo title dentro del div 'contact'.",
        "Formato esperado": "Número telefónico en texto"
    }
])

salida = "Resultados_Scraping.xlsx"
with pd.ExcelWriter(salida, engine = 'openpyxl') as write:
    df.to_excel(write, sheet_name='Lead', index=False)
    top25.to_excel(write, sheet_name="Top25", index=False)
    diccionario.to_excel(write, sheet_name='Diccionario_Campos', index=False)

print(f"Archivo Excel guardado como: {salida}")



    