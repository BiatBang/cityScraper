from bs4 import BeautifulSoup
import urllib.request
import requests
import stringUtils
import boto3
"""
spot: {
		‘spotId’: string, // 10 char string
		‘name’: string,
		‘count’: int,   //////// count of views or adds
		‘location’: string,
		‘description’: string,
        ‘openTime’: string,
		‘images’: [{
	    ‘url’: string
}, …(urls of images of this spot)]
}
"""
"""
Toronto: https://www.tripadvisor.ca/Attractions-g155019-Activities-a_allAttractions.true-Toronto_Ontario.html
"""
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
rootUrl = "https://www.tripadvisor.ca"
spotTable = boto3.resource('dynamodb').Table('spot')
cityTable = boto3.resource('dynamodb').Table('city')
cities = []


def getHtml(url):
    page = urllib.request.urlopen(url)
    html = page.read()
    return html


def getContent(url):
    html = getHtml(url)
    soup = BeautifulSoup(html, "html.parser")
    return soup


def createSpotId(num):
    idExisted = True
    randomId = ""
    while idExisted:
        randomId = stringUtils.randomString(num)
        spotItem = spotTable.get_item(Key={'spotId': randomId})
        if 'Item' not in spotItem:
            idExisted = False
    return randomId

"""
the main scraper functions
"""
def getSpotInfo(spotLink):
    spotContent = getContent(rootUrl + spotLink)

    spotId = createSpotId(10)
    name = spotContent.find('h1', class_="ui_header h1").text
    count = 0

    try:
        locationComps = spotContent.find('span',
                                         class_="textAlignWrapper address"
                                         ).findChildren()[1].findChildren()
        location = ""
        for lcomp in locationComps:
            location += lcomp.text
        if not location:
            location = "Location unknown"
    except:
        location = "Location unknown"

    try:
        description = spotContent.find_all(
            'div',
            class_=
            "attractions-attraction-detail-about-card-AttractionDetailAboutCard__section--1_Efg"
        )[1].find_all('span')[0].text
        if not description:
            description = "No description about this place"
    except:
        description = "No description about this place"

    try:
        openTimeComps = spotContent.find(
            'span',
            class_="is-hidden-mobile header_detail").find_all('span',
                                                              class_="time")
        openTime = openTimeComps[0].text + "--" + openTimeComps[1].text
        if not openTime:
            openTime = "Open all day"
    except:
        openTime = "Open all day"

    images = []

    spotInfo = {
        'spotId': spotId,
        'name': name,
        'count': count,
        'location': location,
        'description': description,
        'openTime': openTime,
        'images': images
    }
    return spotInfo


def saveSpotInfo(spotInfo):
    spotTable.put_item(Item=spotInfo)
    return

"""
format the information and save into dynamodb
"""
def saveSpotIntoCity(cityName, spotId):
    cityId = ""
    for city in cities:
        if city['name'] == cityName:
            cityId = city['cityId']
    spots = cityTable.get_item(Key={'cityId': cityId})['Item']['spots']
    if spotId not in spots:
        spots.append(spotId)
    cityTable.update_item(Key={'cityId': cityId},
                          UpdateExpression="SET spots = :val",
                          ExpressionAttributeValues={
                              ":val": spots
                          })
    return

"""
use spot url to get all information of the spot
"""
def saveSpotByLink(cityName, spotLink):
    spotInfo = getSpotInfo(spotLink)
    print("save", spotLink)
    saveSpotInfo(spotInfo)
    saveSpotIntoCity(cityName, spotInfo['spotId'])
    return

"""
get spots' urls from attraction page
"""
def getCitySpotLinks(cityName):
    cityUrl = cityName + 'Url'
    cityContent = getContent(cityUrls[cityUrl])
    citySpotsList = cityContent.find_all(
        'div', class_="tracking_attraction_title listing_title")
    citySpotLinks = []
    for citySpot in citySpotsList:
        spotLink = citySpot.find_all('a')[0]['href']
        citySpotLinks.append(spotLink)
    return citySpotLinks

"""
get all spots from the city and store info
"""
def storeSpots(cityName):
    citySpotLinks = getCitySpotLinks(cityName)
    for citySpotLink in citySpotLinks:
        saveSpotByLink(cityName, citySpotLink)
    return

# usage: change parameter to city's name corresponding to city name in db
if __name__ == "__main__":
    cities = cityTable.scan()['Items']
    storeSpots("Vancouver") 