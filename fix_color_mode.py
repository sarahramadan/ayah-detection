import sys
from PIL import Image
for i in range(1,605):
   image_dir = sys.argv[1] + '/'
   #filename = "001_Page_"+str(i).zfill(2) + '.jpg'
   filename = str(i) + '.png'   
   # find lines
   image = Image.open(image_dir + filename).convert('RGBA')
   image.save(image_dir + filename,"PNG");
