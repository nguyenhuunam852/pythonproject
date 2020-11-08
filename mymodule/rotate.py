from PIL import Image

def rotate_img(img_path, rt_degr):
    img = Image.open(img_path)
    return img.rotate(rt_degr, expand=1)
