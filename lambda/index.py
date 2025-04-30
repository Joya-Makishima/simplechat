import json
import os
import re
import urllib.request
import ssl

# FastAPI
API_URL = os.environ.get("FASTAPI_ENDPOINT","https://2215-35-247-160-159.ngrok-free.app")
ssl._create_default_https_context = ssl._create_unverified_context


def extract_region_from_arn(arn: str) -> str:
    m = re.search(r"arn:aws:lambda:([^:]+):", arn)
    return m.group(1) if m else "us-east-1"


def lambda_handler(event, context):
    try:
        print("Received event:", json.dumps(event))

        #メッセージを取得
        body = json.loads(event["body"])
        message = body["message"]
        conversation_history = body.get("conversationHistory", [])
        print("Processing message:", message)

        #ペイロード
        req_payload = json.dumps(
            {
                "prompt": message,
                "max_new_tokens": 256,
                "temperature": 0.7,
                "top_p": 0.9,
                "do_sample": True,
            }
        ).encode("utf-8")

        request = urllib.request.Request(
            API_URL,
            data=req_payload,
            headers={"Content-Type": "application/json"},
        )

        with urllib.request.urlopen(request, timeout=30) as resp:
            resp_body = json.loads(resp.read().decode("utf-8"))

        print("FastAPI response:", resp_body)
        assistant_response = resp_body["generated_text"]

        # 会話履歴を更新（UI 側で使うなら）
        conversation_history.append({"role": "user", "content": message})
        conversation_history.append({"role": "assistant", "content": assistant_response})

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps(
                {
                    "success": True,
                    "response": assistant_response,
                    "conversationHistory": conversation_history,
                }
            ),
        }

    except Exception as e:
        print("Error:", str(e))
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
            },
            "body": json.dumps({"success": False, "error": str(e)}),
        }

