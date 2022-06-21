import collections
import copy
import json
import pathlib
import shutil
import sqlite3

import UnityPy

import Config
import TSFile

if __name__ == "__main__":
    if not Config.BACKUP_DIR.is_dir():
        Config.BACKUP_DIR.unlink(missing_ok=True)
        Config.BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    if not Config.OUT_DIR.is_dir():
        Config.OUT_DIR.unlink(missing_ok=True)
        Config.OUT_DIR.mkdir(parents=True, exist_ok=True)

    TSInfo = TSFile.loadTSInfo(
        '{0}/UITS.json'.format(Config.RESOUCE_DIR), TSFile.TSFileType.JSON)
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

        # remove useless rows
        cardDBCursor.execute('DROP TABLE Loc')
        cardDBCursor.execute('CREATE TABLE Loc(Key TEXT PRIMARY KEY UNIQUE NOT NULL,Bundle'
                             ' TEXT,enUS TEXT,jaJP TEXT);')
        cardDBCursor.execute('CREATE UNIQUE INDEX Key ON Loc (Key);')

        for rawKey, rawValue in RawData.items():
            # patch translations
            if not TSInfo.__contains__(rawKey):
                TSInfo[rawKey] = {'oracleText': rawValue['enUS'],
                                  'translation': rawValue['enUS']}
                rawValue['jaJP'] = rawValue['enUS']
            elif TSInfo[rawKey]['oracleText'] != rawValue['enUS']:
                TSInfo[rawKey] = {'oracleText': rawValue['enUS'],
                                  'translation': rawValue['enUS']}
                rawValue['jaJP'] = rawValue['enUS']
            else:
                rawValue['jaJP'] = TSInfo[rawKey]['translation']

            # write data to database
            cardDBCursor.execute('INSERT INTO Loc(Key,Bundle,enUS,jaJP) VALUES(:Key,:Bundle,:enUS,:jaJP);',
                                 {'Key': rawKey, 'Bundle': rawValue['Bundle'], 'enUS': rawValue['enUS'], 'jaJP': rawValue['jaJP']})

        # 'GC' database file
        cardDBConnect.isolation_level = None
        cardDBCursor.execute('VACUUM')
        cardDBConnect.commit()

    locLibraryAsset = '{0}/resources.assets'.format(Config.WINDOWS_DATA_DIR)
    monoBehaviorName = 'LocLibrary'
    assetEnv = UnityPy.load(locLibraryAsset)
    for obj in assetEnv.objects:
        if obj.type != UnityPy.enums.ClassIDType.MonoBehaviour:
            continue

        objData = obj.read()
        if objData.name != monoBehaviorName:
            continue
        if not objData.serialized_type.nodes:
            # hook(or other method) AssetStudio::MonoBehaviourConverter::ConvertToTypeTree dump TypeTree::m_Nodes
            # when AssetStudio choose target monoBehaviour,the function will be called
            # then converter to UnityPy::helpers::TypeTreeHelper.py::read_typetree need format:
            # [{
            #    "level": 0,
            #    "type": "MonoBehaviour",
            #    "name": "Base",
            #    "meta_flag": 0
            # },
            # {
            #    "level": 1,
            #    "type": "int",
            #    "name": "m_SomeNode",
            #    "meta_flag": 0
            # }]
            with open('{0}/LocLibraryAssetTypeTree.json'.format(Config.RESOUCE_DIR), 'r', encoding='UTF-8') as f:
                typeTree = json.load(f)
            objData.serialized_type.nodes = typeTree

        objTree = objData.read_typetree()
        if not objTree:
            raise NotImplementedError('cannot found typetree in {0}:{1}'.format(
                locLibraryAsset, monoBehaviorName))

        for LocText in objTree['_texts']:
            if not TSInfo.__contains__(LocText['key']):
                TSInfo[LocText['key']] = {'oracleText': LocText['translations'][0]
                                          ['translation'], 'translation': LocText['translations'][0]['translation']}
            elif TSInfo[LocText['key']]['oracleText'] != LocText['translations'][0]['translation']:
                TSInfo[LocText['key']] = {'oracleText': LocText['translations'][0]
                                          ['translation'], 'translation': LocText['translations'][0]['translation']}

            enNode = copy.deepcopy(LocText['translations'][0])
            zhNode = copy.deepcopy(enNode)
            zhNode['lang'] = 'ja-JP'
            zhNode['translation'] = TSInfo[LocText['key']]['translation']
            LocText['translations'].clear()
            LocText['translations'].append(enNode)
            LocText['translations'].append(zhNode)

        obj.save_typetree(objTree)

    shutil.copy(locLibraryAsset, Config.BACKUP_DIR)
    assetName = pathlib.Path(locLibraryAsset).name
    with open('{0}/{1}'.format(Config.OUT_DIR, assetName), "wb") as f:
        f.write(assetEnv.file.save())

    TSFile.SaveTSInfo(TSInfo, 'UITS', TSFile.TSFileType.JSON)
