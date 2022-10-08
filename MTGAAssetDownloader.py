import json
import requests
import enum
import gzip


class MTGA_PLATFORM(enum.Enum):
    Windows = "windows"
    Android = "android"
    IOS = "ios"
    MacOS = 'macos'


playerId = "\0"  # seem can be any Non-None value
clientVersion = "2022.20.1"
platformKey = MTGA_PLATFORM.MacOS.value

if __name__ == "__main__":
    resp = requests.post('https://doorbellprod.azurewebsites.net/api/ring?code=46u7OAmyEZ6AtfgaPUHiXNiC55/mrtp3aAmE018KZamDhvr0vZ8mxg==',
                         data='{{"playerId":"{0}","clientVersion":"{1}","environmentKey":"Prod","platformKey":"{2}"}}'.format(playerId, clientVersion, platformKey))

    resJson = json.loads(resp.text)
    fileHash = resJson['contentHash']

    manifestAssetUri = "https://assets.mtgarena.wizards.com/Manifest_{0}.mtga".format(
        fileHash)

    resp = requests.get(manifestAssetUri)
    if resp.status_code != 200:
        # ’https://assets.mtgarena.wizards.com/External_{0}.{1}.{2}-{3}.mtga‘.format(clientVersion, build, SourceVersion, platformKey) value is hash
        # but if you want get "build" "SourceVersion",you need have client
        raise Exception('can not found {0} manifest file'.format(platformKey))

    unCompContent = gzip.decompress(resp.content)
    manifestJson = json.loads(unCompContent)

    rawAssetNames = []
    for assetNode in manifestJson['Assets']:
        # Raw_CardDatabase_ Raw_ClientLocalization_ shared 'Raw_C' and Raw_cards_ not use.
        if assetNode['Name'].startswith('Raw_C'):
            pass
        else:
            continue
        # print(assetNode['Name'])
        rawAssetNames.append(assetNode['Name'])

    for name in rawAssetNames:
        rawAssetUri = "https://assets.mtgarena.wizards.com/{0}.gz".format(name)
        resp = requests.get(rawAssetUri)
        if resp.status_code != 200:
            print("can not download:'{0}'".format(rawAssetUri))
            continue
        with open(name, 'wb') as f:
            f.write(gzip.decompress(resp.content))
