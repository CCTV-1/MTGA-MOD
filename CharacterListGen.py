import collections

import Config

TextResourceList = [
    'CharacterList.txt',
    'CardTS.json',
    'UITS.json'
]


def updateCharacterList(chDict: collections.OrderedDict, filename: str) -> None:
    with open('{0}/{1}'.format(Config.RESOUCE_DIR, filename), 'r', encoding='UTF-8') as f:
        fileContent = f.read()

    for ch in fileContent:
        chDict[ch] = 1


if __name__ == '__main__':
    characterDict = collections.OrderedDict()

    for filename in TextResourceList:
        updateCharacterList(characterDict, filename)

    fileContent = ''.join(characterDict)
    with open('{0}/{1}'.format(Config.RESOUCE_DIR, TextResourceList[0]), 'w', encoding='UTF-8') as f:
        f.write(fileContent)
