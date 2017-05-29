import csv, os

def readCSV(file):
    if os.path.isfile(file):
        data = dict()
        try:
            with open(file) as f:
                reader = csv.reader(f)
                headings = next(reader)
                for h in headings:
                    data[h] = []
                for row in reader:
                    for h, v in zip(headings, row):
                        data[h].append(v)
            return data
        except:
            data=None
            #Nulls in file causes CSV reader to fail
            #Recreate the file stripping out all nulls
            with open(file,'rb') as f:
                data=f.read()
            with open(file,'wb') as f:
                f.write(data.replace('\x00',''))
            #Try again
            return readCSV(file)
    else:
        return None



GPX_HEADER = '<?xml version="1.0" encoding="UTF-8"?><gpx creator="StravaGPX" version="1.1" xmlns="http://www.topografix.com/GPX/1/1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd http://www.garmin.com/xmlschemas/GpxExtensions/v3 http://www.garmin.com/xmlschemas/GpxExtensionsv3.xsd http://www.garmin.com/xmlschemas/TrackPointExtension/v1 http://www.garmin.com/xmlschemas/TrackPointExtensionv1.xsd http://www.garmin.com/xmlschemas/GpxExtensions/v3 http://www.garmin.com/xmlschemas/GpxExtensionsv3.xsd http://www.garmin.com/xmlschemas/TrackPointExtension/v1 http://www.garmin.com/xmlschemas/TrackPointExtensionv1.xsd http://www.garmin.com/xmlschemas/GpxExtensions/v3 http://www.garmin.com/xmlschemas/GpxExtensionsv3.xsd http://www.garmin.com/xmlschemas/TrackPointExtension/v1 http://www.garmin.com/xmlschemas/TrackPointExtensionv1.xsd http://www.garmin.com/xmlschemas/GpxExtensions/v3 http://www.garmin.com/xmlschemas/GpxExtensionsv3.xsd http://www.garmin.com/xmlschemas/TrackPointExtension/v1 http://www.garmin.com/xmlschemas/TrackPointExtensionv1.xsd" xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1" xmlns:gpxx="http://www.garmin.com/xmlschemas/GpxExtensions/v3">'

data = readCSV('201705160444.log')

with open('test.gpx','w') as f:
    f.write(GPX_HEADER + '\n')
    f.write(' <metadata>\n  <time>{}</time>\n </metadata>\n'.format(data['TIMESTAMP'][0]))
    f.write(' <trk>\n  <trkseg>\n')
    for a in range(len(data['TIMESTAMP'])):
        if data['LATITUDE'][a] == '-' or data['LONGITUDE'][a] == '-':
            continue
        f.write('   <trkpt lat="{}" lon="{}">\n'.format(data['LATITUDE'][a], data['LONGITUDE'][a]))
        f.write('    <time>{}</time>\n'.format(data['TIMESTAMP'][a]))
        f.write('    <extensions>\n     <gpxtpx:TrackPointExtension>\n')
        exclude = ['LATITUDE','LONGITUDE','TIMESTAMP']
        for d in data:
            if d not in exclude:
                f.write('      <gpxtpx:{}>{}</gpxtpx:{}>\n'.format(d.lower(), data[d][a], d.lower()))
        f.write('     </gpxtpx:TrackPointExtension>\n    </extensions>\n   </trkpt>\n')
    f.write('  </trkseg>\n </trk>\n</gpx>\n')


