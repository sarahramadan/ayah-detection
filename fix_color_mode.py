import sys
import glob
from PIL import Image
from tqdm import tqdm
image_dir = sys.argv[1]
print("Fixing color mode for PNG images in " + image_dir + "...")
for file_name in tqdm(glob.glob(image_dir + "/*.png")):
  try:
    image = Image.open(file_name).convert('RGBA')
    image.save(file_name, "PNG")
  except Exception as error:
    print("Error in file: " + file_name + " [" + str(error) + "]")
