import boto3
from boto3.dynamodb.conditions import Key, Attr

cityTable = boto3.resource('dynamodb').Table('city')
spotTable = boto3.resource('dynamodb').Table('spot')

def addCity(spotId, cityId):
    # spot = spotTable.get_item(spotId)
    # print(spot)
    spotTable.update_item(Key={'spotId': spotId},
                          UpdateExpression="SET cityId = :val",
                          ExpressionAttributeValues={":val": cityId})

def addCity2Spot():
    cities = cityTable.scan()['Items']
    for city in cities:
        cityId = city['cityId']
        spots = city['spots']
        # addCity(spots[0], cityId)
        for spot in spots:
            addCity(spot, cityId)

if __name__ == "__main__":
    addCity2Spot()