import pymongo

client = pymongo.MongoClient("mongodb+srv://fromost:aB39936645@cluster0.ooprr.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = client["twitter"]
user_data = db["user_data"]
trackings = db["trackings"]

userid = "TheWilliamHK1"
channel = "<hzjlsfgbn>"

tweets_count = [x for x in user_data.find({},{f"{userid}_data":1,"_id":0}) if bool(x)]
print(tweets_count)
print(tweets_count[0][f"{userid}_data"]["tweets_count"])
#try:
#    user_data.delete_one({f"{userid}_data":{"tweets_count":tweets_count[1][f"{userid}_data"]["tweets_count"]}})
#except Exception as e:
#    print(e)

