from bs4 import BeautifulSoup
import urllib.request
import requests
import stringUtils
import boto3
import os.path
from boto3.dynamodb.conditions import Key, Attr

rootUrl = "https://www.tripadvisor.ca"
spotTable = boto3.resource('dynamodb').Table('spot')
cityTable = boto3.resource('dynamodb').Table('city')
bucketName = "ece1779-spot-images"
bucket = boto3.resource('s3').Bucket(bucketName)
rootObjectUrl = "https://ece1779-spot-images.s3.amazonaws.com/" # your s3 url prefix like https://****.s3.amazonaws.com/
cityUrls = {
    "TorontoUrl":
    "https://www.tripadvisor.ca/Attractions-g155019-Activities-a_allAttractions.true-Toronto_Ontario.html",
    "VancouverUrl":
    "https://www.tripadvisor.ca/Attractions-g154943-Activities-a_allAttractions.true-Vancouver_British_Columbia.html",
    "MontrealUrl":
    "https://www.tripadvisor.ca/Attractions-g155032-Activities-a_allAttractions.true-Montreal_Quebec.html",
    "OttawaUrl":
    "https://www.tripadvisor.ca/Attractions-g155004-Activities-a_allAttractions.true-Ottawa_Ontario.html",
    "SeattleUrl":
    "https://www.tripadvisor.ca/Attractions-g60878-Activities-a_allAttractions.true-Seattle_Washington.html",
    "ChicagoUrl":
    "https://www.tripadvisor.ca/Attractions-g35805-Activities-a_allAttractions.true-Chicago_Illinois.html",
    "New York CityUrl":
    "https://www.tripadvisor.ca/Attractions-g60763-Activities-a_allAttractions.true-New_York_City_New_York.html",
    "BostonUrl":
    "https://www.tripadvisor.ca/Attractions-g60745-Activities-a_allAttractions.true-Boston_Massachusetts.html",
    "San FranciscoUrl":
    "https://www.tripadvisor.ca/Attractions-g60713-Activities-a_allAttractions.true-San_Francisco_California.html",
    "Los AngelesUrl":
    "https://www.tripadvisor.ca/Attractions-g32655-Activities-a_allAttractions.true-Los_Angeles_California.html",
    "Las VegasUrl":
    "https://www.tripadvisor.ca/Attractions-g45963-Activities-a_allAttractions.true-Las_Vegas_Nevada.html",
    "Washington DCUrl":
    "https://www.tripadvisor.ca/Attractions-g28970-Activities-a_allAttractions.true-Washington_DC_District_of_Columbia.html",
}

def getHtml(url):
    page = urllib.request.urlopen(url)
    html = page.read()
    return html

def getContent(url):
    html = getHtml(url)
    soup = BeautifulSoup(html, "html.parser")
    return soup

"""
get all spots urls from attractions page
"""
def getCitySpotLinks(cityName):
    cityUrl = cityName + 'Url'
    cityContent = getContent(cityUrls[cityUrl])
    citySpotsList = cityContent.find_all(
        'div', class_="tracking_attraction_title listing_title")
    citySpotLinks = []
    count = 0
    for citySpot in citySpotsList:
        if count >= 15:
            break
        spotLink = citySpot.find_all('a')[0]['href']
        citySpotLinks.append(spotLink)
        count += 1
    return citySpotLinks

"""
find the image url and download into local folder
"""
def dldImageFromSpotLink(cityName, citySpotLink):
    spotContent = getContent(rootUrl + citySpotLink)
    name = spotContent.find('h1', class_="ui_header h1").text
    try:
        img1link = spotContent.find('div', class_="prw_rup prw_common_basic_image photo_widget attractions_large landscape").find('div').find('img')['data-lazyurl']
        saveLocalImgByLink(cityName, img1link, name, 1)
    except:
        print("sth. wrong")
    linkNum = 2
    try:
        img234block = spotContent.find('div', class_="ui_column is-3-desktop is-hidden-mobile mini_photo_wrapper").find_all(
            'div', class_="prw_rup prw_common_basic_image photo_widget small landscape")
        for imgb in img234block:
            imgblink = imgb.find('div').find('img')['data-lazyurl']
            saveLocalImgByLink(cityName, imgblink, name, linkNum)
            linkNum += 1
    except:
        print("sth. wrong")
    return

def saveLocalImgByLink(cityName, imgLink, spotName, loc):
    filepath = "/PythonProjects/tripSpider/spotImgs/" + cityName + "/" + cityName + "%" + spotName + "%" + str(loc) + ".png"
    myfile = requests.get(imgLink)
    open(filepath, 'wb').write(myfile.content)

"""
get links of all spots and download images of spots one by one to local folder
"""
def dldImageByCity(cityName):
    spotLinks = getCitySpotLinks(cityName)
    for spotLink in spotLinks:
        dldImageFromSpotLink(cityName, spotLink)
        print(rootUrl + spotLink)
    return

"""
add image urls into spot['images']
"""
def addUrlToImgs(filename, url):
    # City%Spot%1.png
    # url is object url into images
    city = filename.split('%')[0]
    spot = filename.split('%')[1]
    response = spotTable.scan(FilterExpression=Attr('name').eq(spot))
    if 'Items' in response:
        spotItem = response['Items'][0]
        images = spotItem['images']
        spotId = spotItem['spotId']
        if url not in images:
            images.append(url)
        spotTable.update_item(Key={'spotId': spotId},
                          UpdateExpression="SET images = :val",
                          ExpressionAttributeValues={
                              ":val": images
                          })

"""
upload images by city name
"""
def uploadImageByCity(cityName):
    imgDir = "D:/PythonProjects/tripSpider/spotImgs/" + cityName + "/"
    for dirpath, dirnames, filenames in os.walk(imgDir):        
        for filename in filenames:
            url = str(rootObjectUrl + filename).replace(' ', '+').replace('%', '%25')
            addUrlToImgs(filename, url)
            with open(os.path.join(imgDir, filename), 'rb') as tmp:
                response = bucket.put_object(Key=filename, Body=tmp)
            print("upload", url)
    return 

def truncateImageLinks(cityName):
    spotIds = cityTable.scan(FilterExpression=Attr('name').eq(cityName))['Items'][0]['spots']
    for spotId in spotIds:
        truncateImgBySpot(spotId)

def truncateImgBySpot(spotId):
    images = []
    spotTable.update_item(Key={'spotId': spotId},
                          UpdateExpression="SET images = :val",
                          ExpressionAttributeValues={
                              ":val": images
                          })

"""
usage: change the parameter to city's name corresponding to city name in db
"""
if __name__ == "__main__":
    dldImageByCity("Vancouver")
    uploadImageByCity("Vancouver")
    # truncateImageLinks("San Francisco")