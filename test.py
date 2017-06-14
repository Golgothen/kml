from kml3 import *

f = KMLFeature()
f.name = 'Test Feature'
f.description = 'Test feature test description'
f.visibility = 'yes'
f.open = 'no'
f.atom_link = 'http://test.link/author'
f.atom_author = 'Paul Ellis'
f.address = 'Test Address'
f.xal_AddressDetails = 'Test Address Details'
f.phoneNumber = '1800 000 000'
f.Snippet = Snippet('Test Snippet', 2)
f.id = 'Test Feature ID'
f.time = '2006-06'
f.view = 'Camera'
f.view.time = ('2006','2007')
f.view.viewerOptions.append(
    GXViewerOption(
        'streetview', 1))
f.view.viewerOptions.append(
    GXViewerOption(
        'historicalimagery', 0))
f.view.viewerOptions.append(
    GXViewerOption(
        'sunlight', 1))
f.view.latitude = -20.2
f.view.longitude = 14.3
f.view.altitude = 35.0
f.view.heading = 0.0
f.view.tilt = 10
f.view.roll = -5
f.view.altitudeMode = 'clampToGround'
f.styleUrl = '#MyStyle'
s = Style()
s.IconStyle = IconStyle('FF00FF00',
                        'normal',
                        1.1,
                        50,
                        Icon('http://url.to.icon/file',
                             32,32,16,16,'onInterval',
                             3.5,1.0,'Test Format',
                             'http://test.query'),
                        HotSpot(16,16,'pixels','pixels'))

s.LabelStyle = LabelStyle('FF000000',
                          'random',
                          1.6,)

s.LineStyle = LineStyle('FFAAAAAA',
                        'normal',
                        2,
                        '88FF3344',
                        1.2,
                        7.4,
                        1)

s.PolyStyle = PolyStyle('33A2F411',
                        'normal',
                        1,
                        1)
                        
s.BalloonStyle = BalloonStyle('FFFFFFFF',
                              'FF000000',
                              'Test Balloon Style Text',
                              'default')

s.ListStyle.listItemType = 'check'
s.ListStyle.bgColor = 'FF0044AA'
s.ListStyle.append('open','http"//item.icon.state/open')
s.ListStyle.append('closed','http"//item.icon.state/closed')
s.ListStyle.append('error','http"//item.icon.state/error')
s.ListStyle.append('fetching0','http"//item.icon.state/fetching0')
s.ListStyle.append('fetching1','http"//item.icon.state/fetching1')
s.ListStyle.append('fetching2','http"//item.icon.state/fetching2')

f.styleSelector = s

f.region = Region(LatLonAltBox(1.0, 10.0, 1, 10),
                  Lod(128, -1, 0, 0))

schema = Schema('Test Schema', 'TestSchemaID')
schema.append(SimpleField('Field1', 'string', '<![CDATA[<b>Test Field string</b>]]>'))
schema.append(SimpleField('Field2', 'float', '<![CDATA[<b>Test Field float</b>]]>'))
schema.append(SimpleField('Field3', 'int', '<![CDATA[<b>Test Field int</b>]]>'))
schema.append(SimpleField('Field4', 'double', '<![CDATA[<b>Test Field double</b>]]>'))
schema.append(SimpleField('Field5', 'uint', '<![CDATA[<b>Test Field uint</b>]]>'))
schema.append(SimpleField('Field6', 'short', '<![CDATA[<b>Test Field short</b>]]>'))
schema.append(SimpleField('Field7', 'ushort', '<![CDATA[<b>Test Field ushort</b>]]>'))
schema.append(SimpleField('Field8', 'bool', '<![CDATA[<b>Test Field bool</b>]]>'))
schema.append(SimpleField('Field9', 'str', '<![CDATA[<b>Test Field str</b>]]>'))
schema.append(SimpleField('Field10', 'booleanEnum', '<![CDATA[<b>Test Field booleanEnum</b>]]>'))

sd = SchemaData(schema)
d = {'Field1': 'Test Field 1 Data',
     'Field2' : 123.456,
     'Field8' : False}

sd.addData(d)
f.extendedData = sd

m = Model()
m.altitudeMode = 'clampToGround'
m.location = Location(-30.6, 15,2, 1000)
m.orientation = Orientation(245.6, 12.6, 89.0)
m.modelScale = Scale(1,1,1)
m.link = Link('Link HRef',
              'onInterval',
              5,
              'onRequest',
              30.0,
              25.0,
              'Test Format',
              'Test HTTPQuery')

rm = ResourceMap()
rm.append(Alias('source Href 1', 'target Href 1'))
rm.append(Alias('source Href 2', 'target Href 2'))
rm.append(Alias('source Href 3', 'target Href 3'))
rm.append(Alias('source Href 4', 'target Href 4'))

m.resourceMap = rm





