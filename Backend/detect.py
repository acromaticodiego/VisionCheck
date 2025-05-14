import os
import cv2
from ultralytics import YOLO
from ultralytics.nn.tasks import Detect
import numpy as np

class Detect:
    def __init__(self) -> None:
        #Cargar Modelo Detect
        print('Cargando Modelo Detect...')
        self.model = YOLO('100EPOCHS_V2.onnx', task='detect')
        #self.model = YOLO('Backend/100EPOCHS_V2.onnx', task='detect')
        print('modelo cargado')

        print('Cargando Modelo Stem...')
        self.model_stem = YOLO('Stem_Segmentation_V7_Bin.pt', task='segment')
        #self.model_stem = YOLO('Backend/Stem_Segmentation_V7_Bin.pt', task='segment')
        print('modelo cargado')

    def det_cutting(self, image):
        self.dis_img = image.copy()
        self.cutImg_list=[]
        results = self.model(image)
        self.box_list = []
        for result in results:
            self.boxes = result.boxes
            for box in result.boxes.xyxy:
                x_min, y_min, x_max, y_max = box
                x_min=int(x_min)
                x_max=int(x_max)
                y_min=int(y_min)
                y_max=int(y_max)
                cv2.rectangle(self.dis_img, (x_min, y_min), (x_max, y_max), (255, 0, 0), 2)
                self.crop_img = image[y_min:y_max, x_min:x_max]
                self.cutImg_list.append(self.crop_img)
                self.box_list.append(box)

            
            width, height = self.dis_img.shape[:2]
            print(width,height)
            width, height = int(width*0.4), int(height*0.4)
            self.dis_img = cv2.resize(self.dis_img,(height,width))

        return self.dis_img, self.cutImg_list, self.box_list

    def detect_stem(self,image,draw):
        self.results = self.model_stem(image)
        self.img_results=image.copy()
        self.angle = 0
        detect = False #Confirmar derección
        
        if(self.results[0].masks is not None):
            detect = True
            # Convertir imagen a un solo canal
            mask_raw = self.results[0].masks[0].cpu().data.numpy().transpose(1, 2, 0)
            mask_3channel = cv2.merge((mask_raw,mask_raw,mask_raw)) 

            # Extraer dimensiones
            h1, w1, c2 = self.results[0].orig_img.shape

            #print(f'original size ({h1},{w1})')
            # Resize mascara
            mask = cv2.resize(mask_3channel, (w1, h1))
            # BGR a HSV
            hsv = cv2.cvtColor(mask, cv2.COLOR_BGR2HSV)

            # HSV fronteras
            lower_black = np.array([0,0,0])
            upper_black = np.array([0,0,1])

            # Combinación de mascaras
            mask = cv2.inRange(mask, lower_black, upper_black)
            mask_inv = cv2.bitwise_not(mask)

            contours, _ = cv2.findContours(mask_inv, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
            min_area_rects = [cv2.minAreaRect(contours[0])]
            (_, (h_box, w_box), _) = min_area_rects[0] #Extraer dimension de caja
            #print(f'box size ({h_box},{w_box})')

            area_org = h1*w1
            area_box = h_box*w_box
            area_per = (area_box*100)//area_org #Calcular porcentaje de caja

            print(f'box area percentage {area_per}')
            
            if area_per > 3: #Verificar que el area sea mayor a 3%
                for rect in min_area_rects:
                    box = cv2.boxPoints(rect)
                    box = box.astype('int')
                    self.angle = rect[2]

                    center = rect[0]
                    center = (int(center[0]), int(center[1]))
                    
                    if(self.angle<45):
                        width_rect = rect[1][0]
                        angle_rad = np.deg2rad(self.angle)
                        end_x = int(center[0] + width_rect * np.sin(angle_rad))
                        end_y = int(center[1] - width_rect * np.cos(angle_rad))
                    else:
                        width_rect = rect[1][1]
                        angle_rad = np.deg2rad(self.angle)
                        end_x = int(center[0] - width_rect * np.cos(angle_rad))
                        end_y = int(center[1] - width_rect * np.sin(angle_rad))

                    if(draw): #Dibujar cuadro y ángula (Debug)
                        cv2.drawContours(self.img_results, [box], 0, (0, 255, 0), 2)  # Green color with thickness 2
                        image = cv2.circle(self.img_results, center, radius=6, color=(0, 0, 255), thickness=-1)
                        cv2.line(self.img_results, center, (end_x, end_y), color=(0, 0, 255), thickness=2)
            else:
                print('False Detection')
                self.angle = 0
                detect = False
        return self.img_results, self.angle, detect
