import sys
import sqlite3
import base64
import argparse
from tempfile import mkstemp
from glob import glob
import csv
from tqdm import tqdm
from utils import safe_makedir


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_path', type=str, required=True,
                        help='''Path to input folder containing segmented data SQL files to import''')
    parser.add_argument('--output_path', type=str, required=True,
                        help='''Path to output folder to generate platform specific files into''')
    parser.add_argument('--reference_width', type=float, required=True,
                        help='''Reference width of which segmented data SQL files were generated''')
    parser.add_argument('--recitation_id', type=int, required=True,
                        help='''Recitation ID of the segmented data''')
    return parser.parse_args()


def create_db():
  print("Creating database...")
  _, db_file_name = mkstemp()
  print("Created database at " + db_file_name)
  conn = sqlite3.connect(db_file_name)
  cursor = conn.cursor()
  cursor.execute('''
    CREATE TABLE "glyphs" (
      'id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
      'pageId' INTEGER,
      'lineId' INTEGER,
      'suraId' INTEGER,
      'verseId' INTEGER,
      'indexId' INTEGER,
      'left' INTEGER,
      'right' INTEGER,
      'top' INTEGER,
      'bottom' INTEGER);
  ''')
  cursor.execute('''
    CREATE TABLE "encoded_glyphs" (
      'id' INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
      'pageId' INTEGER,
      'lineId' INTEGER,
      'suraId' INTEGER,
      'verseId' INTEGER,
      'data' TEXT);
  ''')
  return conn


def import_data(conn, sql_dir):
  print("Importing SQL files in " + sql_dir + "...")
  cursor = conn.cursor()
  for file_name in tqdm(glob(sql_dir + "/*.sql")):
    with open(file_name, "rb") as file:
      cursor.executescript(file.read())
  conn.commit()


def group_data(conn):
  print("Grouping data...")
  cursor = conn.cursor()
  cursor.execute('''
    INSERT INTO encoded_glyphs (
      pageId,
      lineId,
      suraId,
      verseId,
      data
    )
    SELECT
      pageId,
      min(lineId) lineId,
      suraId,
      verseId,
      '[' || group_concat('"' || left || ',' || top || ',' || right || ',' || bottom || '"', ',') || ']' data
    FROM glyphs
    GROUP BY
      suraid,
      verseid,
      pageid
    ORDER BY
      suraid,
      verseid,
      pageid;
  ''')
  conn.commit()


def encode_data(conn, width, ref_width):
  encoded_data = []
  ratio = width / ref_width
  cursor = conn.cursor()
  for row in cursor.execute('SELECT * FROM encoded_glyphs ORDER BY pageid, suraid, verseid'):
    data = row[5]
    data = data.replace('[', '').replace(']', '')
    rects = data.split('","')
    data = ""
    for rect in rects:
      coords = rect.replace('"', '')
      coords = coords.split(',')
      if len(data) > 0:
        data += ","
      left = int(round(int(coords[0]) * ratio))
      top = int(round(int(coords[1]) * ratio))
      right = int(round(int(coords[2]) * ratio))
      bottom = int(round(int(coords[3]) * ratio))
      data += str(left << 48 | top << 32 | right << 16 | bottom)
    data = base64.b64encode(data)
    encoded_data.append((row[1], row[2], row[3], row[4], data))
  return encoded_data


def export_data_sql(data, recitation_id, file_name):
  print("Exporting %d records to %s..." % (len(data), file_name))
  with open(file_name, 'wb') as file:
    for row in data:
      file.write('''
      INSERT INTO recitations_data (
        recitation_id,
        page_id,
        line_id,
        sura_id,
        verse_id,
        data
      ) VALUES (%s, %s, %s, %s, %s, '%s');
      ''' \
      % (recitation_id, row[0], row[1], row[2], row[3], row[4]))


def export_data_tsv(data, recitation_id, file_name):
  print("Exporting %d records to %s..." % (len(data), file_name))
  with open(file_name, 'wb') as file:
    writer = csv.writer(file, delimiter='\t',
                            quotechar='"', quoting=csv.QUOTE_MINIMAL)
    writer.writerow([
      'rewayaId',
      'pageId',
      'suraId',
      'verseId',
      'lineId',
      'data'
    ])
    for row in data:
      writer.writerow([
        recitation_id,
        row[0],
        row[2],
        row[3],
        row[1],
        row[4]
      ])


if __name__ == "__main__":
  args = parse_arguments()

  conn = create_db()

  import_data(conn, args.input_path)
  group_data(conn)

  out_dir = safe_makedir(args.output_path)
  for width in [320, 480, 800, 1200, 1500]:
    data = encode_data(conn, width, args.reference_width)
    file_name = "%s/%d.sql" % (out_dir, width)
    export_data_sql(data, args.recitation_id, file_name)
    if width == 800:
      file_name = "%s/%d.tsv" % (out_dir, width)
      export_data_tsv(data, args.recitation_id, file_name)

  conn.close()
