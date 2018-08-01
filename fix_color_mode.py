from glob import glob
import argparse
from PIL import Image
from tqdm import tqdm


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_path', type=str, required=True,
                        help='''Path to input folder containing PNG images''')
    return parser.parse_args()


def fix(input_path):
  print("Fixing color mode for PNG images in " + input_path + "...")
  for file_name in tqdm(glob(input_path + "/*.png")):
    try:
      image = Image.open(file_name).convert('RGBA')
      image.save(file_name, "PNG")
    except Exception as error:
      print("Error in file: " + file_name + " [" + str(error) + "]")


if __name__ == "__main__":
  args = parse_arguments()

  fix(args.input_path)
