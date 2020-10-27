import boto3
from boto3.dynamodb.conditions import Key, Attr
import random
import csv

userTable = boto3.resource('dynamodb').Table('user')
spotTable = boto3.resource('dynamodb').Table('spot')
spotIds = []
userIds = []

def grabUserIds():
    users = userTable.scan()['Items']
    for user in users:
        userIds.append(user['userId'])

def grabSpotIds():
    spots = spotTable.scan()['Items']
    for spot in spots:
        spotIds.append(spot['spotId'])   

def createData():
    with open('user-habit.csv', 'w', newline='') as file:
        timestamp = 0
        writer = csv.writer(file)
        for userId in userIds:
            for i in range(60):
                ind = random.randint(0, len(spotIds) - 1)
                spot = spotTable.get_item(Key={'spotId':spotIds[ind]})['Item']
                if len(spot['images']) == 0:
                    i -= 1
                    continue
                print(len(spot['images']))
                writer.writerow([userId, spotIds[ind], timestamp])
                timestamp += 1
    return

if __name__ == "__main__":
    grabSpotIds()
    grabUserIds()
    createData()