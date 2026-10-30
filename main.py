import json
import os
import random
import string
import time
import urllib.request
import urllib.error


def generate_random_string(length=25):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


def send_webhook(url, message):
    final_message = f"{message}\n{generate_random_string(25)}"
    data = {"content": final_message}

    headers = {
        "Content-Type": "application/json",
        "User-Agent": "DiscordBot (Python-urllib)"
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers=headers,
        method="POST"
    )
    
    while True:
        try:
            with urllib.request.urlopen(req) as response:
                if response.status in (200, 204):
                    print(f"✅ 送信成功")
                    return 
                else:
                    print(f"ステータスコード: {response.status}")
                    return
        except urllib.error.HTTPError as e:
            if e.code == 429:
                try:
                    response_text = e.read().decode("utf-8")
                    response_json = json.loads(response_text)
                    retry_after = response_json.get("retry_after", 2.0)
                    
                    print(f"レート制限: {retry_after}秒待機します")
                    time.sleep(retry_after)
                    continue
                except Exception:
                    print("レート制限:3秒待機します")
                    time.sleep(3)
                    continue
            else:
                print(f"エラーが発生しました(HTTP {e.code}): {e.reason}")
                return
        except Exception as e:
            print(f"エラーが発生しました: {e}")
            return


def load_file_content(filename):
    if not os.path.exists(filename):
        return None
    with open(filename, "r", encoding="utf-8") as f:
        return f.read().strip()


def load_webhooks(filename="webhook.txt"):
    if not os.path.exists(filename):
        return []
    
    urls = []
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                urls.append(line)
    return urls


def main():
    print("=== Discord Webhook tool ===")

    message = load_file_content("message.txt")
    if not message:
        print("'message.txt'が見つからないか、中身が空です。")
        print("'message.txt'を作成して送信したいメッセージを記述してください。")
        return

    urls = load_webhooks("webhook.txt")
    if not urls:
        print("'webhook.txt'が見つからないか、有効なURLが記述されていません。")
        print("'webhook.txt'を作成し、1行に1つのWebhookを記入してください。")
        return

    print(f"\n{len(urls)}件のWebhook URLを読み込みました。")

    try:
        print("\n========================================")
        print("送信回数を入力してください")
        while True:
            try:
                count = int(input(" 送信回数: "))
                if count <= 0:
                    print("1以上の数字を入力してください。")
                    continue
                break
            except ValueError:
                print("有効な数字を入力してください。")

        print("\n送信間隔（秒）を入力してください")
        while True:
            try:
                interval = float(input(" 送信間隔: "))
                if interval < 0:
                    print("0以上の数字を入力してください。")
                    continue
                break
            except ValueError:
                print("有効な数字を入力してください。")

        print(f"\n送信を開始します...\n")
        
        for i in range(count):
            for url in urls:
                send_webhook(url, message)

            if i < count - 1:
                time.sleep(interval)         
                
        print("\n完了。")  
            
    except KeyboardInterrupt:
        print("\n終了しました")

if __name__ == "__main__":
    main()
