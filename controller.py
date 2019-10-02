from typing import List, Dict
import requests
from datetime import datetime
import csv

URL_TEMPLATE = "https://{host}/v3/link/clicks?units={units}&access_token={token}&rollup=false&link={link}"
HOST = "api-ssl.bitly.com"
TOKEN = "ACCESS_TOKEN" # generate and place your access token here
START_TIMESTAMP = 1567321201  # UNIX timestamp from which you want to start collecting data

# Add links to this array
LINKS = [
    "abcd"  # this represents https://bit.ly/abcd
]


class ClickData:
    link: str
    clicks: int
    dt: int
    date: str


def _export_click_data_to_csv(all_data: Dict[str, List[ClickData]]):
    lines = []
    header_row = ["Url"]
    for link, clickData in all_data.items():
        for cd in clickData:
            if cd.date not in header_row:
                header_row.append(cd.date)
    lines.append(header_row)

    for link, clickData in all_data.items():
        row = [link]
        for i in range(1, len(header_row)):
            row.append(_get_data_for_date(clickData, header_row[i]))
        lines.append(row)

    with open('clicks.csv', 'w') as writeFile:
        writer = csv.writer(writeFile)
        writer.writerows(lines)
    writeFile.close()


def _get_click_data(link: str) -> List[ClickData]:
    url = URL_TEMPLATE.format(host=HOST, units=200, token=TOKEN, link=link)
    response = requests.get(url).json()
    if not response:
        print("Failed to get data for {link}".format(link=link))
        return []
    click_data_raw = response["data"]["link_clicks"]
    click_data: List[ClickData] = []
    for data in click_data_raw:
        if data["dt"] < START_TIMESTAMP:
            continue
        data_object = ClickData()
        data_object.link = link
        data_object.clicks = data["clicks"]
        data_object.dt = data["dt"]
        data_object.date = datetime.utcfromtimestamp(data_object.dt).strftime('%d-%m-%Y')
        click_data.append(data_object)
    return click_data


def _get_data_for_date(clickData, date):
    for cd in clickData:
        if cd.date == date:
            return str(cd.clicks)
    return "NA"


def main():
    all_data = {}
    for link in LINKS:
        link_full = "https://bit.ly/{link}".format(link=link)
        click_data = _get_click_data(link_full)
        all_data[link_full] = click_data
    _export_click_data_to_csv(all_data)
    return


if __name__ == "__main__":
    main()
