#!/usr/bin/env python2
import os
import argparse
import cv2
from PIL import Image
from tqdm import tqdm
from verses_count import verses_count
from ayat import find_ayat, draw, output_aya_segment
from utils import safe_makedir, load_lines


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
    parser.add_argument('--pages', type=str, default='1..604',
                        help='''Comma seprated page numbers or ranges, default is 1..604''')
    parser.add_argument('--start_sura', type=str, default='1',
                        help='''Start sura numbers for each page in the input pages, default = 1''')
    parser.add_argument('--start_aya', type=str, default='1',
                        help='''Start aya numbers for each page in the input pages, default = 1''')
    parser.add_argument('--matching_threshold', type=float, default=0.42,
                        help='''Matching threshold to match aya separators, default = 0.42''')
    return parser.parse_args()


def parse_start_tuples(args):
  tuples = []
  pages = args.pages.split(',')
  suras = args.start_sura.split(',')
  ayahs = args.start_aya.split(',')
  total_pages = 0

  if not (len(pages) == len(suras) == len(ayahs)):
    raise ValueError('Lengths of pages, start_sura and start_aya arguments must match')

  for page, sura, ayah in zip(pages, suras, ayahs):
    page_range = page.split('..')
    start_page = int(page_range[0])
    end_page = int(page_range[-1])
    total_pages += end_page - start_page + 1
    tuples.append({
      'start_page': start_page,
      'end_page': end_page,
      'start_sura': int(sura),
      'start_aya': int(ayah)
    })
  return total_pages, tuples

def main_find_ayat(progress_bar, all_pages_lines, count_ayat, start_page, end_page,
                   start_sura, start_aya, separator1_path, separator3_path,
                   matching_threshold, input_path, output_path, segments_path):
  # by default, we don't increase the ayah on the top of this loop
  # to handle ayat that span multiple pages - this flag allows us to
  # override this.
  end_of_ayah = False
  sura = start_sura
  ayah = start_aya
  default_lines_to_skip = 2

  if start_page < 3:  # default behavior for pages 1 and 2
    lines_to_skip = default_lines_to_skip
    ayah = 1
  elif sura == 9 and ayah < 2: # skip only 1 line (header) for tawba
    lines_to_skip = 1
    ayah = 1
  elif ayah < 1: # skip 1 if ayah = 0 (basmalah), skip 2 if ayah = -1 (header)
    lines_to_skip = 1 - ayah
    ayah = 1
  else: # don't skip anything, starting from the middle of a sura
    lines_to_skip = 0

  for i in range(start_page, end_page + 1):
    filename = str(i) + '.png'
    lines = all_pages_lines[i]

    img_gray = cv2.imread(input_path + filename, -1)
    if i == 1 or i == 2:
      template = cv2.imread(separator1_path, -1)
    else:
      template = cv2.imread(separator3_path, -1)

    ayat = find_ayat(img_gray, template, matching_threshold)

    tpl_width = template.shape[1]

    current_line = 0
    x_pos_in_line = -1
    num_lines = len(lines)

    with open(segments_path + str(i).zfill(3) + ".sql", "wb") as segments_file:
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
            if lines_to_skip == 2:  # header
              vals = (i, line + 1, sura, -1, 1, cur_line_minx, cur_line_maxx, miny, maxy)
            elif lines_to_skip == 1 and sura == 9:  # header of tawba
              vals = (i, line + 1, sura, -1, 1, cur_line_minx, cur_line_maxx, miny, maxy)
            else:  # basmala
              vals = (i, line + 1, sura, 0, 1, cur_line_minx, cur_line_maxx, miny, maxy)
            output_aya_segment(vals, img_gray, segments_file)
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
            if minx < tpl_width/2:  # small value indicating that the separator is the last thing comes in line
              minx = 0
            end_of_sura = False
            if count_ayat[sura - 1] == ayah:
              end_of_sura = True

            # last aya in sura segment must extend to the leftmost, the empty space is ugly
            # also last ayah in page 2 must extend to the leftmost
            if end_of_sura or i == 2 and ayah_item == ayat[-1]:
              minx = 0

            vals = (i, line + 1, sura, ayah, pos, minx, maxx, miny, maxy)
            output_aya_segment(vals, img_gray, segments_file)

            # check if this is header/basmalah, it must occupy the whole line
            if (vals[3] == -1 or vals[3] == 0) and (vals[5] != 0 or vals[6] != cur_line_maxx):
              raise RuntimeError(
                  'Something is wrong: Header or Basmalah are not occuping the whole line')

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
            output_aya_segment(vals, img_gray, segments_file)

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
          output_aya_segment(vals, img_gray, segments_file)
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
            maxx = cur_line[1][0]
            if x_pos_in_line > 0:
              maxx = x_pos_in_line
              x_pos_in_line = -1
            vals = (i, l + 1, sura, ayah, pos, cur_line[0][0], maxx,
              cur_line[0][1], cur_line[1][1])
            output_aya_segment(vals, img_gray, segments_file)

    # done with detecting segments, now write using cv2
    image_name = output_path + str(i).zfill(3) + ".png"
    cv2.imwrite(image_name, img_gray)

    # now paste segmented to original
    original = Image.open(input_path + filename).convert('RGBA')
    segmented = Image.open(image_name).convert('RGBA')
    segmented.paste(original, mask=original)
    segmented.save(image_name, "PNG")

    # finally increment progress bar
    progress_bar.update(1)


if __name__ == "__main__":
  args = parse_arguments()
  total_pages, start_tuples = parse_start_tuples(args)

  input_path = args.input_path + '/'
  output_path = safe_makedir(args.output_path + '/ayat/')
  segments_path = safe_makedir(args.output_path + '/segments/')
  lines = load_lines(args.output_path)

  print("Finding aya boundaries using separator templates into " + output_path + "...")
  with tqdm(total=total_pages) as pbar:
    for tuple in start_tuples:
      main_find_ayat(progress_bar=pbar,
                    all_pages_lines=lines,
                    start_page=tuple['start_page'],
                    end_page=tuple['end_page'],
                    start_sura=tuple['start_sura'],
                    start_aya=tuple['start_aya'],
                    count_ayat=verses_count[args.count_method],
                    separator1_path=args.separator1_path,
                    separator3_path=args.separator3_path,
                    matching_threshold=args.matching_threshold,
                    input_path=input_path,
                    output_path=output_path,
                    segments_path=segments_path)
