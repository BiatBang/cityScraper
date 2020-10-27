import boto3
import csv
from boto3.dynamodb.conditions import Key, Attr
from time import gmtime, strftime
import time
import random

def updateCsv():
    s3 = boto3.client('s3')
    with open('habit.csv', 'wb') as data:
        s3.download_fileobj('a3-user-habit', 'user-habit.csv', data)
    habitTable = boto3.resource('dynamodb').Table('user-habit')
    habits = habitTable.scan()['Items']
    timestamp = 0
    with open('habit.csv', 'r') as f:
        for row in reversed(list(csv.reader(f))):
            if len(row) <= 0:
                continue
            timestamp = int(row[2])
            break
    with open('habit.csv', 'a', newline='') as file:
        writer = csv.writer(file)
        for habit in habits:
            print(habit)
            timestamp += 1
            writer.writerow([habit['userId'], habit['spotId'], timestamp])
            try:
                habitTable.delete_item(Key={'habitId': habit['habitId']})
            except:
                print('no thing')
    bucket = boto3.resource('s3').Bucket("a3-user-habit")
    with open('habit.csv', 'rb') as tmp:
        bucket.put_object(Key='user-habit.csv', Body=tmp)


def updateCampaign():
    # create solution new version
    sArn = "arn:aws:personalize:us-east-1:735141600372:solution/a3-solution2"
    cArn = "arn:aws:personalize:us-east-1:735141600372:campaign/a3-campaign"
    personalize = boto3.client('personalize')
    # get latest solution
    solution = personalize.describe_solution(solutionArn=sArn)
    try:
        svArn = solution['solution']['latestSolutionVersion'][
            'solutionVersionArn']
        versionInfo = personalize.describe_solution_version(
            solutionVersionArn=svArn)
        while versionInfo['solutionVersion']['status'] != 'ACTIVE':
            time.sleep(20)
            versionInfo = personalize.describe_solution_version(
                solutionVersionArn=svArn)
            print(versionInfo['solutionVersion']['status'])
        # update campaign with latest solution
        print("after version", strftime("%Y-%m-%d %H:%M:%S", gmtime()))
        print(svArn)
        personalize.update_campaign(campaignArn=cArn, solutionVersionArn=svArn)
        print("after update campaign", strftime("%Y-%m-%d %H:%M:%S", gmtime()))
    except:
        print('version failed this time')
    print("before update solution", strftime("%Y-%m-%d %H:%M:%S", gmtime()))
    personalize.create_solution_version(solutionArn=sArn, trainingMode='FULL')

def getUserRecommendations():
    campaignArn = "arn:aws:personalize:us-east-1:735141600372:campaign/a3-campaign"
    personalize = boto3.client('personalize-runtime')
    userId = "uz3GMmIB43"
    spotTable = boto3.resource('dynamodb').Table('spot')
    recomSpots = []
    try:
        response = personalize.get_recommendations(campaignArn=campaignArn,
                                                userId=userId)
        itemList = response['itemList']
        for i in range(2):
            ran = random.randint(0, len(itemList)-1)
            spotItem = spotTable.get_item(Key={'spotId': itemList[ran]['itemId']})
            if 'Item' in spotItem:
                recomSpots.append(spotItem['Item'])
                print(spotItem['Item'])
    except Exception:
        print(Exception)
        print("didn't get recommendations")
    # print(recomSpots)

if __name__ == "__main__":
    updateCsv()
    updateCampaign()
    # getUserRecommendations()