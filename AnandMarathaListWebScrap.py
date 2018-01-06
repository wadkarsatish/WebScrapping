import requests
from bs4 import BeautifulSoup
import simplejson
import json

anandMarathaUrl = "https://www.anandmaratha.com"
fileName = "AnandMaratha.json"

# get cookies for further
# session = requests.Session()
# session.post(anandMarathaUrl)
# cookie = session.cookies.get_dict()
# print(cookie)

sessionId = input("Enter Coockie Id : ")
cookie = {'PHPSESSID': sessionId}

baseUrl = "https://www.anandmaratha.com/search_listing.php"
page = requests.post(baseUrl, cookies=cookie)
soup = BeautifulSoup(page.text, 'html.parser')
count = soup.findAll("b")[0].text.split("of")[1].replace(' ', '')
print("Total Pages : " + count)
table = soup.find("table", {"class": "clearfix"})
headers = [header.getText(strip=True) for header in table.findAll("th")]

headers.insert(0, "Images")
headers.insert(1, "DetailsUrl")

results = []
print(baseUrl)

for i in range(int(count)):
    baseUrl = "https://www.anandmaratha.com/search_listing.php?&page=" + \
        str(i + 1) + "&val="
    print("Downloading... : " + baseUrl)
    page = requests.post(baseUrl, cookies=cookie)
    soup = BeautifulSoup(page.text, 'html.parser')
    table = soup.find("table", {"class": "clearfix"})

    for row in table.findAll("tr"):
        tempRow = {}
        for i, cell in enumerate(row.findAll("td")):
            if len(cell.find_all("a")) == 0:
                tempRow.update({headers[i]: cell.getText().replace(
                    '\n', '').replace(' ', '')})
            else:
                if(len(cell.find_all("img")) > 0):
                    tempRow.update(
                        {headers[0]: cell.find_all("img")[0]["src"]})

                if(len(cell.find_all("a")) > 0):
                    tempRow.update(
                        {headers[1]: anandMarathaUrl + "/" + cell.find_all("a")[0]["href"]})

        if tempRow != {}:
            results.append(tempRow)

# List write file
# file = open("list.json", "w")
# simplejson.dump(results, file)
# file.close()

# get details of each record
detailsResult = []
results.pop()
resultLength = len(results)
print("Total number matches the search criteria : " + str(resultLength))

try:
    # clear the file
    file = open("AnandMaratha.json", "w")
    file.close()

    for i, res in enumerate(results, 1):
        url = str(res.get("DetailsUrl"))
        print("Download result " + str(i) + " out of " +
              str(resultLength) + ": Url :" + url)

        if url != "None":
            # print(res.get("DetailsUrl"))
            page = requests.post(res.get("DetailsUrl"), cookies=cookie)
            soup = BeautifulSoup(page.text, 'html.parser')
            div = soup.find_all("div", {"class": "about-us-content"})
            imageDiv = div[0]
            detailsDiv = div[1]

            imagePath = imageDiv.find_all("img")[0]["src"]
            result = {"Image": anandMarathaUrl + "/" + imagePath}
            registrationNo = imageDiv.find_all("p")[0]
            result.update({"Id": registrationNo.getText().split(":")[
                0].replace('\n', '').replace(' ', '')})

            for row in detailsDiv.find_all("h5"):
                header = row.getText().split(":")[0].replace(
                    '\n', '').replace(' ', '')
                data = row.getText().split(":")[1].replace(
                    '\n', '').replace(' ', '')
                result.update({header: data})
            detailsResult.append(result)

        # if len(detailsResult) >= 20:
        #     # write file
        #     file = open("AnandMaratha_" + str(i) + ".json", "w")
        #     simplejson.dump(detailsResult, file)
        #     file.close()
        #     detailsResult = []

    # write file
    file = open("AnandMaratha_Complete.json", "w")
    simplejson.dump(detailsResult, file)
    file.close()
except Exception as e:
    print(e)
