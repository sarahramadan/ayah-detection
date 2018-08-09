#!/usr/bin/env python2
import os
import argparse
from glob import glob
from subprocess import call
from tempfile import mkstemp
from tqdm import tqdm
from utils import safe_makedir

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_path1', type=str, required=True,
                        help='''Path to first input folder containing PNG images''')
    parser.add_argument('--input_path2', type=str, required=True,
                        help='''Path to second input folder containing PNG images''')
    parser.add_argument('--output_path', type=str, required=True,
                        help='''Path to output folder to generate comparison images in''')
    return parser.parse_args()


def compare_images(path1, path2, output_path):
  for input_file1 in tqdm(glob(path1 + "/*.png")):
    basename = os.path.basename(input_file1)
    matches = glob("%s/%s" % (path2, basename))
    if len(matches) == 1:
      input_file2 = matches[0]
      output_file = "%s/%s" % (output_path, basename)
      _, diff_file_name = mkstemp()
      diff_cmd = "convert %s %s -compose difference -composite -alpha remove %s.png" % (
          input_file1, input_file2, diff_file_name)
      call(diff_cmd.split(' '))
      cat_cmd = "montage %s %s.png %s -geometry +0 %s" % (input_file1, diff_file_name, input_file2, output_file)
      call(cat_cmd.split(' '))


if __name__ == "__main__":
  args = parse_arguments()

  out_dir = safe_makedir(args.output_path)
  compare_images(args.input_path1, args.input_path2, out_dir)
