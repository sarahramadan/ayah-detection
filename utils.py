import os
import pickle

_lines_file_name = '/lines.txt'

def safe_makedir(path):
  if not os.path.isdir(path):
    os.mkdir(path)
  return path


def save_lines(path, lines):
  with open(path + _lines_file_name, "wb") as file:
    pickle.dump(lines, file)


def load_lines(path):
  lines = None
  with open(path + _lines_file_name, "rb") as file:
    lines = pickle.load(file)
  return lines
