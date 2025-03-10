import requests

# https://account.tmysam.top/apis/thirdparty_token_verify.php?app=InfiniDoc&token=${token}


def tauthAuthenticator(token):
    url = f"https://account.tmysam.top/apis/thirdparty_token_verify.php?app=InfiniDoc&token={token}"
    response = requests.get(url)
    if (response.json()["success"]):
        return True, response.json()["uid"]
    else:
        return False, 0


if __name__ == "__main__":
    print(tauthAuthenticator(input("Enter token: ")))
