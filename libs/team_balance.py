import requests

def get_balance(addr):
    try:
        response = requests.get(f"https://api.haskoin.com/btc/address/{addr}/balance")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error getting balance for address {addr}: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending request for address {addr}: {str(e)}")