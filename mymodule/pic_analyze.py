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
pytesseract.pytesseract.tesseract_cmd = r'C://Program Files (x86)//Tesseract-OCR//tesseract.exe'
tessdata_dir_config = '--tessdata-dir "C://Program Files (x86)//Tesseract-OCR//tessdata"'



def Analyze(web,words):
  options = Options()
  options.headless = False
  profile = webdriver.FirefoxProfile()
  profile.DEFAULT_PREFERENCES['frozen']['javascript.enabled'] = False
  
  profile.update_preferences()

  driver = webdriver.Firefox(
    firefox_profile=profile,
    options=options
  )
  driver.get(web.name)
  width = driver.execute_script("return document.body.offsetWidth;")
  height = driver.execute_script("return document.body.offsetHeight;")
 
  time.sleep(2)
  driver.set_window_size(width,height)
  for w in words:
    image = driver.find_elements_by_xpath('//*[text()[contains(.,"'+w+'")]]')
    
    for img in image:
      text = img.get_attribute('innerHTML')
      new = "<a style='background: yellow; border: 2px solid red;'>"+w+"</a>"
      text = text.replace(w,new)
      driver.execute_script("arguments[0].innerHTML=arguments[1]",img,text) 
  file_name = settings.MEDIA_ROOT + '/picture/'+web.id+'.png'
  driver.save_screenshot(file_name)
 
  
  driver.close()
  return file_name
