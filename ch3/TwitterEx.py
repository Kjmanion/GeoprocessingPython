import sys
import os
from osgeo import ogr
import tweepy


def avgCoordinates(coords):
    lat = 0
    lon = 0
    for coord in coords:
        lon += coord[0]
        lat += coord[1]
    lat = lat/4
    lon = lon/4
    lat = round(lat, 5)
    lon = round(lon, 5)
    newCoords = [lat, lon]
    return newCoords

# auth = tweepy.OAuthHandler(#Input tokens here//)
# auth.set_access_token(#input more values here)

api = tweepy.API(auth)

places = api.geo_search(query="USA", granularity="country")

place_id = places[0].id
print ("USA id is: ", place_id)

driver = ogr.GetDriverByName("GeoJSON")
if os.path.exists("tweets3.geojson"):
    driver.DeleteDataSource("tweets3.geojson")

ds1 = driver.CreateDataSource(r"tweets3.geojson")
lyr = ds1.CreateLayer('layer')

coord_fld = ogr.FieldDefn('X', ogr.OFTReal)
coord_fld.SetWidth(12)
coord_fld.SetPrecision(7)
lyr.CreateField(coord_fld)
coord_fld.SetName("Y")
lyr.CreateField(coord_fld)
tweet_fld = ogr.FieldDefn('Tweet', ogr.OFTString)
tweet_fld.SetWidth(200)
lyr.CreateField(tweet_fld)
usr = ogr.FieldDefn('User', ogr.OFTString)
usr.SetWidth(25)
lyr.CreateField(usr)

searchQuery = 'place:96683cc9126741d1 #Terps OR #terps'
maxTweets = 1000
tweetsPerQry = 1000

featureDefn = lyr.GetLayerDefn()
out_feat = ogr.Feature(featureDefn)
point = ogr.Geometry(ogr.wkbPoint)

for tweet in tweepy.Cursor(api.search, q=searchQuery).items(maxTweets):
    if tweet.place is not None:
        newCoords = avgCoordinates(tweet.place.bounding_box.coordinates[0])
        print newCoords
        out_feat.SetField("X", newCoords[1])
        out_feat.SetField("Y", newCoords[0])
        out_feat.SetField("Tweet", tweet.text)
        out_feat.SetField("User", tweet.user.name)
        point.AddPoint(newCoords[1], newCoords[0])
        out_feat.SetGeometry(point)
        lyr.CreateFeature(out_feat)

del ds1
