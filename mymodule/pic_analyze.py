from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time
import cv2
import base64
import numpy as np
import pytesseract
import io
from pytesseract import Output
from PIL import Image
from io import StringIO
import os
from django.conf import settings
pytesseract.pytesseract.tesseract_cmd = r'C://Program Files (x86)//Tesseract-OCR//tesseract.exe'
tessdata_dir_config = '--tessdata-dir "C://Program Files (x86)//Tesseract-OCR//tessdata"'

def analystPicture(pics,word,id_list):
    loca=[]
    n = 0 
    file_list=[]
    for pic in pics:  
       img = base64.b64decode(pic); 
       npimg = np.fromstring(img, dtype=np.uint8); 
       img = cv2.imdecode(npimg, 1)
       d = pytesseract.image_to_data(img, output_type=Output.DICT, config=tessdata_dir_config)
       n_boxes = len(d['level'])
       overlay = img.copy()
       for i in range(n_boxes):
          text = d['text'][i]
          if word in text.lower():
            (x1, y1, w1, h1) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
            loca.append([x1, y1, w1, h1])
            cv2.rectangle(overlay, (x1, y1), (x1 + w1, y1 + h1), (255, 0, 0), -1)
       alpha = 0.4  # Transparency factor.
       img_new = cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)
    
       filename= settings.MEDIA_ROOT +'/picture/' + id_list[n]+".png"
       if(len(loca)>0):
         file_list.append(filename)

       n+=1
       cv2.imwrite(filename,img_new)
     

    return file_list


def Analyze(web,list_form,word):
  options = Options()
  options.headless = True
  profile = webdriver.FirefoxProfile()
  profile.DEFAULT_PREFERENCES['frozen']['javascript.enabled'] = False
  profile.update_preferences()

  driver = webdriver.Firefox(
    firefox_profile=profile,
    options=options
  )
  driver.get(web)
  all_image=[]
  for w in list_form:
    image = driver.find_elements_by_xpath("//*[text()[contains(.,'"+w+"')]]")

    for index,value in enumerate(image):
      if(value.text!=''):
        list_text=value.text.split(' ')
        out=10
        while(len(list_text)<10):
          try:
           image[index]=value.find_elements_by_xpath("..")[0]
           text = image[index].text
           list_text = text.split(' ')
           if(out==0):
              out=10
              break
           else:
              out-=1

          except:
           if(out==0):
             out=10
             break
           else:
             out-=1
    all_image=all_image+image 
  
  test=[]
  for index,value in enumerate(all_image):
      list_sub = [x.id for x in value.find_elements_by_xpath(".//*")]
      test = test+[y.id for y in all_image if y.id in list_sub and y.id not in test and value.id!=y.id]

  final=[]
  final = list(dict.fromkeys(test))
  
  for index,value in enumerate(all_image):
    if(value.id in final):
      all_image[index]=None
    
  list_bs64=[]
  id_list=[]
  all_image =  list(dict.fromkeys(all_image))
 
        
  for i in all_image:
    try:
      id_list.append(i.id)
      list_bs64.append(i.screenshot_as_base64)
    except Exception as e:
      print(e)  

  pic_list=[]
  try: 
    pic_list = analystPicture(list_bs64,word,id_list)
  except Exception as e:
    print(e) 
  return pic_list