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
from selenium.webdriver.common.action_chains import ActionChains

from mymodule.rotate import rotate_img


def Analyze(web,words):
  options = Options()
  options.headless = True
  profile = webdriver.FirefoxProfile()
  profile.DEFAULT_PREFERENCES['frozen']['javascript.enabled'] = False
  
  profile.update_preferences()
  try:
   driver = webdriver.Firefox(
    firefox_profile=profile,
    options=options
   )
  except Exception as e:
    print(e)
  driver.set_page_load_timeout(10)
  driver.get(web.name)
  width = driver.execute_script("return document.body.offsetWidth;")
  height = driver.execute_script("return document.body.offsetHeight;")
  
  time.sleep(2)
   
  for w in words:
    image = driver.find_elements_by_xpath('//*[text()[contains(.,"'+w+'")]]')
    try:
     for img in image:
      try: 
       if(img.tag_name!='script' and img.text!=''):
        try:
         text = img.get_attribute('innerHTML')
         new = "<span style='background: yellow; border: 2px solid red;'>"+w+"</span>"
         text = text.replace(w,new)
         driver.execute_script("arguments[0].innerHTML=arguments[1]",img,text) 
        except Exception as e:
         print(e)
      except Exception as e:
       print(e)
    except Exception as e:
       print(e)
  file_name = settings.MEDIA_ROOT + '/picture/'+str(web.id)+'.png'
  driver.set_window_size(width,height)
  driver.save_screenshot(file_name)
  img_rt_90 = rotate_img(file_name, 90)
  img_rt_90.save(file_name)
  driver.close()
  return file_name
