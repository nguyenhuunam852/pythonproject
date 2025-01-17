from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import time
import cv2
import base64
import numpy as np
import io
from PIL import Image
from io import StringIO
import os
from django.conf import settings
from selenium.webdriver.common.action_chains import ActionChains

from mymodule.rotate import rotate_img
import random
import string

def get_random_string(length):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str
def Analyze(web,words,oldfile):
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
    driver.close()
    print(e)
  try:
   driver.set_page_load_timeout(20)
   driver.get(web.name)
   width = driver.execute_script("return document.documentElement.offsetWidth;")
   height = driver.execute_script("return document.documentElement.scrollHeight;")
  
   for w in words:
    image = driver.find_elements_by_xpath('//*[text()[contains(.,"'+w+'")]]')
    try:
     for img in image:
      try: 
       if(img.tag_name!='script' and img.text!=''):
        try:
         text = img.get_attribute('innerHTML')
         import re
         verify = []
         text1 = " "+text+" "
         verify = re.findall('[^a-zA-Z0-9]'+w+'[^a-zA-Z0-9]',text1)
      
         for vword in verify: 
            new = "<span style='background: yellow; border: 2px solid red;'>"+w+"</span>"
            nword = vword.replace(w,new)
            text = text.replace(w,nword)
            driver.execute_script("arguments[0].innerHTML=arguments[1]",img,text) 
        except Exception as e:
         print(e)
      except Exception as e:
       print(e)
    except Exception as e:
       print(e)
   if(oldfile!=""):
      import os
      os.remove(settings.MEDIA_ROOT + '/picture/' + oldfile)
   file_name = settings.MEDIA_ROOT + '/picture/'+get_random_string(8)+'.png'
   driver.execute_script("window.scrollTo(0, "+str(height/2)+"); ")
   driver.set_window_size(width,height)
   driver.save_screenshot(file_name)
   img_rt_90 = rotate_img(file_name, 90)
   img_rt_90.save(file_name)
   driver.close()
   return file_name
  except Exception as e:
     driver.close()
     print(e)