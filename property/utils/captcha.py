import random
import string
from PIL  import Image,ImageDraw,ImageFont
from io import BytesIO
import  base64
import uuid
from django.http import HttpResponse
from rest_framework.permissions import BasePermission
from django.core.cache import cache
from rest_framework.response import Response

# cache base captcha
def get(self,request):
    """Genereat cache base cpatcha  for login register user wchich not save in database, and varify captcha using captcha key """
    captcha = "".join(random.choices(string.ascii_uppercase + string.digits , key=6))
    captcha_key = f"captcha_{random.randint(uuid.uuid4().hex)}"

    # set captcha timeout
    cache.set(captcha_key,captcha,timeout=43200)
    return Response({
        "captcha_key":captcha_key,
        "captcha":captcha                       #generate captcha image
    })




# Generate captcha image with colore
def gen_cap_img(cap_text):
    image = Image.new("RGB",(120,40),color=(255,255,255))
    draw = ImageDraw.Draw(image)

    try:
        fontimg = ImageFont.truetype("arial.ttf",28)
    except:
        fontimg = ImageFont.load_default()
    
    draw.text((10,5) , cap_text,fill="black",font=fontimg) 
    buffer = BytesIO()
    image.save(buffer,format="PNG")
    buffer.seek(0)
    return HttpResponse( buffer.getvalue(),content_type="image/png")
    
