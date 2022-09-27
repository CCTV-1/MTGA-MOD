import json
import requests
import enum
import gzip

class MTGA_PLATFORM(enum.Enum):
    Windows = "windows"
    Android = "android"
    IOS = "ios"
    MacOS = 'macos'

playerId = "\0" #seem can be any Non-None value
clientVersion = "2022.19.11"
platformKey = MTGA_PLATFORM.MacOS.value

if __name__ == "__main__":
    resp = requests.post('https://doorbellprod.azurewebsites.net/api/ring?code=46u7OAmyEZ6AtfgaPUHiXNiC55/mrtp3aAmE018KZamDhvr0vZ8mxg==',
                data='{{"playerId":"{0}","clientVersion":"{1}","environmentKey":"Prod","platformKey":"{2}"}}'.format(playerId, clientVersion, platformKey))

    resJson = json.loads(resp.text)
    fileHash = resJson['contentHash']

    assetUri = "https://assets.mtgarena.wizards.com/Manifest_{0}.mtga".format(fileHash)

    resp = requests.get(assetUri)
    if resp.status_code != 200:
        raise Exception('can not found {0} manifest file'.format(platformKey))

    unCompContent = gzip.decompress(resp.content)
    manifestJson = json.loads(unCompContent)

    for assetNode in manifestJson['Assets']:
        if assetNode['Name'].startswith('Raw_CardDatabase'):
            print(assetNode['Name'])
        elif assetNode['Name'].startswith('Raw_ClientLocalization'):
            print(assetNode['Name'])
        else:
            continue