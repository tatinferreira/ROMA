import requests
import time
import json
from win10toast import ToastNotifier

# 加载配置
def load_config():
    with open("config.json", "r") as f:
        return json.load(f)

# 获取用户 ID
def get_user_id(username, headers):
    url = f"https://api.twitter.com/2/users/by/username/{username}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()['data']['id']
    return None

# 获取用户推文
def get_latest_tweet(user_id, headers):
    url = f"https://api.twitter.com/2/users/{user_id}/tweets"
    params = {"max_results": 5}
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        if 'data' in data:
            return data['data'][0]  # 最新一条推文
    return None

# 发出通知
def notify(title, message):
    toaster = ToastNotifier()
    toaster.show_toast(title, message, duration=10)

# 主函数
def main():
    config = load_config()
    bearer_token = config["bearer_token"]
    usernames = config["usernames"]
    headers = {"Authorization": f"Bearer {bearer_token}"}

    # 存储上一次 tweet id
    last_seen = {}

    # 获取所有用户的 ID
    user_ids = {}
    for username in usernames:
        user_id = get_user_id(username, headers)
        if user_id:
            user_ids[username] = user_id
        else:
            print(f"Failed to get user ID for {username}")

    while True:
        for username, user_id in user_ids.items():
            tweet = get_latest_tweet(user_id, headers)
            if tweet:
                tweet_id = tweet['id']
                if username not in last_seen or tweet_id != last_seen[username]:
                    text = tweet['text']
                    notify(f"New tweet from @{username}", text[:280])
                    last_seen[username] = tweet_id
        time.sleep(30)

if __name__ == "__main__":
    main()
