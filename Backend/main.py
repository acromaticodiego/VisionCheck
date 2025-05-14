import cv2
from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Body, Query
import subprocess
# from DecodeQR import decodeQR
# from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import shutil
import os
import uuid
import httpx
import pandas as pd 
import logging
from controlModel import Control_stem
import variables_globales
from datetime import datetime
from mongoDB import connection_data_base, count_harvester_records, count_harvester_records_week, query_data
import asyncio
from fastapi.responses import FileResponse

# Inicializa la aplicación FastAPI
app = FastAPI()

# Manejador global de excepciones HTTP para devolver respuestas JSON con el detalle del error
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"mensaje": exc.detail},
    )

# Configurar CORS para permitir solicitudes desde cualquier origen (útil durante el desarrollo)
origins = [
    "*",
    "http://localhost",
    "http://localhost:8000",
]

# Se utiliza el middleware de CORS, actualmente se configura para permitir todos los orígenes
middleware = [
    Middleware(CORSMiddleware, allow_origins=origins)
]
app = FastAPI(middleware=middleware)

# Directorios de almacenamiento de imágenes
UPLOAD_DIR = "uploads/"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

UPLOAD_DIR_QR = "Cap_Image_QR/"

if not os.path.exists(UPLOAD_DIR_QR):
    os.makedirs(UPLOAD_DIR_QR)

# Variables globales utilizadas en el servidor
CodeQR = ''

count_stem = 0 

count_momentos = 0

count_hb = 0

id_bag = ""
variety = ""
harvester = ""
cuttings = ""
block = ""

#---------------------------------------------------------------------------------------------
# Endpoint para subir una imagen y procesarla
@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    global count_stem
    global count_momentos
    # Genera un identificador único (aunque no se utiliza posteriormente)
    unique_id = str(uuid.uuid4())
    
    # Se guarda el archivo con el nombre "imagenX.jpg", donde X es un número del 1 al 4
    for i in range(1, 5):
        file_name = f"imagen{i}.jpg"  
        
        file_path = os.path.join(UPLOAD_DIR, file_name)
        # Si el archivo no existe aún se sale del loop
        if not os.path.exists(file_path):
            break
        
    # Guarda el archivo subido en el servidor
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Lee la imagen usando OpenCV y la rota 90° en sentido contrario a las agujas del reloj
    image = cv2.imread(file_path)
    rotated_img = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
    cv2.imwrite(file_path, rotated_img)
    
    # Procesa la imagen mediante la función controlModel y actualiza el conteo global de tallos
    count_return = controlModel(file_name)
    count_stem += count_return

    return {"filename": file_name, "message": "Archivo subido exitosamente",
            'count_stem': count_stem,
           }

#---------------------------------------------------------------------------------------------
# Endpoint para subir imagen de código QR
@app.post("/QR/")
async def upload_file_QR(file: UploadFile = File(...)):
    global CodeQR
    global count_stem
    # Genera un identificador único (no es usado posteriormente)
    unique_id = str(uuid.uuid4())
    # Se define la ruta para guardar la imagen del QR
    file_path = os.path.join(UPLOAD_DIR_QR, 'Codigo_QR.png')

    # Si el archivo no existe, se guarda
    
    if not os.path.exists(file_path):    
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    # Se podría decodificar el QR (código comentado)
    # CodeQR = decodeQR()

    
    
    return {"filename": 'Codigo_QR', "message": "Archivo subido exitosamente"}

#---------------------------------------------------------------------------------------------
# Función para obtener la fecha actual formateada
def obtener_fecha_actual():
    fecha_actual = datetime.now()
    fecha_formateada = fecha_actual.strftime("%d/%m/%Y")
    return fecha_formateada

#---------------------------------------------------------------------------------------------
# Endpoint para obtener valores iniciales para la web mediante un GET
@app.get("/get_values_iniciales")
async def search_initial_values():
    print("✅ Solicitud recibida en /get_values_iniciales")
    global id_bag
    global variety 
    global harvester 
    global cuttings
    global block

    # Ruta del archivo que contiene el id_bag (código de saco)
    file_path = r'C:\Users\juanl\OneDrive\Desktop\cuttingVision\qr_codes.txt'
    
    # Verifica que el archivo exista y lee el id_bag
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            id_bag = file.readline().strip()
    else:
        raise HTTPException(status_code=500, detail="El archivo qr_codes.txt no existe.")

    if not id_bag:
        raise HTTPException(status_code=500, detail="El archivo qr_codes.txt está vacío.")
    
    # Lee de nuevo el contenido completo del archivo para verificar
    if os.path.exists(file_path):
       with open(file_path, 'r') as file:
           contenido = file.readlines()
           print("📂 Contenido del archivo:", contenido)
           id_bag = contenido[0].strip() if contenido else None

    if id_bag:
        print("🎯 ID_BAG leído:", id_bag)
    else:
        raise HTTPException(status_code=500, detail="No se pudo leer un ID_BAG válido.")

    values = {}
    # Consulta la información de cortes usando el id_bag obtenido
    values = await get_cuttings_info(id_bag, values)
    
    # Asigna valores globales a partir de la respuesta obtenida
    id_value = values["_id"]
    harvester = values["harvester"]
    variety = values["variety"]
    cuttings = values["cuttings"]
    block  = values["block"]
    # Calcula la medida según la variedad y bloque
    medCM = medida(variety, block)
    variables_globales.medCM = medCM
    
    return {"id_value": id_value, "harvester": harvester,
            "variety": variety, "medCM": medCM, "cuttings": cuttings}

#---------------------------------------------------------------------------------------------
# Función asíncrona para extraer datos JSON desde un endpoint externo y almacenarlos en un diccionario
async def get_cuttings_info(code: str, values: dict, retries: int = 3, delay: int = 1):
    # URL del endpoint externo para obtener información sobre los cortes
    url = f"http://10.1.2.25:4183/api/v1/cuttings/{code}/"
    print(f"🌍 Consultando API externa con: {url}")

    for attempt in range(retries):
        try:
            # Realiza la petición GET de forma asíncrona usando httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
            print(f"📡 Código de respuesta API: {response.status_code}")

            # Si la respuesta es exitosa, se extraen los datos
            
            if response.status_code == 200:
            
                data = response.json().get("data", {})
            
                if not data:
                    raise HTTPException(status_code=500, detail="La API devolvió un JSON sin datos.")
                # Se actualiza el diccionario con la información recibida
                values.update({
                    "_id": data.get("_id"),
                    "type": data.get("type"),
                    "farm": data.get("farm"),
                    "variety": data.get("variety"),
                    "varietyId": data.get("varietyId"),
                    "plantingWeek": data.get("plantingWeek"),
                    "cuttings": data.get("cuttings"),
                    "device": data.get("device"),
                    "user": data.get("user"),
                    "renewal": data.get("renewal"),
                    "recordDate": data.get("recordDate"),
                    "state": data.get("state"),
                    "block": data.get("block"),
                    "bed": data.get("bed"),
                    "subBed": data.get("subBed"),
                    "harvester": data.get("harvester"),
                    "bedCuttings": data.get("bedCuttings"),
                    "extempIn": data.get("extempIn"),
                    "extempOut": data.get("extempOut")
                })
                print(f"✅ Datos recibidos de la API: {values}")
                return values
            else:
                print(f"⚠️ Error en la API externa: {response.status_code}, {response.text}")
                raise HTTPException(status_code=response.status_code, detail=response.text)

        except httpx.RequestError as e:
            print(f"❌ Error de conexión con la API en el intento {attempt + 1}: {e}")
            if attempt < retries - 1:
                print(f"⏳ Reintentando en {delay} segundos...")
                await asyncio.sleep(delay)
            else:
                raise HTTPException(status_code=500, detail="Error al conectar con la API externa después de varios intentos.")
        
        except Exception as e:
            print(f"🔥 Error inesperado: {e}")
            raise HTTPException(status_code=500, detail="Error inesperado en el servidor.")

#---------------------------------------------------------------------------------------------
# Función para obtener la medida según la variedad y el bloque usando un archivo Excel
def medida(variedad, block):
    global valores_F
    global valores_G
    column_names = ['Col1', 'Col2', 'Col3', 'Col4', 'Col5', 'Col6', 'Col7']
    file_path = os.path.abspath('VARIEDADES Y LONGITUDES.xlsx')
    
    try:
        # Convierte la variedad a mayúsculas para asegurar coincidencia en la búsqueda
        variedad = variedad.upper()
        if os.path.exists(file_path):
            df = pd.read_excel(file_path, names=column_names, engine='openpyxl', header=None)
            # Filtra las filas donde la columna 'Col3' coincide con la variedad
            filtro = df[df['Col3'] == variedad]
            
            if not filtro.empty:
                valores_F = filtro['Col6'].values
                valores_G = filtro['Col7'].values
                
                # Lista de bloques para determinar el valor de longitud
                block_list = [5, 6, 7, 8, 9, 14]  # Nota: el bloque 14 tiene un criterio especial
                if block in block_list:
                    longitud = valores_F
                else:
                    longitud = valores_G
                return longitud.tolist()
            else:
                print(f"No se encontró el valor '{variedad}' en la columna 'Col3'.")
                return f"No se encontraron valores para '{variedad}'."
        else:
            print("El archivo no existe.")
            return "El archivo no existe."
    except Exception as e:
        print(f"Ocurrió un error: {e}")
        return f"Error: {e}"

#---------------------------------------------------------------------------------------------
# Función para eliminar imágenes en un directorio específico
def delete_images(directory_path):
    try:
        # Obtiene la lista de archivos en el directorio
        files = os.listdir(directory_path)
        # Recorre y elimina cada archivo
        for file_name in files:
            file_path = os.path.join(directory_path, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)
    
        print("Imágenes eliminadas exitosamente")
    
    except Exception as e:
        print(f"Error al eliminar imágenes: {e}")

# Endpoint para eliminar imágenes de directorios específicos
@app.get("/delete/")
async def get_delete():
    delete_images('uploads')
    delete_images('results')
    delete_images('Recortes')
    return {"message": "images successfully deleted"}

#---------------------------------------------------------------------------------------------
# Configuración básica del logging a nivel INFO
logging.basicConfig(level=logging.INFO)

# Función para ejecutar el control del modelo a partir de una imagen; se utiliza la clase Control_stem
def controlModel(path):
    control = Control_stem(path)
    conut_stem = control.cont_stem()
    return conut_stem

#---------------------------------------------------------------------------------------------
# Endpoint para obtener información del control del modelo (detección de tallos)
@app.get("/controlModel/")
async def get_controlModel():
    global count_stem
    try:
        logging.info("Iniciando controlModel...")
        logging.info("controlModel finalizado.")
        return {
            "message": "modelo cargado y algoritmos ejecutados",
            "status_code": 200,
            "count_stem": count_stem,
        }
    except Exception as e:
        logging.error(f"Error en controlModel: {e}")
        return {"message": "Error interno del servidor", "status_code": 500}

#---------------------------------------------------------------------------------------------
# Endpoint para obtener el análisis de la imagen (detectar medidas, área foliar, etc.)
@app.get("/analisis/")
async def get_analisis():
    global count_hb
    global id_bag
    global variety
    global harvester
    global cuttings
    global block
    global count_stem
    
    length = 0
    diameter = 0
    stem_l = 0
    stem_s = 0
    stem_g = 0
    # Directorio de la carpeta donde están los recortes de la imagen para análisis
    folder_path = r'C:\Users\juanl\OneDrive\Desktop\cuttingVision\Backend\Recortes'
    control = Control_stem(folder_path)
   
    carpeta_captura_imagenes_web = r"C:\Users\juanl\OneDrive\Desktop\cuttingVision\Backend\uploads"
    carpeta_analisis_proceso = r'C:\Users\juanl\OneDrive\Desktop\cuttingVision\Backend\Recortes'
    try:
        # Realiza el proceso de corte de imagen y análisis de objetos
        control.cutting_img(carpeta_captura_imagenes_web, carpeta_analisis_proceso)
        count_hb = control.detect_objects(folder_path)

        logging.info(f"Hoja en base: {count_hb}")
        
        # Obtiene medidas y estadísticas relacionadas a los tallos
        length, diameter, stem_l, stem_s, stem_g, average_diameter, desviacion_estandar_longitud, promedio_diametro, max_diameter, min_diameter = control.detect_stem(carpeta_analisis_proceso)
        max_esqueje = control.max_esqueje
        # Análisis del área foliar (promedio, máximo, mínimo, desviación)
        average_area_foliar, max_area_foliar, min_area_foliar, std_area_foliar = control.detect_area_foliar(carpeta_analisis_proceso)

        # Imprime información de depuración
        print('desviacion:', diameter)
        print('desviacion:', diameter)
        print('desviacion:', diameter)
        print('Hb:', count_hb)
        day = obtener_fecha_actual()
        print('La fecha actual...')
        print('La fecha actual...')
        print('La fecha actual...')
        print(day)
        # Guarda los registros en la base de datos
        connection_data_base(id_bag, variety, cuttings, block, harvester, count_stem, count_hb, stem_l, stem_s, length, diameter, day)        
        return {
            "message": "Hojas encontradas",
            "status_code": 200,
            "count_hb": count_hb,
            "length": length,
            "diameter": diameter,
            "stem_l": stem_l,
            "stem_s": stem_s,
            "stem_g": stem_g,
            "average_diameter": average_diameter,
            "desviacion_estandar_longitud": desviacion_estandar_longitud,
            "max_esqueje": max_esqueje,
            "min_esqueje": control.min_esqueje,
            "average_area_foliar": average_area_foliar,
            "max_area_foliar": max_area_foliar,
            "min_area_foliar": min_area_foliar,
            "promedio_diametro": promedio_diametro,
            "max_diameter": max_diameter,
            "promedio_diametro_menor": min_diameter,
            "std_area_foliar": std_area_foliar,
        }
    except Exception as e:
        logging.error(f"Error en controlModel: {e}")
        return {
            "message": "Error interno del servidor",
            "status_code": 500
        }

#---------------------------------------------------------------------------------------------
'''
@app.get("/harvester_data_day_week/")
async def get_harvester_data_day_week():
    global harvester
    print('Cosechador = ', harvester)
    print('Cosechador = ', harvester)
    print('Cosechador = ', harvester)
    day = obtener_fecha_actual()

    try:
        logging.info("Datos del cosechador en el dia")

        count,count_Cutting_bag,count_base_sheet,count_long_stem,count_short_stem,average_length_day,average_diameter_day = count_harvester_records(harvester,day)
        countW, count_Cutting_bag_w,count_base_sheet_w, count_long_stem_w, count_short_stem_w, average_length_week, average_diameter_week = count_harvester_records_week(harvester,day)
        print('promedio del diametro ', average_diameter_day)
        print('ejecutadooooooooooooooooooooooooooooooooooooooooooooooooo')

        return {
            "message": "modelo cargado y algoritmos ejecutados",
            "status_code": 200,
            "count": count,
            "count_Cutting_bag": count_Cutting_bag,
            "count_base_sheet": count_base_sheet,
            "count_long_stem": count_long_stem,
            "count_short_stem": count_short_stem,
            "average_length_day": average_length_day,
            "average_diameter_day": average_diameter_day,
            "countW": countW,
            "count_Cutting_bag_w": count_Cutting_bag_w,
            "count_base_sheet_w": count_base_sheet_w,
            "count_long_stem_w": count_long_stem_w,
            "count_short_stem_w": count_short_stem_w,
            "average_length_week": average_length_week,
            "average_diameter_week": average_diameter_week
        }
    except Exception as e:
        logging.error(f"Error en controlModel: {e}")
        return {"message": "Error interno del servidor", "status_code": 500}
'''
#---------------------------------------------------------------------------------------------
# Endpoint para iniciar un escaneo: reinicia el contador de tallos y elimina las imágenes
@app.get("/start_scan")
async def start_scan():
    try:
        global count_stem
        count_stem = 0
        response = await httpx.get("http://127.0.0.1:8000/delete/")
        
        return {"mensaje": "Escaneo iniciado correctamente"}
    except Exception as e:
        # En caso de error se podría propagar una excepción HTTP
        pass

#---------------------------------------------------------------------------------------------
# Endpoint para listar imágenes detectadas (versión 1)
@app.get("/list_detected_images")
async def get_detected_images():
    try:
        # Se utiliza un nombre dummy para inicializar la clase Control_stem ya que el método no depende de una imagen en concreto
        control = Control_stem("dummy.jpg")
        images = control.list_detected_images()
        return {"detected_images": images}
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"Error: {str(e)}"})


#---------------------------------------------------------------------------------------------
# Endpoint para servir una imagen a partir de su nombre de archivo
@app.get("/images/{filename}")
async def get_hb_image(filename: str):
    output_folder = "C:/Users/juanl/OneDrive/Desktop/cuttingVision/Backend/results"
    file_path = os.path.join(output_folder, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    else:
        raise HTTPException(status_code=404, detail="Image not found")

#---------------------------------------------------------------------------------------------
# Endpoint para listar imágenes detectadas (versión 2) para otra categoría
@app.get("/list_detected_images1")
async def get_detected_images1():
    try:

        control = Control_stem("dummy.jpg")
        images = control.list_detected_images1()
        return {"detected_images1": images}
    except Exception as e:

        return JSONResponse(status_code=500, content={"message": f"Error: {str(e)}"})


#---------------------------------------------------------------------------------------------
# Endpoint para servir imágenes de "esquejescortos"
@app.get("/images/esquejescortos/{filename}")
async def get_esquejescortos_image(filename: str):
    output_folder = r"C:\Users\juanl\OneDrive\Desktop\cuttingVision\Backend\esquejescortos"
    file_path = os.path.join(output_folder, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    else:

        raise HTTPException(status_code=404, detail="Image not found")


#---------------------------------------------------------------------------------------------
# Endpoint para listar imágenes detectadas (versión 3) para modales
@app.get("/list_detected_images2")
async def get_detected_images1():

    try:

        control = Control_stem("dummy.jpg")
        images = control.list_detected_images2()
        return {"detected_images2": images}
    except Exception as e:
        return JSONResponse(status_code=500, content={"message": f"Error: {str(e)}"})


#---------------------------------------------------------------------------------------------
# Endpoint para servir imágenes de "esquejesargos"
@app.get("/images/esquejesargos/{filename}")
async def get_esquejescortos_image(filename: str):
    output_folder = r"C:\Users\juanl\OneDrive\Desktop\cuttingVision\Backend\esquejes_largos"
    file_path = os.path.join(output_folder, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path)
    else:
        raise HTTPException(status_code=404, detail="Image not found")

#---------------------------------------------------------------------------------------------
# Endpoint para capturar una imagen desde la cámara USB
@app.get("/capture_image")
def capture_image():
    # Intenta abrir la cámara USB usando el índice 1
    cap = cv2.VideoCapture(1)
    if not cap.isOpened():
        raise HTTPException(status_code=500, detail="No se pudo acceder a la cámara USB.")
    
    ret, frame = cap.read()
    cap.release()  # Libera la cámara tras capturar
    if not ret:
        raise HTTPException(status_code=500, detail="No se pudo capturar la imagen desde la cámara USB.")
    
    # Redimensiona la imagen y la rota 90° en sentido contrario a las agujas del reloj
    frame = cv2.resize(frame, (1920, 1080))
    rotated_img = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
    
    # Determina un nombre de archivo disponible similar a la lógica de /upload/
    file_name = None
    for i in range(1, 5):
        candidate = f"imagen{i}.jpg"
        file_path = os.path.join(UPLOAD_DIR, candidate)
        if not os.path.exists(file_path):
            file_name = candidate
            break
    if file_name is None:
        raise HTTPException(status_code=500, detail="No se encontró un nombre de archivo disponible.")
    
    file_path = os.path.join(UPLOAD_DIR, file_name)
    cv2.imwrite(file_path, rotated_img)
    
    # Procesa la imagen mediante controlModel y actualiza el contador global de tallos
    count_return = controlModel(file_name)
    global count_stem
    count_stem += count_return
    
    return {
        "filename": file_name,
        "message": "Archivo capturado y procesado exitosamente",
        "count_stem": count_stem
    
    
    }