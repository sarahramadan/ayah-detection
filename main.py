import sys
import cv2
from PIL import Image
from PIL import ImageDraw
from lines import find_lines
from lines import find_lines2,find_lines3
from ayat import find_ayat, draw, output_aya_segment
import random


sura_ayat = [7, 286, 200, 176, 120, 165, 206, 75, 129, 109, 123, 111,
             43, 52, 99, 128, 111, 110, 98, 135, 112, 78, 118, 64, 77,
             227, 93, 88, 69, 60, 34, 30, 73, 54, 45, 83, 182, 88, 75,
             85, 54, 53, 89, 59, 37, 35, 38, 29, 18, 45, 60, 49, 62, 55,
             78, 96, 29, 22, 24, 13, 14, 11, 11, 18, 12, 12, 30, 52, 52,
             44, 28, 28, 20, 56, 40, 31, 50, 40, 46, 42, 29, 19, 36, 25,
             22, 17, 19, 26, 30, 20, 15, 21, 11, 8, 8, 19, 5, 8, 8, 11,
             11, 8, 3, 9, 5, 4, 7, 3, 6, 3, 5, 4, 5, 6]

count_ayat = sura_ayat

outFolder = sys.argv[4] + '/'

sura = 1
ayah = 1
#sura = 2
#ayah = 6
lines_to_skip = 0
default_lines_to_skip = 2

# by default, we don't increase the ayah on the top of this loop
# to handle ayat that span multiple pages - this flag allows us to
# override this.
end_of_ayah = False
r = lambda: random.randint(0,255)
# warsh: 1, 560 (last page: 559)
# shamerly: 2, 523 (last page: 522) - lines to skip: 3 (2 + 1 basmala)
# qaloon: 1, 605 (last page: 604) - lines to skip: 2 (1 + 1 basmala)
#sura: 1,6
for i in range(1,605):
  image_dir = sys.argv[1] + '/'
  #filename = "001_Page_"+str(i).zfill(2) + '.jpg'
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
  image.save(outFolder + str(i).zfill(3) + 'output.png', "PNG")
  # **************************************************

  #img_rgb = cv2.imread(image_dir + filename)
  #img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
  img_gray = cv2.imread(image_dir + filename, -1)
  if i == 1 or i == 2:
    template = cv2.imread(sys.argv[3], -1)
  else:
    template = cv2.imread(sys.argv[2], -1)

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
      if lines_to_skip > 0:
        if lines_to_skip == 2: # header
          vals = (i, line + 1, sura, -1, 1, cur_line[0][0], cur_line[1][0], cur_line[0][1], cur_line[1][1])
        elif lines_to_skip == 1 and sura ==9: # header of tawba
          vals = (i, line + 1, sura, -1, 1, cur_line[0][0], cur_line[1][0], cur_line[0][1], cur_line[1][1])
        else: # basmala
          vals = (i, line + 1, sura, 0, 1, cur_line[0][0], cur_line[1][0], cur_line[0][1], cur_line[1][1])
        output_aya_segment(vals, img_gray)
        lines_to_skip = lines_to_skip - 1
        current_line = current_line + 1
        continue
      pos = pos + 1
      if y_pos <= maxy:
        # we found the line with the ayah
        maxx = cur_line[1][0]
        if x_pos_in_line > 0:
          maxx = x_pos_in_line
        minx = ayah_item[0]
        if minx < tpl_width/2: # small value indicating that the separator is the last thing comes in line
          minx = 0
        vals = (i, line + 1, sura, ayah, pos, minx, maxx, miny, maxy)
        output_aya_segment(vals, img_gray)
        end_of_sura = False
        if count_ayat[sura - 1] == ayah:
          end_of_sura = True

        if end_of_sura or abs(minx - cur_line[0][0]) < tpl_width/2:
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
        maxx = cur_line[1][0]
        if x_pos_in_line > 0:
          maxx = x_pos_in_line
        x_pos_in_line = -1
        current_line = current_line + 1
        vals = (i, line + 1, sura, ayah, pos, cur_line[0][0], maxx,
              cur_line[0][1], cur_line[1][1])
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
    for l in range(line, num_lines):
      cur_line = lines[l]
      pos = pos + 1
      maxx = cur_line[1][0]
      if x_pos_in_line > 0:
        maxx = x_pos_in_line
        x_pos_in_line = -1
      vals = (i, l + 1, sura, ayah, pos, cur_line[0][0], maxx,
        cur_line[0][1], cur_line[1][1])
      output_aya_segment(vals, img_gray)

  # done with detecting segments, now write using cv2
  image_name = outFolder + "z" + str(i) + ".png"
  cv2.imwrite(image_name, img_gray)

  # now paste segmented to original
  original = Image.open(image_dir + filename).convert('RGBA')
  segmented = Image.open(image_name).convert('RGBA')
  segmented.paste(original, mask=original)
  segmented.save(image_name, "PNG")
