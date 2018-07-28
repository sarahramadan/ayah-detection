import sys
import sqlite3
import base64

ratio = float(sys.argv[1]) / 800
rec = "2"

conn = sqlite3.connect('/home/ayman/phpliteAdmin/Tadween')

cursor = conn.cursor()
st = ""
for row in cursor.execute('select * from encoded_glyphs order by pageid, suraid, verseid'):
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
	if len(st) > 0:
		st += "\n"
	#st += "insert into recitations_data (recitation_id, page_id, sura_id, verse_id, line_id, data) values (%s,%s,%s,%s,%s,'%s')" % (rec, row[1], row[3], row[4], row[2], data)
	#conn.cursor().execute('update encoded_glyphs set encoded_data="%s" where id = %d' % (data, row[0]))

print st

conn.commit()

conn.close()
