import boto3
from boto3.dynamodb.conditions import Key, Attr
import stringUtils

"""
input: a list of citynames
example: [{'city': 'Toronto', 'country': 'Canada'}, 'Montreal'
        {'city': 'Montreal', 'country': 'Canada'}]
"""
def addNewCity(cityInfos):
    cityTable = boto3.resource('dynamodb').Table('city')
    allCities = cityTable.scan()['Items']
    # for now don't input cities with same name
    for cityInfo in cityInfos:
        cityExsited = False
        for city in allCities:
            if city['name'] == cityInfo['city']:
                cityExsited = True
                break
        if not cityExsited:
            idexisted = True
            while idexisted:
                randomId = stringUtils.randomString(10)
                ci = cityTable.get_item(Key={'cityId': randomId})
                if 'Item' not in ci:
                    idexisted = False
            randomId = stringUtils.randomString(10)
            city = {
                'cityId': randomId,
                'name': cityInfo['city'],
                'country': cityInfo['country'],
                'spots': []
            }
            cityTable.put_item(Item = city)

if __name__ == "__main__":
    addNewCity([{
        'city': 'Toronto',
        'country': 'Canada'
    }, {
        'city': 'Montreal',
        'country': 'Canada'
    }, {
        'city': 'Vancouver',
        'country': 'Canada'
    }, {
        'city': 'Ottawa',
        'country': 'Canada'
    }, {
        'city': 'Seattle',
        'country': 'United States'
    }, {
        'city': 'Chicago',
        'country': 'United States'
    }, {
        'city': 'New York City',
        'country': 'United States'
    }, {
        'city': 'Boston',
        'country': 'United States'
    }, {
        'city': 'San Francisco',
        'country': 'United States'
    }, {
        'city': 'Los Angeles',
        'country': 'United States'
    }, {
        'city': 'Las Vegas',
        'country': 'United States'
    }, {
        'city': 'Washington DC',
        'country': 'United States'
    }])

    #Seattle, Chicago, NYC, Boston, San Francisco, Los Angeles, Las Vegas, Washington DC
