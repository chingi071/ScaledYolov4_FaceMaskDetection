import os
import shutil
from bs4 import BeautifulSoup
import math

def run_convert(all_classes, train_img, train_annotation, yolo_path, write_train_txt, write_val_txt):
    now_path = os.getcwd()
    data_counter = 0

    for data_file in os.listdir(train_annotation):
        try:
            with open(os.path.join(train_annotation, data_file), 'r') as f:
                print("read file...")
                soup = BeautifulSoup(f.read(), 'xml')
                img_name = soup.select_one('filename').text

                for size in soup.select('size'):
                    img_w = int(size.select_one('width').text)
                    img_h = int(size.select_one('height').text)
                    
                img_info = []
                for obj in soup.select('object'):
                    xmin = int(obj.select_one('xmin').text)
                    xmax = int(obj.select_one('xmax').text)
                    ymin = int(obj.select_one('ymin').text)
                    ymax = int(obj.select_one('ymax').text)
                    objclass = all_classes.get(obj.select_one('name').text)

                    x = (xmin + (xmax-xmin)/2) * 1.0 / img_w
                    y = (ymin + (ymax-ymin)/2) * 1.0 / img_h
                    w = (xmax-xmin) * 1.0 / img_w
                    h = (ymax-ymin) * 1.0 / img_h
                    img_info.append(' '.join([str(objclass), str(x),str(y),str(w),str(h)]))

                # copy image to yolo path and rename
                img_path = os.path.join(train_img, img_name)
                img_format = img_name.split('.')[1]  # jpg or png
                shutil.copyfile(img_path, yolo_path + str(data_counter) + '.' + img_format)
                
                # create yolo bndbox txt
                with open(yolo_path + str(data_counter) + '.txt', 'a+') as f:
                    f.write('\n'.join(img_info))

                data_counter += 1
                    
        except Exception as e:
            print(e)
           
    print('the file is processed')

    # create train and val txt
    path = os.path.join(now_path, yolo_path)
    datasets = []
    for idx in os.listdir(yolo_path):
        if not idx.endswith('.txt'):
            idx_path = path + idx
            datasets.append(idx_path)

    len_datasets = math.floor(len(datasets)*0.8)
    with open(write_train_txt, 'a') as f:
        f.write('\n'.join(datasets[0:len_datasets]))

    with open(write_val_txt, 'a') as f:
        f.write('\n'.join(datasets[len_datasets:]))

all_classes = {'mask_weared_incorrect': 2, 'without_mask': 1, 'with_mask': 0}
train_img = "Face_Mask_data/images"
train_annotation = "Face_Mask_data/annotations"
yolo_path = "yolo_data/"
write_train_txt = 'yolov4-csp/data/train.txt'
write_val_txt = 'yolov4-csp/data/val.txt'

if not os.path.exists(yolo_path):
    os.mkdir(yolo_path)
else:
    lsdir = os.listdir(yolo_path)
    for name in lsdir:
        if name.endswith('.txt') or name.endswith('.jpg') or name.endswith('.png'):
            os.remove(os.path.join(yolo_path, name))

cfg_file = write_train_txt.split('/')[0]
if not os.path.exists(cfg_file):
    os.mkdir(cfg_file)
    
if os.path.exists(write_train_txt):
    file=open(write_train_txt, 'w')

if os.path.exists(write_val_txt):
    file=open(write_val_txt, 'w')

run_convert(all_classes, train_img, train_annotation, yolo_path, write_train_txt, write_val_txt)