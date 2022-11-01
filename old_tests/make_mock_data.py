import requests
import wget

response = requests.get("https://www.pref.okinawa.jp/toukeika/estimates/estidata.html")
with open("./mock_data/response_mock_at_2022_10_25.txt", "w") as f:
    f.write(response.text)

file_url = "https://www.pref.okinawa.jp/toukeika/estimates/2022/pop202209.xls"
wget.download(file_url, out="./mock_data")
