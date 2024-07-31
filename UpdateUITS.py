import collections
import copy
import json
import pathlib
import shutil
import sqlite3

import UnityPy

import Config
import TSFile

# key : new row
ExtraLocalizationTexts: dict[str:dict[str, str]] = {
    'ZoneType_Your_MainDeck': {'Bundle': '', 'enUS': 'Your Main Deck', 'jaJP': '你的主牌'},
}

if __name__ == "__main__":
    if not Config.BACKUP_DIR.is_dir():
        Config.BACKUP_DIR.unlink(missing_ok=True)
        Config.BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    if not Config.OUT_DIR.is_dir():
        Config.OUT_DIR.unlink(missing_ok=True)
        Config.OUT_DIR.mkdir(parents=True, exist_ok=True)

    TSInfo = TSFile.loadTSInfo(
        '{0}/UITS.json'.format(Config.RESOUCE_DIR), TSFile.TSFileType.JSON)
    TSChangeInfo = collections.OrderedDict()
    RawData = collections.OrderedDict()
    DBDir = pathlib.Path('{0}/Downloads/Raw/'.format(Config.WINDOWS_DATA_DIR))
    DBPath = ''
    for assetFile in DBDir.iterdir():
        if 'Raw_ClientLocalization_' in assetFile.name:
            DBPath = assetFile
            break
    if not DBPath:
        raise FileNotFoundError(
            'can not found Raw_ClientLocalization_* file in {0}'.format(DBDir))

    shutil.copy(DBPath, Config.BACKUP_DIR)
    with sqlite3.connect(DBPath) as cardDBConnect:
        cardDBCursor = cardDBConnect.cursor()

        for rawRow in cardDBCursor.execute('SELECT Key,Bundle,enUS,jaJP FROM Loc;'):
            RawData[rawRow[0]] = {
                'Bundle': rawRow[1],
                'enUS': rawRow[2],
                'jaJP': rawRow[3],
            }

        # remove useless column data(Core.Meta.Cards::DeckImportParser::GetLocalizedNames need these column exist)
        cardDBCursor.execute('DROP TABLE Loc')
        cardDBCursor.execute('CREATE TABLE Loc(Key TEXT PRIMARY KEY UNIQUE NOT NULL,Bundle'
                             ' TEXT,enUS TEXT,jaJP TEXT,ptBR TEXT DEFAULT (\'\'), frFR TEXT '
                             'DEFAULT (\'\'), itIT TEXT DEFAULT (\'\'), deDE TEXT DEFAULT (\'\')'
                             ', esES TEXT DEFAULT (\'\'), ruRU TEXT DEFAULT (\'\'), koKR TEXT'
                             ' DEFAULT (\'\'), zhCN TEXT DEFAULT (\'\'), zhTW TEXT DEFAULT (\'\'));')
        cardDBCursor.execute('CREATE UNIQUE INDEX Key ON Loc (Key);')

        for rawKey, rawValue in RawData.items():
            # patch translations
            if not TSInfo.__contains__(rawKey):
                TSInfo[rawKey] = {'oracleText': rawValue['enUS'],
                                  'translation': rawValue['enUS']}
                TSChangeInfo[rawKey] = {'oracleText': rawValue['enUS'],
                                  'translation': rawValue['enUS']}
                rawValue['jaJP'] = rawValue['enUS']
            elif TSInfo[rawKey]['oracleText'] != rawValue['enUS']:
                TSInfo[rawKey] = {'oracleText': rawValue['enUS'],
                                  'translation': rawValue['enUS']}
                TSChangeInfo[rawKey] = {'oracleText': rawValue['enUS'],
                                  'translation': rawValue['enUS']}
                rawValue['jaJP'] = rawValue['enUS']
            else:
                rawValue['jaJP'] = TSInfo[rawKey]['translation']

            # write data to database
            cardDBCursor.execute('INSERT INTO Loc(Key,Bundle,enUS,jaJP) VALUES(:Key,:Bundle,:enUS,:jaJP);',
                                 {'Key': rawKey, 'Bundle': rawValue['Bundle'], 'enUS': rawValue['enUS'], 'jaJP': rawValue['jaJP']})

        # patch extra loc texts
        for extraKey, extraValue in ExtraLocalizationTexts.items():
            cardDBCursor.execute('INSERT INTO Loc(Key,Bundle,enUS,jaJP) VALUES(:Key,:Bundle,:enUS,:jaJP);',
                                 {'Key': extraKey, 'Bundle': extraValue['Bundle'], 'enUS': extraValue['enUS'], 'jaJP': extraValue['jaJP']})

        # 'GC' database file
        cardDBConnect.isolation_level = None
        cardDBCursor.execute('VACUUM')
        cardDBConnect.commit()

    locLibraryAsset = '{0}/resources.assets'.format(Config.WINDOWS_DATA_DIR)
    #locLibraryAsset = '{0}/resources.assets'.format(Config.MACOS_RES_DIR)
    #locLibraryAsset = '{0}/cdaf79762ab211d4a99121c50d2507bc'.format(Config.ANDROID_DATA_DIR)
    assetObjectName = 'LocLibraryData'
    assetEnv = UnityPy.load(locLibraryAsset)
    for obj in assetEnv.objects:
        if obj.type != UnityPy.enums.ClassIDType.TextAsset:
            continue

        objData = obj.read()
        if objData.name != assetObjectName:
            continue

        LocJsonData = json.loads(objData.script)
        for LocText in LocJsonData:
            if not TSInfo.__contains__(LocText['Key']):
                TSInfo[LocText['Key']] = {'oracleText': LocText['Translations'][0]
                                          ['Translation'], 'translation': LocText['Translations'][0]['Translation']}
            elif TSInfo[LocText['Key']]['oracleText'] != LocText['Translations'][0]['Translation']:
                TSInfo[LocText['Key']] = {'oracleText': LocText['Translations'][0]
                                          ['Translation'], 'translation': LocText['Translations'][0]['Translation']}

            enNode = copy.deepcopy(LocText['Translations'][0])
            zhNode = copy.deepcopy(enNode)
            zhNode['Language'] = 'ja-JP'
            zhNode['Translation'] = TSInfo[LocText['Key']]['translation']
            LocText['Translations'].clear()
            LocText['Translations'].append(enNode)
            LocText['Translations'].append(zhNode)

        objData.script = bytes(json.dumps(LocJsonData), encoding='utf-8')
        objData.save()

    shutil.copy(locLibraryAsset, Config.BACKUP_DIR)
    assetName = pathlib.Path(locLibraryAsset).name
    with open('{0}/{1}'.format(Config.OUT_DIR, assetName), "wb") as f:
        f.write(assetEnv.file.save())

    # remove unused entry
    for rawKey in list(TSInfo.keys()):
        if not RawData.__contains__(rawKey):
            TSInfo.pop(rawKey)

    sortTS = collections.OrderedDict()
    sortChanges = collections.OrderedDict()
    for i in sorted(TSInfo):
        sortTS[i] = TSInfo[i]
    for i in sorted(TSChangeInfo):
        sortChanges[i] = TSChangeInfo[i]
    
    if sortChanges:
        TSFile.SaveTSInfo(sortTS, 'UITS', TSFile.TSFileType.JSON)
        TSFile.SaveTSInfo(sortChanges, 'UITSChange', TSFile.TSFileType.JSON)
