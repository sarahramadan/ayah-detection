import os
import random
import argparse
from PIL import Image
from PIL import ImageDraw
from tqdm import trange
from lines import find_lines2
from utils import safe_makedir, save_lines


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_path', type=str, required=True,
                        help='''Path to input folder containing PNG images''')
    parser.add_argument('--output_path', type=str, required=True,
                        help='''Path to output folder to generate verification images in''')
    parser.add_argument('--start_page', type=int, default=1,
                        help='''Start page, default = 1''')
    parser.add_argument('--end_page', type=int, default=604,
                        help='''End page, default = 604''')
    return parser.parse_args()


def main_find_lines(start_page, end_page, input_path, output_path):
  def r(): return random.randint(0, 255)

  # warsh: 1, 560 (last page: 559)
  # shamerly: 2, 523 (last page: 522) - lines to skip: 3 (2 + 1 basmala)
  # qaloon: 1, 605 (last page: 604) - lines to skip: 2 (1 + 1 basmala)
  all_pages_lines = []
  for i in trange(start_page, end_page + 1):
    filename = str(i) + '.png'
    # find lines
    image = Image.open(input_path + filename).convert('RGBA')
    #converting transperant color to white
    image.load()  # needed for split()
    background = Image.new('RGB', image.size, (255, 255, 255))
    background.paste(image, mask=image.split()[3])
    image = background
    # note: these values will change depending on image type and size
    # warsh: 100/35/0, shamerly: 110/87/0, 175/75/1 for qaloon
    #sample-white: 30/20/0, sample-transperant: 30/15/0, amma: 110/75/0
    #quran: 76/15/0

    if i == 1:
      lines = find_lines2(image, 8)
    elif i == 2:
      lines = find_lines2(image, 8)
    else:
      lines = find_lines2(image, 15)

    # ***** Align lines starts and ends *****************
    index = 0
    l1 = None
    drawMe = ImageDraw.Draw(image, "RGBA")
    for line in lines:
      lines[index] = ((0, line[0][1]), (background.size[0], line[1][1]))
      if l1 is not None and line[0][1] > (l1[1][1] + 1):
        lines[index] = ((lines[index][0][0], l1[1][1] + 1),
                        (lines[index][1][0], lines[index][1][1]))
      l1 = lines[index]
      drawMe.rectangle(lines[index], fill=(r(), r(), r(), 100))
      index += 1
    del drawMe
    image.save(output_path + str(i).zfill(3) + ".png", "PNG")
    all_pages_lines.append(lines)
  return all_pages_lines


if __name__ == "__main__":
  args = parse_arguments()

  input_path = args.input_path + '/'
  output_path = safe_makedir(args.output_path + '/lines/')

  print("Splitting pages to lines into " + output_path + "...")
  lines = main_find_lines(start_page=args.start_page,
                          end_page=args.end_page,
                          input_path=input_path,
                          output_path=output_path)

  save_lines(args.output_path, lines)
