#!/usr/bin/env python2
import os
import sys
import argparse
from md5 import md5

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--recitation_id', type=int, required=True)
    parser.add_argument('--qaree_id', type=int, required=True)
    parser.add_argument('--sura_id', type=int, required=True)
    parser.add_argument('--aya_id', type=int, required=True)
    return parser.parse_args()


if __name__ == "__main__":
  args = parse_arguments()

  base_url = "http://audio.elmohafez.com"
  try:
    salt = os.environ["ELMOHAFEZ_SALT"]
  except KeyError as error:
    print("Environment variable ELMOHAFEZ_SALT must be set")
    sys.exit(1)

  input = "%d-%d-%d-%d0%s" % (args.recitation_id, args.qaree_id, args.sura_id, args.aya_id, salt)
  hash = md5(input).hexdigest()
  print("%s/%d-%d/%c/%s.mp3" % (base_url, args.recitation_id, args.qaree_id, hash[0], hash))
