import os
import threading
import cv2
import time
from detect import Detect
from process_img import ImgProcess


class Run_on_pic:  #Ejecutar algoritmos de en fotografia
    def __init__(self) -> None:
        self.detect = Detect()
        self.process = ImgProcess()

    def run_pic(self,img, variedad, cosechador):
        img_results = img.copy()
        binImg_list = []
        img_cuttings, cutImg_list, box_list = self.detect.det_cutting(img)
        stem_count = len(cutImg_list)
        print(stem_count)
        start_time = time.time()
        list_length = []
        list_diameter = []
        list_fitness = []

        for index, img in enumerate(cutImg_list):
            bin_img=self.process.binarize_img(img)
            binImg_list.append(bin_img)
            binary_img_rgb = cv2.cvtColor(bin_img, cv2.COLOR_GRAY2RGB)
            stem_det_img, angle, detect_ckeck = self.detect.detect_stem(binary_img_rgb, draw=False)
            rot_img = self.process.rotate_img(stem_det_img, angle)
            clean_img = self.process.clean_img(rot_img)
            meassure_img, cutting_lengt, cutting_diameter, fitness = self.process.meassure(clean_img, 1.52)
            list_length.append(cutting_lengt)
            list_diameter.append(cutting_diameter)
            list_fitness.append(fitness)

        results_img = self.process.results(img_results, box_list, list_length, list_diameter, list_fitness)
        width, height = results_img.shape[:2]
        width, height = int(width*0.5), int(height*0.5)
        results_img = cv2.resize(results_img,(height,width))
        self.process.store_data(list_length, list_diameter, list_fitness,variedad,cosechador)

        return stem_count, results_img, list_fitness
    

    
    def run(self):
        start_time = time.time()
        run_on_pic = Run_on_pic()
        folder_capture = "uploads"
        img_list = []
        fitness_list = []
        stem_total_count = 0
        if os.path.exists(folder_capture):
            for filename in os.listdir(folder_capture):
                img = cv2.imread(f'{folder_capture}/{filename}')
                stem_count, result_img, fitness = run_on_pic.run_pic(img,'multisol',0)
                img_list.append(result_img)
                for fit in fitness:
                    fitness_list.append(fit)
                stem_total_count += stem_count
        result_image_list = [img_list[3],img_list[0],img_list[1],img_list[2]]
        stitched_image = cv2.hconcat(result_image_list)    
        true_count = fitness_list.count(True)
        fit_total_count = len(fitness_list)
        fitness_percentage = (true_count / fit_total_count) * 100
        end_time = time.time()
        running_time = end_time - start_time
        cv2.imshow('results', result_image_list)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        print("Running time:", running_time, "sec") 

        print(f'true count: {true_count}')
        print(f'total count: {fit_total_count}')
        print(f'percentage: {fitness_percentage}')

        #for index, img in enumerate(result_image_list):
        #    cv2.imshow(f'image {index}', img)
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()
        return stem_total_count, true_count, fitness_percentage, stitched_image

if __name__ == '__main__':
    run_on_pic = Run_on_pic()
    run_on_pic.run()