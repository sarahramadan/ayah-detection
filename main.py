import sys
import random
import argparse
import cv2
from PIL import Image
from PIL import ImageDraw
from verses_count import verses_count
from lines import find_lines, find_lines2,find_lines3
from ayat import find_ayat, draw, output_aya_segment


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_path', type=str, required=True,
                        help='''Path to input folder containing PNG images''')
    parser.add_argument('--output_path', type=str, required=True,
                        help='''Path to output folder to generate verification images in''')
    parser.add_argument('--separator1_path', type=str, required=True,
                        help='''Path to separator image template for pages 1 and 2''')
    parser.add_argument('--separator3_path', type=str, required=True,
                        help='''Path to separator image template for pages 3 up to the end''')
    parser.add_argument('--count_method', type=str, choices=list(verses_count.keys()), required=True,
                        help='''Counting method to use''')
    parser.add_argument('--start_page', type=int, default=1,
                        help='''Start page, default = 1''')
    parser.add_argument('--end_page', type=int, default=604,
                        help='''End page, default = 604''')
    parser.add_argument('--start_sura', type=int, default=1,
                        help='''Start sura number, default = 1''')
    parser.add_argument('--start_aya', type=int, default=1,
                        help='''Start aya number, default = 1''')
    return parser.parse_args()

args = parse_arguments()

image_dir = args.input_path + '/'
out_folder = args.output_path + '/'
count_ayat = verses_count[args.count_method]
sura = args.start_sura
ayah = args.start_aya
lines_to_skip = 0
default_lines_to_skip = 2

# by default, we don't increase the ayah on the top of this loop
# to handle ayat that span multiple pages - this flag allows us to
# override this.
end_of_ayah = False
def r(): return random.randint(0, 255)
# warsh: 1, 560 (last page: 559)
# shamerly: 2, 523 (last page: 522) - lines to skip: 3 (2 + 1 basmala)
# qaloon: 1, 605 (last page: 604) - lines to skip: 2 (1 + 1 basmala)
#sura: 1,6
for i in range(args.start_page, args.end_page + 1):
  filename = str(i) + '.png'
  print filename
  print image_dir + filename
  # find lines
  image = Image.open(image_dir + filename).convert('RGBA')
  #converting transperant color to white
  image.load()  # needed for split()
  background = Image.new('RGB', image.size, (255,255,255))
  background.paste(image, mask=image.split()[3])
  image = background
  # note: these values will change depending on image type and size
  # warsh: 100/35/0, shamerly: 110/87/0, 175/75/1 for qaloon
  #sample-white: 30/20/0, sample-transperant: 30/15/0, amma: 110/75/0
  #quran: 76/15/0
  #sura

  if i == 1:
    lines = find_lines2(image, 8)
  elif i == 2:
    lines = find_lines2(image, 8)
  else:
    lines = find_lines2(image, 15)
#   lines = find_lines(image, 80, 20, 1)
#   lines = find_lines3(image)
  print 'found: %d lines on page %d' % (len(lines), i)

  # ***** Align lines starts and ends *****************
  index = 0
  l1 = None
  drawMe = ImageDraw.Draw(image,"RGBA")
  for line in lines:
    lines[index] = ((0, line[0][1]), (background.size[0], line[1][1]))
    if l1 is not None and line[0][1] > (l1[1][1] + 1):
      lines[index] = ((lines[index][0][0], l1[1][1] + 1), (lines[index][1][0], lines[index][1][1]))
    l1 = lines[index]
    drawMe.rectangle(lines[index],fill=(r(),r(),r(),100))
    index += 1
  del drawMe
  image.save(out_folder + str(i).zfill(3) + 'output.png', "PNG")
  # **************************************************

  #img_rgb = cv2.imread(image_dir + filename)
  #img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
  img_gray = cv2.imread(image_dir + filename, -1)
  if i == 1 or i == 2:
    template = cv2.imread(args.separator1_path, -1)
  else:
    template = cv2.imread(args.separator3_path, -1)

  ayat = find_ayat(img_gray, template)
  print 'found: %d ayat on page %d' % (len(ayat), i)

  tpl_width = template.shape[1]
  tpl_height = template.shape[0]

  current_line = 0
  x_pos_in_line = -1
  num_lines = len(lines)

  first = True
  for ayah_item in ayat:
    if ((end_of_ayah or not first) and count_ayat[sura - 1] == ayah):
      sura = sura + 1
      ayah = 1
      lines_to_skip = default_lines_to_skip
      if sura == 9:
        lines_to_skip = lines_to_skip - 1
      end_of_ayah = False
    elif (end_of_ayah or not first):
      ayah = ayah + 1
      end_of_ayah = False
    first = False
    y_pos = ayah_item[1]

    pos = 0
    for line in range(current_line, num_lines):
      cur_line = lines[line]
      miny = cur_line[0][1]
      maxy = cur_line[1][1]
      cur_line_minx = cur_line[0][0]
      cur_line_maxx = cur_line[1][0]
      if lines_to_skip > 0:
        if lines_to_skip == 2: # header
          vals = (i, line + 1, sura, -1, 1, cur_line_minx, cur_line_maxx, miny, maxy)
        elif lines_to_skip == 1 and sura ==9: # header of tawba
          vals = (i, line + 1, sura, -1, 1, cur_line_minx, cur_line_maxx, miny, maxy)
        else: # basmala
          vals = (i, line + 1, sura, 0, 1, cur_line_minx, cur_line_maxx, miny, maxy)
        output_aya_segment(vals, img_gray)
        lines_to_skip = lines_to_skip - 1
        current_line = current_line + 1
        continue
      pos = pos + 1
      if y_pos <= maxy:
        # we found the line with the ayah
        maxx = cur_line_maxx
        if x_pos_in_line > 0:
          maxx = x_pos_in_line
        minx = ayah_item[0]
        if minx < tpl_width/2: # small value indicating that the separator is the last thing comes in line
          minx = 0
        end_of_sura = False
        if count_ayat[sura - 1] == ayah:
          end_of_sura = True

        # last aya in sura segment must extend to the leftmost, the empty space is ugly
        # also last ayah in page 2 must extend to the leftmost
        if end_of_sura or i == 2 and ayah_item == ayat[-1]:
          minx = 0

        vals = (i, line + 1, sura, ayah, pos, minx, maxx, miny, maxy)
        output_aya_segment(vals, img_gray)

        if end_of_sura or abs(minx - cur_line_minx) < tpl_width/2:
          x_pos_in_line = -1
          current_line = current_line + 1
          if current_line == num_lines:
            # last line, and no more ayahs - set it to increase
            end_of_ayah = True
        else:
          x_pos_in_line = minx
        break
      else:
        # we add this line
        maxx = cur_line_maxx
        if x_pos_in_line > 0:
          maxx = x_pos_in_line
        x_pos_in_line = -1
        current_line = current_line + 1
        vals = (i, line + 1, sura, ayah, pos, cur_line_minx, maxx,
              miny, maxy)
        output_aya_segment(vals, img_gray)

  # draw aya separators
  draw(img_gray, template, ayat)

  # handle cases when the sura ends on a page, and there are no more
  # ayat. this could mean that we need to adjust lines_to_skip (as is
  # the case when the next sura header is at the bottom) or also add
  # some ayat that aren't being displayed at the moment.
  if end_of_sura:
    # end of sura always means x_pos_in_line is -1
    sura = sura + 1
    ayah = 1
    lines_to_skip = default_lines_to_skip
    if sura == 9:
      lines_to_skip = lines_to_skip - 1
    end_of_ayah = False
    while line + 1 < num_lines and lines_to_skip > 0:
      line = line + 1
      if lines_to_skip == 2: # header
        vals = (i, line + 1, sura, -1, 1, lines[line][0][0], lines[line][1][0], lines[line][0][1], lines[line][1][1])
      elif lines_to_skip == 1 and sura ==9: # header of tawba
        vals = (i, line + 1, sura, -1, 1, lines[line][0][0], lines[line][1][0], lines[line][0][1], lines[line][1][1])
      else: # basmala
        vals = (i, line + 1, sura, 0, 1, lines[line][0][0], lines[line][1][0], lines[line][0][1], lines[line][1][1])
      output_aya_segment(vals, img_gray)
      lines_to_skip = lines_to_skip - 1
    if lines_to_skip == 0 and line + 1 != num_lines:
      ayah = 0

  # we have some lines unaccounted for or stopped mid-line
  if x_pos_in_line != -1 or line + 1 != num_lines:
    if x_pos_in_line == -1:
      line = line + 1
    pos = 0
    ayah = ayah + 1
    # we ignore pages 1 and 2 because they always have empty spaces at the end
    if i > 2:
      for l in range(line, num_lines):
        cur_line = lines[l]
        pos = pos + 1
        maxx = cur_line_maxx
        if x_pos_in_line > 0:
          maxx = x_pos_in_line
          x_pos_in_line = -1
        vals = (i, l + 1, sura, ayah, pos, cur_line[0][0], maxx,
          cur_line[0][1], cur_line[1][1])
        output_aya_segment(vals, img_gray)

  # done with detecting segments, now write using cv2
  image_name = out_folder + "z" + str(i) + ".png"
  cv2.imwrite(image_name, img_gray)

  # now paste segmented to original
  original = Image.open(image_dir + filename).convert('RGBA')
  segmented = Image.open(image_name).convert('RGBA')
  segmented.paste(original, mask=original)
  segmented.save(image_name, "PNG")
