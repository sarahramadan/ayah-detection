#!/usr/bin/env python3
import os
import argparse
from glob import glob
from tqdm import tqdm
from cairosvg import svg2png # pip install cairosvg


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_path', type=str, required=True,
                        help='''Path to input folder containing SVG files''')
    parser.add_argument('--output_path', type=str, required=True,
                        help='''Path to output folder to generate PNG files into''')
    parser.add_argument('--width', type=float, required=True,
                        help='''Width to generate PNG files with''')
    return parser.parse_args()


def convert(input_path, output_path, width):
  for input_file in tqdm(glob(input_path + "/*.svg")):
    output_file, _ = os.path.splitext(os.path.basename(input_file))
    output_file = "%s/%s.png" % (output_path, output_file)
    svg2png(url=input_file, write_to=output_file, parent_width=width)

if __name__ == "__main__":
  args = parse_arguments()

  convert(args.input_path, args.output_path, args.width)
