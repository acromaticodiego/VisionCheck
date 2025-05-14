import os
import cv2
import numpy as np
from detect import Detect
from ultralytics import YOLO
import time 
import math
import variables_globales
import pandas as pd
import shutil  # Asegúrate de importar shutil

count_momentos = 0

class Control_stem:  
    def __init__(self, img_name) -> None:
        self.detect = Detect()

        ##self.model = YOLO('model_hoja_base_100EM.pt ', task='detect')
        self.model = YOLO('model_hoja_base_100EM.pt', task='detect')
        #self.model_stem = YOLO('Stem_detect_seg.pt', task='detect')...
        #self.model_stem = YOLO('yolov8m.pt', task='detect')
        self.model_stem = YOLO('Stem_detect_seg.pt', task='detect')
        #self.model_stem = YOLO('Detector_esqueje.pt', task='detect')
        self.img_name =  img_name
    
    def binarize(self, img):
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(img_gray, (5, 5), 0)
        adapt_th = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 81, 8)
        th_inv = cv2.bitwise_not(adapt_th)
        contours, _ = cv2.findContours(th_inv, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        main_contour = None
        max_contour_area = 0
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > max_contour_area:
                max_contour_area = area
                main_contour = contour

        result = np.zeros_like(img_gray)
        cv2.drawContours(result, [main_contour], -1, (255, 255, 255), thickness=cv2.FILLED)

        return cv2.bitwise_not(adapt_th)
    
    def cont_stem(self):
        global count_momentos
        stem_l = 0
        stem_s = 0 
        stem_g = 0
        # Definir la ruta de la carpeta
        folder_path = fr'C:\Users\juanl\OneDrive\Desktop\cuttingVision\Backend\uploads\{self.img_name}'
        
        output_folder_path = fr'C:\Users\juanl\OneDrive\Desktop\cuttingVision\Backend\results'
        
        # Crear la carpeta de resultados si no existe
        if not os.path.exists(output_folder_path):
            os.makedirs(output_folder_path)

        total_stems = 0

        img = cv2.imread(folder_path)
        
        # Verificar si la imagen se leyó correctamente
        if img is None:
            print(f"Error al leer la imagen en la ruta: {folder_path}")
        
        # Procesar la imagen y contar los esquejes
        img_cuttings, cutImg_list, box_list = self.detect.det_cutting(img)
        
        # Convertir las coordenadas de PyTorch a listas de Python
        box_list = [box.tolist() for box in box_list]
        
        # --------------------- CAMBIO AGREGADO: Agrupar cajas solapadas inline ---------------------
        # Este bloque agrupa las cajas solapadas para que, si hay dos o más en el mismo esqueje,
        # se cuenten como una sola.
        unique_boxes = []
        threshold = 0.3  # Umbral de solapamiento (IoU)

        for box in box_list:
            found = False
            for u_box in unique_boxes:
                # Calcular la intersección entre box y u_box
                xx1 = max(box[0], u_box[0])
                yy1 = max(box[1], u_box[1])
                xx2 = min(box[2], u_box[2])
                yy2 = min(box[3], u_box[3])
                w = max(0, xx2 - xx1)
                h = max(0, yy2 - yy1)
                intersection = w * h

                # Calcular áreas de ambas cajas
                area_box = (box[2] - box[0]) * (box[3] - box[1])
                area_u_box = (u_box[2] - u_box[0]) * (u_box[3] - u_box[1])
                union = area_box + area_u_box - intersection

                iou = intersection / union if union > 0 else 0

                if iou > threshold:
                    found = True
                    break
            if not found:
                unique_boxes.append(box)
        # ----------------------------------------------------------------------------------------
        
        # Dibujar los recuadros verdes sobre las cajas únicas detectadas
        img_results = img.copy()
        total_stems += len(unique_boxes)
        for box in unique_boxes:
            x1, y1, x2, y2 = map(int, box)
            cv2.rectangle(img_results, (x1, y1), (x2, y2), (0, 102, 0), 2)
            
        # Guardar la imagen con los recuadros en la carpeta de resultados
        output_img_path = os.path.join(output_folder_path, f"result_{self.img_name}")
        cv2.imwrite(output_img_path, img_results)

        count_momentos += 1  # Variable de control 
        return total_stems
    
    def cutting_img(self, input_folder, output_folder):
        # Crear la carpeta de salida si no existe
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
        count = 0
        file_list = os.listdir(input_folder)
        for filename in file_list:
            # Ignora archivos que no son imágenes
            if not filename.endswith(('.jpg', '.jpeg', '.png', '.bmp')):
                continue
            # Lee la imagen
            img_path = os.path.join(input_folder, filename)
            img = cv2.imread(img_path)
            # Procesa la imagen
            img_cuttings, cutImg_list, box_list = self.detect.det_cutting(img)
            # Itera sobre cada imagen recortada
            for img_ in cutImg_list:
                # Convierte a escala de grises
                bin_img_bgr = cv2.cvtColor(img_, cv2.COLOR_BGR2GRAY)
                # Guarda la imagen con el contador como nombre de archivo
                output_filename = os.path.join(output_folder, f'image_{count}.jpg')
                cv2.imwrite(output_filename, bin_img_bgr)
                # Incrementa el contador
                count += 1
        print("Pausa de 4 segundos")
        time.sleep(3)  # Esperar 4 segundos

    def detect_objects(self, folder_path):  
        image_files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        con_HB = 0
        output_folder = r"C:\Users\juanl\OneDrive\Desktop\cuttingVision\Backend\HBn"
         # Limpiar la carpeta de salida antes de guardar nuevas imágenes
        if os.path.exists(output_folder):
            shutil.rmtree(output_folder)  # Elimina la carpeta y su contenido
        os.makedirs(output_folder, exist_ok=True)  # Vuelve a crear la carpeta vacía
    
        for image_file in image_files:
            image_path = os.path.join(folder_path, image_file)
            img = cv2.imread(image_path)
            img_HB = img.copy()  # Crear una copia de la imagen original
            results = self.model(img)
            total_boxes = 0
            has_cls_1 = False  # Variable para rastrear si hay al menos un cls == 1
        
            for result in results:
                boxes = result.boxes
                if boxes is not None:
                    for box in boxes:
                        cls = int(box.cls)  # Convertir a entero para evitar errores
                        total_boxes += 1
                        if cls == 1:
                            has_cls_1 = True
        
            for result in results:
                for bbox, box in zip(result.boxes.xyxy, result.boxes):
                    x1, y1, x2, y2 = bbox[:4].int().tolist()
                    if int(box.cls) == 1:
                        cv2.rectangle(img_HB, (x1, y1), (x2, y2), (0, 0, 255), 2)
                    elif int(box.cls) == 0:
                        cv2.rectangle(img_HB, (x1, y1), (x2, y2), (255, 0, 0), 2)
        
            if total_boxes >= 1 and has_cls_1:
                 con_HB += 1  
                 # Guardar la imagen procesada solo si se detectó cls == 1
                 output_path = os.path.join(output_folder, image_file)
                 cv2.imwrite(output_path, img_HB)
    
        cv2.destroyAllWindows()
        return con_HB
       
    def detect_stem(self, folder_path):
        
        output_folder = r"C:\Users\juanl\OneDrive\Desktop\cuttingVision\Backend\rojo_azul"
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        esqueje_corto_folder = r"C:\Users\juanl\OneDrive\Desktop\cuttingVision\Backend\esquejescortos"
        if os.path.exists(esqueje_corto_folder):
            shutil.rmtree(esqueje_corto_folder)  # Elimina la carpeta y su contenido
        os.makedirs(esqueje_corto_folder, exist_ok=True)  # Vuelve a crear la carpeta vacía
            
        esqueje_largo_folder = r"C:\Users\juanl\OneDrive\Desktop\cuttingVision\Backend\esquejes_largos"
        if os.path.exists(esqueje_largo_folder):
            shutil.rmtree(esqueje_largo_folder)  # Elimina la carpeta y su contenido
        os.makedirs(esqueje_largo_folder, exist_ok=True)  # Vuelve a crear la carpeta vacía

        image_files = [f for f in os.listdir(folder_path) if f.endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
        # Listas para almacenar las medidas de longitud y diámetro
        lengths = []
        diameters = []
        average_length=0
        average_diameter=0
        stem_Long = 0
        stem_small = 0 
        stem_good = 0
        box_count = 0
        medCM = float((variables_globales.medCM[0]))
        desviacion_estandar_longitud = 0
        

        max_stem_length = 0
        min_stem_length = float('inf')

        # Variables para llevar el seguimiento del esqueje más largo
        #max_stem_length = 0
        #max_stem_image = None
       
        for img_file in image_files:
            img_path = os.path.join(folder_path, img_file)
            img = cv2.imread(img_path)
            img_original = img.copy()
            # Aumentar el tamaño de la imagen al triple

            img = cv2.resize(img, None, fx=3, fy=3, interpolation=cv2.INTER_LINEAR)
            # Realizar la detección de objetos con el modelo_stem
            results = self.model_stem(img)
            # Procesar los resultados de la detección
            max_area = 0
            max_box = None
            for result in results:
                for box in result.boxes.xyxy:
                    box_count +=1
                    x_min, y_min, x_max, y_max = map(int, box)
                    area = (x_max - x_min) * (y_max - y_min)
                    if area > max_area:
                        max_area = area
                        max_box = (x_min, y_min, x_max, y_max)

            if max_box is not None:
                x_min, y_min, x_max, y_max = max_box
                centroid_x = (x_min + x_max) // 2
                centroid_y = (y_min + y_max) // 2
                region_of_interest = img[y_min:y_max, x_min:x_max]
                region_binarized = self.binarize(region_of_interest)
                region_binarized_color = cv2.cvtColor(region_binarized, cv2.COLOR_GRAY2BGR)
                img[y_min:y_max, x_min:x_max] = region_binarized_color
                #gray_roi = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                cv2.circle(img, (centroid_x, centroid_y), 3, (255, 255, 0), -1)
                cv2.rectangle(img, (x_min, y_min), (x_max, y_max), (255, 0, 255), 2)
                contours, _ = cv2.findContours(region_binarized, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                adjusted_contours = [cv2.convexHull(contour + (x_min, y_min)) for contour in contours]
                
                detected_inclinations = []
                for contour in adjusted_contours:
                    if len(contour) >= 5:                                    
                        cv2.drawContours(region_binarized_color, [contour], -1, (0, 0, 255), 2)
                        (x, y), (width, height), angle = cv2.fitEllipse(contour)
                        angle_rad = math.radians(angle)                          
                        detected_inclinations.append(angle_rad)
                    
                if len(contour) >= 5:
                    cv2.drawContours(region_binarized_color, [contour], -1, (0, 0, 255), 2)
                    (x, y), (width, height), angle = cv2.fitEllipse(contour)
                    angle_rad = math.radians(angle)
                    direction_x = math.cos(angle_rad)
                    direction_y = math.sin(angle_rad)
                    
                    corners = [(x_min, y_min), (x_min, y_max), (x_max, y_min), (x_max, y_max)]
                    #distances_to_corners = [math.sqrt((centroid_x - corner[0])*2 + (centroid_y - corner[1])*2) for corner in corners]
                    distances_to_corners = [math.sqrt((centroid_x - corner[0])**2 + (centroid_y - corner[1])**2) for corner in corners]
                    max_distance = max(distances_to_corners) * 0.95

                    line_x1_extended = int(centroid_x + max_distance * direction_y)
                    line_y1_extended = int(centroid_y - max_distance * direction_x)
                    line_x2_extended = int(centroid_x - max_distance * direction_y)
                    line_y2_extended = int(centroid_y + max_distance * direction_x)

                    cv2.line(img, (line_x1_extended, line_y1_extended), (line_x2_extended, line_y2_extended), (0, 255, 0), 2)
                    line_img = np.zeros_like(img)
                    cv2.line(line_img, (line_x1_extended, line_y1_extended), (line_x2_extended, line_y2_extended), (255, 255, 255), 2)
                    num_pixels_in_line = np.sum(line_img == 255)

                    scale_pixels_per_cm = 240
                    length_cm = (num_pixels_in_line / scale_pixels_per_cm)/3
                    lengths.append(length_cm)   

                    if length_cm > max_stem_length:
                        max_stem_length = length_cm  

                    if length_cm < min_stem_length:
                        min_stem_length = length_cm                 
                
                    line_length = math.sqrt((line_x2_extended - line_x1_extended)**2 + (line_y2_extended - line_y1_extended)**2)
                    if angle_rad >= 1: 
                        point_pos = 70
                    elif angle_rad<1:
                        point_pos = -70 

                    point_x = int(centroid_x + (point_pos / line_length) * (line_x1_extended - line_x2_extended))
                    point_y = int(centroid_y + (point_pos / line_length) * (line_y1_extended - line_y2_extended))
                    image_width = img.shape[1]
                    left_cross_x = 0
                    #left_cross_y = int(point_y - (point_x / direction_x) * direction_y)
                    left_cross_y = int(abs(point_y - (point_x / direction_x) * direction_y))
                    right_cross_x = image_width
                    right_cross_y = int(point_y + ((image_width - point_x) / direction_x) * direction_y)
                    cv2.line(img, (left_cross_x, left_cross_y), (right_cross_x, right_cross_y), (0, 0, 255), 1)
                    mask = np.zeros_like(img, dtype=np.uint8)
                    cv2.line(mask, (left_cross_x, left_cross_y), (right_cross_x, right_cross_y), (255, 255, 255), 2)
                    
                    img_with_colors = img.copy()

                    if length_cm <= (medCM - 0.5):
                       esqueje_corto = img.copy()
                       output_esqueje_corto = os.path.join(esqueje_corto_folder, f"esqueje_corto_{img_file}")
                       cv2.imwrite(output_esqueje_corto, esqueje_corto)
                    
                    output_path = os.path.join(output_folder, f"processed_{img_file}")
                    cv2.imwrite(output_path, img)
                    # Si el tallo es clasificado como largo
                    if length_cm >= (medCM + 0.5):
                        esqueje_largo = img.copy()  # Copia de la imagen procesada
                        output_esqueje_largo = os.path.join(esqueje_largo_folder, f"esqueje_largo_{img_file}")
                        cv2.imwrite(output_esqueje_largo, esqueje_largo)  # Guardar en 'esquejes_largos'

                    
                    output_path = os.path.join(output_folder, f"processed_{img_file}")
                    cv2.imwrite(output_path, img)

                    pixels_painted_count = 0
                    for x in range(left_cross_x, right_cross_x):
                        y = int((right_cross_y - left_cross_y) / (right_cross_x - left_cross_x) * (x - left_cross_x) + left_cross_y)
                        if 0 <= y < img_with_colors.shape[0] and 0 <= x < img_with_colors.shape[1]:
                            if 0 <= y - y_min < region_binarized.shape[0] and 0 <= x - x_min < region_binarized.shape[1]:
                                if region_binarized[y - y_min, x - x_min] == 255:
                                    img_with_colors[y, x] = [255, 0, 0]
                                    pixels_painted_count += 1
                                else:
                                    img_with_colors[y, x] = [0, 0, 255]

                    #print("Número de píxeles pintados:", pixels_painted_count)
                    scale_pixels_per_mm= 300                                           
                    diameter = (pixels_painted_count / scale_pixels_per_mm)
                    diameters.append(diameter )
                    

                    if (length_cm>= (medCM+0.5)):
                        stem_Long +=1
                    elif (length_cm<=(medCM-0.5)):
                        stem_small +=1
                    else:
                        stem_good +=1
                    
        print(diameters,"\n")
        # Convierte la lista en un DataFrame de Pandas
        df = pd.DataFrame(diameters)

        # Calcula la desviación estándar utilizando el método std()
        desviacion_estandar = float(df.std()*10)
        desviacion_estandar = float(np.nan_to_num(desviacion_estandar, nan=0.0))

        print("La desviación estándar de los datos es:", desviacion_estandar)
        print("La desviación estándar de los datos es:", desviacion_estandar)
        print("La desviación estándar de los datos es:", desviacion_estandar)
        print("La desviación estándar de los datos es:", desviacion_estandar)
        # Calcular los promedios
        if sum(lengths) == 0 and sum(diameters) == 0:
            print('PROMEDIO en cero')
        if lengths:
            average_length = (sum(lengths) / len(lengths))
            print("Promedio de la longitud del tallo:", average_length, "CM")
        if diameters:
            average_diameter = (sum(diameters) / len(diameters))
            print("Promedio del diámetro del tallo:", average_diameter, "CM")


        # Aquí se agrega el cálculo del Promedio diametro
        if diameters:
            promedio_diametro = sum(diameters) / len(diameters)
        else:
            promedio_diametro = 0
        print("Promedio diametro:", promedio_diametro, "CM")  


        if diameters:
            max_diameter = max(diameters)
        else:
            max_diameter = 0
        print("Diámetro máximo:", max_diameter, "CM")  

        if diameters:
            min_diameter = min(diameters)
        else:
            min_diameter = 0
        print("Promedio diametro menor:", min_diameter, "CM")


        # Agregar cálculo de la desviación estándar para la longitud
        if lengths:
            df_lengths = pd.DataFrame(lengths)
            desviacion_estandar_longitud = float(df_lengths.std()[0])
            print("La desviación estándar de la longitud es:", desviacion_estandar_longitud)
        else:
            desviacion_estandar_longitud = 0    

        if min_stem_length == float('inf'):
            min_stem_length = 0    

        self.max_esqueje = max_stem_length
        self.min_esqueje = min_stem_length
        print("El esqueje más largo mide:", self.max_esqueje, "CM")
        print("El esqueje más pequeño mide:", self.min_esqueje, "CM")
            
     
        return average_length, desviacion_estandar, stem_Long, stem_small, stem_good, average_diameter, desviacion_estandar_longitud, promedio_diametro,max_diameter, min_diameter
        
    def detect_area_foliar(self, folder_path):
        # Ruta de salida para guardar imágenes procesadas
        output_folder = r"C:\Users\juanl\OneDrive\Desktop\cuttingVision\Backend\areafoliar"

        # Intentar eliminar la carpeta si existe
        try:
           shutil.rmtree(output_folder)
        except FileNotFoundError:
            pass  # No hay problema si la carpeta no existe
        except PermissionError:
            print("⚠ No se pudo eliminar la carpeta, puede estar en uso.")

        os.makedirs(output_folder, exist_ok=True)  # Se recrea la carpeta

        # Listar archivos de imagen
        image_files = [f for f in os.listdir(folder_path) if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]

        # Lista para almacenar áreas foliares (en mm²)
        areas_mm2 = []
        failed_images = 0  # Contador de imágenes fallidas

        # Parámetros de escala
        scale_pixels_per_cm = 398  # píxeles por cm en la imagen original
        resize_factor = 3          # factor de ampliación aplicado a la imagen
        effective_pixels_per_cm = scale_pixels_per_cm * resize_factor
        conversion_factor = 100 / (effective_pixels_per_cm ** 2)

        for img_file in image_files:
            img_path = os.path.join(folder_path, img_file)
            img = cv2.imread(img_path)

            if img is None:
                print(f"⚠ No se pudo leer la imagen: {img_file}")
                failed_images += 1
                continue

            # Redimensionar imagen
            img = cv2.resize(img, None, fx=resize_factor, fy=resize_factor, interpolation=cv2.INTER_LINEAR)

            # Intentar aplicar binarización
            try:
               bin_img = self.binarize(img)
            except AttributeError:
                # En caso de error, usar umbralización manual
               gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
               _, bin_img = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

            # Contar píxeles blancos (zona foliar)
            white_pixels = cv2.countNonZero(bin_img)
            area = white_pixels * conversion_factor
            areas_mm2.append(area)

            # Dibujar contornos sobre la imagen original
            contours, _ = cv2.findContours(bin_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            img_contour = img.copy()
            cv2.drawContours(img_contour, contours, -1, (0, 255, 0), 2)

            # Guardar imagen procesada
            output_path = os.path.join(output_folder, f"processed_{img_file}")
            cv2.imwrite(output_path, img_contour)

        # Calcular el promedio del área foliar (en mm²)
        average_area = sum(areas_mm2) / len(areas_mm2) if areas_mm2 else 0
        print(f"✅ Promedio del área foliar: {average_area:.2f} mm²")

         # Calcular el área foliar máxima (mayor)
        max_area = max(areas_mm2) if areas_mm2 else 0
        print(f"✅ Área foliar mayor: {max_area:.2f} mm²")

        # Calcular el área foliar mínima (menor)
        min_area = min(areas_mm2) if areas_mm2 else 0
        print(f"✅ Área foliar menor: {min_area:.2f} mm²")

        # Calcular la desviación estándar del área foliar
        std_area = math.sqrt(sum((x - average_area) ** 2 for x in areas_mm2) / len(areas_mm2)) if areas_mm2 else 0
        print(f"✅ Desviación estándar del área foliar: {std_area:.2f} mm²")

        # Mensaje si hubo imágenes fallidas
        if failed_images > 0:
            print(f"⚠️ {failed_images} imágenes no pudieron procesarse.")

        # Almacenar el valor promedio en la clase
        self.average_area_foliar = average_area
        self.max_area_foliar = max_area
        self.min_area_foliar = min_area
        self.std_area_foliar = std_area

        return average_area,max_area,min_area,std_area
    
    ## NUEVA FUNCIÓN: Listar imágenes procesadas
    def list_detected_images(self):
        output_folder = r"C:\Users\mesacalidadpm\Desktop\MesaCalidad_V5\Backend\HBn"
        if not os.path.exists(output_folder):
            return []  # Si no existe la carpeta, se retorna una lista vacía
        image_files = [f for f in os.listdir(output_folder)
                       if os.path.isfile(os.path.join(output_folder, f))]
        return image_files
    

    ## NUEVA FUNCIÓN: Listar imágenes procesadas
    def list_detected_images1(self):
        output_folder = r"C:\Users\juanl\OneDrive\Desktop\cuttingVision\Backend\esquejescortos"
        if not os.path.exists(output_folder):
            return []  # Si no existe la carpeta, se retorna una lista vacía
        image_files = [f for f in os.listdir(output_folder)
                       if os.path.isfile(os.path.join(output_folder, f))]
        return image_files
    
     ## NUEVA FUNCIÓN: Listar imágenes procesadas
    def list_detected_images2(self):
        output_folder = r"C:\Users\juanl\OneDrive\Desktop\cuttingVision\Backend\esquejes_largos"
        if not os.path.exists(output_folder):
            return []  # Si no existe la carpeta, se retorna una lista vacía
        image_files = [f for f in os.listdir(output_folder)
                       if os.path.isfile(os.path.join(output_folder, f))]
        return image_files
    

        

 