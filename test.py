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
f.Snippet = Snippet(text = 'Test Snippet',
                    maxLines = 2)
f.id = 'Test Feature ID'
f.time = '2006-06'
f.view = Camera(latitude = -20.2,
                longitude = 14.3,
                altitude = 35.0,
                heading = 0.0,
                tilt = 10,
                roll = -5,
                altitudeMode = 'clampToGround',
                time = ('2006','2007'))
f.view = LookAt(latitude = -20.2,
                longitude = 14.3,
                altitude = 35.0,
                heading = 0.0,
                tilt = 10,
                range = 500,
                altitudeMode = 'clampToGround',
                time = ('2006','2007'))

f.view.viewerOptions.append(
    GXViewerOption(
        'streetview', 1))
f.view.viewerOptions.append(
    GXViewerOption(
        'historicalimagery', 0))
f.view.viewerOptions.append(
    GXViewerOption(
        'sunlight', 1))

f.styleUrl = '#MyStyle'
s = Style()
s.IconStyle = IconStyle(color = 'FF00FF00',
                        colorMode = 'normal',
                        scale = 1.1,
                        heading = 50,
                        icon = Icon(href = 'http://url.to.icon/file',
                                    gx_x = 32,
                                    gx_y = 32,
                                    gx_w = 16,
                                    gx_h = 16,
                                    refreshMode = 'onInterval',
                                    refreshInterval = 3.5,
                                    viewBoundScale = 1.0,
                                    viewFormat = 'Test Format',
                                    httpQuery = 'http://test.query'),
                        hotSpot = HotSpot(x = 16,
                                          y = 16,
                                          xunits = 'pixels',
                                          yunits = 'pixels')
                        )

s.LabelStyle = LabelStyle(color = 'FF000000',
                          colorMode = 'random',
                          scale = 1.6,)

s.LineStyle = LineStyle(color = 'FFAAAAAA',
                        colorMode = 'normal',
                        width = 2,
                        gx_outerColor = '88FF3344',
                        gx_outerWidth = 1.2,
                        gx_physicalWidth = 7.4,
                        gx_labelVisibility = 1)

s.PolyStyle = PolyStyle(color = '33A2F411',
                        colorMode = 'normal',
                        fill = 1,
                        outline = 1)
                        
s.BalloonStyle = BalloonStyle(bgColor = 'FFFFFFFF',
                              textColor = 'FF000000',
                              text = 'Test Balloon Style Text',
                              displayMode = 'default')

s.ListStyle.listItemType = 'check'
s.ListStyle.bgColor = 'FF0044AA'
s.ListStyle.append(ItemIcon(state = 'open',
                            href = 'http"//item.icon.state/open')
                   )
s.ListStyle.append(ItemIcon(state = 'closed',
                            href = 'http"//item.icon.state/closed')
                   )
s.ListStyle.append(ItemIcon(state = 'error',
                            href = 'http"//item.icon.state/error')
                   )
s.ListStyle.append(ItemIcon(state = 'fetching0',
                            href = 'http"//item.icon.state/fetching0')
                   )
s.ListStyle.append(ItemIcon(state = 'fetching1',
                            href = 'http"//item.icon.state/fetching1')
                   )
s.ListStyle.append(ItemIcon(state = 'fetching2',
                            href = 'http"//item.icon.state/fetching2')
                   )

f.styleSelector = s

f.region = Region(LatLonAltBox = LatLonAltBox(north = 1.0,
                                              south = 10.0,
                                              east = 1,
                                              west = 10),
                  Lod = Lod(minLodPixels = 128,
                            maxLodPixels = -1,
                            minFadeExtent = 0,
                            maxFadeExtent = 0)
                  )

schema = Schema(name = 'Test Schema',
                id = 'TestSchemaID')
schema.append(SimpleField(name = 'Field1', type = 'string', displayName = '<![CDATA[<b>Test Field string</b>]]>'))
schema.append(SimpleField(name = 'Field2', type = 'float', displayName = '<![CDATA[<b>Test Field float</b>]]>'))
schema.append(SimpleField(name = 'Field3', type = 'int', displayName = '<![CDATA[<b>Test Field int</b>]]>'))
schema.append(SimpleField(name = 'Field4', type = 'double', displayName = '<![CDATA[<b>Test Field double</b>]]>'))
schema.append(SimpleField(name = 'Field5', type = 'uint', displayName = '<![CDATA[<b>Test Field uint</b>]]>'))
schema.append(SimpleField(name = 'Field6', type = 'short', displayName = '<![CDATA[<b>Test Field short</b>]]>'))
schema.append(SimpleField(name = 'Field7', type = 'ushort', displayName = '<![CDATA[<b>Test Field ushort</b>]]>'))
schema.append(SimpleField(name = 'Field8', type = 'bool', displayName = '<![CDATA[<b>Test Field bool</b>]]>'))
schema.append(SimpleField(name = 'Field9', type = 'str', displayName = '<![CDATA[<b>Test Field str</b>]]>'))
schema.append(SimpleField(name = 'Field10', type = 'booleanEnum', displayName = '<![CDATA[<b>Test Field booleanEnum</b>]]>'))

sd = SchemaData(schema = schema)
d = {'Field1': 'Test Field 1 Data',
     'Field2' : 123.456,
     'Field8' : False}

sd.addData(d)
f.extendedData = ExtendedData(schemaData = sd)

m = Model()
m.altitudeMode = 'clampToGround'
m.location = Location(longitude = -30.6,
                      latitude = 15.2,
                      altitude = 1000)
m.orientation = Orientation(heading = 245.6,
                            tilt = 12.6,
                            roll = 89.0)
m.modelScale = Scale(x = 1,
                     y = 1,
                     z = 1)
m.link = Link(href = 'Link HRef',
              refreshMode = 'onInterval',
              refreshInterval = 5,
              viewRefreshMode = 'onRequest',
              viewRefreshTime = 30.0,
              viewBoundScale = 25.0,
              viewFormat = 'Test Format',
              httpQuery = 'Test HTTPQuery')

rm = ResourceMap()
rm.append(Alias(sourceHref = 'source Href 1', targetHref = 'target Href 1'))
rm.append(Alias(sourceHref = 'source Href 2', targetHref = 'target Href 2'))
rm.append(Alias(sourceHref = 'source Href 3', targetHref = 'target Href 3'))
rm.append(Alias(sourceHref = 'source Href 4', targetHref = 'target Href 4'))

m.resourceMap = rm

c = Coordinates()
c.append(Coordinate(latitude = 12.34,
                    longitude = 23.45,
                    altitude = 2000))
c.append(Coordinate(latitude = 12.34,
                    longitude = 23.45,
                    altitude = 2000))
c.append(Coordinate(latitude = 12.34,
                    longitude = 23.45,
                    altitude = 2000))


p = Point(extrude = 'yes',
          altitudeMode = 'clampToGround',
          coordinates = c)
         
l = LineString(gx_altitudeOffset = 12,
               extrude = 'yes',
               tessellate = 'no',
               altitudeMode = 'absolute',
               gx_drawOrder = 1,
               coordinates = c)

lr = LinearRing(gx_altitudeOffset = 30,
                extrude = 'yes',
                tessellate = 'no',
                altitudeMode = 'clampToSeaFloor',
                coordinates = c)

mg = MultiGeometry()
mg.append(p)
mg.append(l)
mg.append(lr)

p = Polygon(outerBoundaryIs = OuterBoundary(linearRing = lr),
            extrude = 'no',
            tessellate = 'yes',
            altitudeMode = 'clampToGround')



