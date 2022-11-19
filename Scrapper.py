import json
import requests
from kafka import KafkaProducer
from afinn import Afinn
afinn = Afinn()


bearer = "AAAAAAAAAAAAAAAAAAAAAKjzjQEAAAAARrY8qjlI%2FGkk4qTu9og9%2FM2ry6Y%3D9gVhYTtVRAgDzv7b8epRtkkZZNZsQ5nO9jtH3Tu0R6euN32MXN"

def bauth(r):
    r.headers["Authorization"] = f"Bearer {bearer}"
    r.headers["User-Agent"] = "v2FilteredStreamPython"
    return r

def getrules():
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/stream/rules", auth=bauth
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot get rules (HTTP {}): {}".format(
                response.status_code, response.text)
        )
    print(json.dumps(response.json()))
    return response.json()

def deleterules(rules):
    if rules is None or "data" not in rules:
        return None

    id = list(map(lambda rule: rule["id"], rules["data"]))
    pl = {"delete": {"ids": id}}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        auth=bauth,
        json=pl
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot delete rules (HTTP {}): {}".format(
                response.status_code, response.text
            )
        )
    print(json.dumps(response.json()))

def setrules():
    srules = [
        {"value": "#covid19 -is:retweet -is:reply", "tag": "covid19"}
    ]
    pl = {"add": srules}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        auth=bauth,
        json=pl,
    )
    if response.status_code != 201:
        raise Exception(
            "Cannot add rules (HTTP {}): {}".format(
                response.status_code, response.text)
        )
    print(json.dumps(response.json()))


def stream(producer):
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/stream", auth=bauth, stream=True,
    )
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(
            "Cannot get stream (HTTP {}): {}".format(
                response.status_code, response.text
            )
        )
    print("waiting")
    for rline in response.iter_lines():
        if rline:
            print(rline)
            json_response = json.loads(rline)
            text = str(json_response["data"]["text"].encode('utf-8'))
            score = afinn.score(text)
            ojson = { 'text': text }
            sentiment = "Neutral"
            if score > 0:
                sentiment = "Positive"
            elif score < 0:
                sentiment = "Negative"
            ojson['sentiment'] = sentiment
            print(sentiment)
            publishdata(producer, 'assignment', json.dumps(ojson))

def connectkafka():
    produc = None
    try:
        produc = KafkaProducer(
            bootstrap_servers=['localhost:9092'], api_version=(0, 10), linger_ms=10)

    except Exception as ex:
        print('Exception while connecting Kafka')
        print(str(ex))
    finally:
        return produc


def publishdata(prodinstance,assignment,value):
    try:
        key_bytes = bytes('foo', encoding='utf-8')
        value_bytes = bytes(value, encoding='utf-8')
        prodinstance.send(assignment, key=key_bytes, value=value_bytes)
        prodinstance.flush()
    except Exception as ex:
        print('Exception in publishing message')
        print(str(ex))


def main():
    rules = getrules()
    deleterules(rules)
    setrules()
    prod = connectkafka()
    stream(prod)


if __name__ == "__main__":
    main()
