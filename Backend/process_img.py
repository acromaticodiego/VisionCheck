import math
import os
import cv2
import numpy as np
import random
import csv
from datetime import datetime

class ImgProcess:
    def __init__(self) -> None:
        pass

    def binarize_img(self, img):
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        #_, th1 = cv2.threshold(gray_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        _, th1 = cv2.threshold(gray_img, 75, 255, cv2.THRESH_BINARY)
        img_fill = th1.copy()
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5))
        for i in range(3):
            img_fill = cv2.morphologyEx(img_fill,cv2.MORPH_OPEN,kernel)

        return img_fill
    
   
    def rotate_img(self, img, angle):
        height, width = img.shape[:2]
        image_center = (width / 2, height / 2)

        if angle > 45:
            angle_rot=angle-90
        else:
            angle_rot=angle
        
        #print('rotated: ', angle_rot,'°')
        rotation_mat = cv2.getRotationMatrix2D(image_center, angle_rot, 1)

        radians = math.radians(angle_rot)
        sin = math.sin(radians)
        cos = math.cos(radians)
        bound_w = int((height * abs(sin)) + (width * abs(cos)))
        bound_h = int((height * abs(cos)) + (width * abs(sin)))

        rotation_mat[0, 2] += ((bound_w / 2) - image_center[0])
        rotation_mat[1, 2] += ((bound_h / 2) - image_center[1])
        
        img = cv2.bitwise_not(img) #invertir imagen para coincidir bkgnd negro
        output_img = cv2.warpAffine(img, rotation_mat, (bound_w, bound_h))
        #output_img = cv2.bitwise_not(rotated) #Invertir para tener bkgnd blanco de nuevo

        return output_img
        
    def clean_img(self, img):
        display_image=img.copy()
        # Find contours
        img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        contours, _ = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        #cv2.drawContours(display_image, contours, -1, (0,255,0), 3)
        # Filter contours to identify the main shape
        main_contour = None
        max_contour_area = 0

        for contour in contours:
            area = cv2.contourArea(contour)
            if area > max_contour_area:
                max_contour_area = area
                main_contour = contour

        # Create a mask for the main shape
        mask = np.zeros_like(img)
        if main_contour is not None:
            cv2.drawContours(mask, [main_contour], -1, (255, 255, 255), thickness=cv2.FILLED)

        # Apply the mask to the original image
        result = cv2.bitwise_and(display_image, display_image, mask=mask)
        return result
    
    def meassure(self, img, scale):
        top_dis=0
        bottom_dis=0
        self.display_img = img.copy()
        height, width = img.shape[:2]

        for y in range(height):
            num_white_pixels = cv2.countNonZero(img[y])
            
            if num_white_pixels > 0:
                cv2.line(self.display_img, (0, y), (width-1, y), (0, 0, 255), 2)
                top_dis=y
                #print("distancia top: ", y)
                
                break


        for y in range(height-1, -1, -1):

            num_white_pixels = cv2.countNonZero(img[y])

            if num_white_pixels > 0:
                bottom_dis=y
                cv2.line(self.display_img, (0, y), (width-1, y), (0, 0, 255), 2)
                #print("distancia bottom: ", y)
                break
        
        dist=bottom_dis-top_dis
        dist_mm=dist/scale 
        dist_mm = round(dist_mm, 2)
        #Calculo de diametro
        top_per=0.8  #Porcentaje frontera top
        bottom_per=0.95 #Porcentaje frontera bottom
        bound_top=int(top_dis+dist*top_per)
        bound_bottom=int(top_dis+dist*bottom_per)
        
        white_pixels = []
        for y in range(bound_top+1, bound_bottom):
            white_pixel_count = 0
            for x in range(width):
                if img[y, x,0] == 255:
                    self.display_img[y, x] = [255, 0, 0]
                    white_pixel_count+=1
            white_pixels.append(white_pixel_count)
        if sum(white_pixels) > 0:
            diameter=sum(white_pixels)/len(white_pixels)
        else:
            diameter = 0
        diameter_mm=diameter/scale
        diameter_mm = round(diameter_mm, 2)
        print(f'diameter px: {diameter}   diameter mm: {diameter_mm}')
        print(f'length px: {dist}   lenght mm: {dist_mm}')
        fitness = random.choice([True, False])
        return self.display_img, dist_mm, diameter_mm, fitness
    
    def results(self, img, box_list, list_length, list_diameter, list_fitness):
        result_image = img.copy()
        for index, box in enumerate(box_list):
            x_min, y_min, x_max, y_max = box
            x_min=int(x_min)
            x_max=int(x_max)
            y_min=int(y_min)
            y_max=int(y_max)
            color = (0,0,0)
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.5
            thickness = 2
            if list_fitness[index] == True:
                color = (34,139,34)
            else:
                color = (0, 0, 255)
            cv2.rectangle(result_image, (x_min, y_min), (x_max, y_max), color, 2)
            cv2.putText(result_image, f"L: {list_length[index]} mm", (x_min+10, y_min+15), font, font_scale, color, thickness)
            cv2.putText(result_image, f"D: {list_diameter[index]} mm", (x_min+10, y_min+30), font, font_scale, color, thickness)

        return result_image
    
    def store_data(self, list_length, list_diameter, list_fitness,variedad, cosechador):
        
        with open('data_results.csv', mode='a', newline='') as file:
            date_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            writer = csv.writer(file)
            for i, _ in enumerate(list_length):
                data = [date_time, list_length[i], list_diameter[i], list_fitness[i],variedad,cosechador]
                writer.writerow(data)