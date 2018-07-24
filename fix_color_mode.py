import sys
import glob
from PIL import Image
image_dir = sys.argv[1]
print("Fixing color mode for PNG images in " + image_dir + "...")
for file_name in glob.glob(image_dir + "/*.png"):
  print(file_name)
  image = Image.open(file_name).convert('RGBA')
  image.save(file_name, "PNG");
print("Done fixing color mode for PNG images in " + image_dir)
