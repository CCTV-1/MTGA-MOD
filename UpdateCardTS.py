import collections
import pathlib
import shutil
import sqlite3

import Config
import TSFile

# LocId : new row
ExtraLocalizationTexts: dict[int:dict[str, str]] = {
    #subtype text
    9000000: {'enUS': 'Dragon Turtle', 'jaJP': '龙／龟'},
    9000001: {'enUS': 'Manticore', 'jaJP': '翼狮'},
    9000002: {'enUS': 'Zombie Ogre', 'jaJP': '灵俑／食人魔'},
    9000003: {'enUS': 'Skeleton Archer', 'jaJP': '骷髅妖／弓箭手'},
    9000004: {'enUS': 'Dragon Egg', 'jaJP': '龙／蛋'},
    9000005: {'enUS': 'Phyrexian Pegasus', 'jaJP': '非瑞人／飞马'},
    9000006: {'enUS': 'Giant Beaver', 'jaJP': '巨人／河狸'},
    9000007: {'enUS': 'Demon Wall', 'jaJP': '恶魔／墙'},
    9000008: {'enUS': 'Mongoose Lizard', 'jaJP': '猫鼬／蜥蜴'},
    #title text
    10000000: {'enUS': 'Charge', 'jaJP': '冲锋'},
}

# old SubtypeTextId : new SubtypeTextId
SubtypeTextPatchRules: dict[int:int] = {
    498439: 9000000,
    20912: 9000001,
    286058: 9000002,
    229573: 9000003,
    42935: 9000004,
    704311: 9000005,
    756615: 9000006,
    927984: 9000007
}

# old TitleId : new TitleId
TitleIDPatchRules: dict[int:int] = {
    58106: 10000000
}

if __name__ == "__main__":
    if not Config.BACKUP_DIR.is_dir():
        Config.BACKUP_DIR.unlink(missing_ok=True)
        Config.BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    TSInfo = TSFile.loadTSInfo(
        '{0}/CardTS.json'.format(Config.RESOUCE_DIR), TSFile.TSFileType.JSON)
    TSChangeInfo = collections.OrderedDict()
    DBDir = pathlib.Path('{0}/Downloads/Raw/'.format(Config.WINDOWS_DATA_DIR))
    DBPath = ''
    for assetFile in DBDir.iterdir():
        if 'Raw_CardDatabase_' in assetFile.name:
            DBPath = assetFile
            break
    if not DBPath:
        raise FileNotFoundError(
            'can not found Raw_CardDatabase_* file in {0}'.format(DBDir))

    RawData = collections.OrderedDict()

    shutil.copy(DBPath, Config.BACKUP_DIR)
    with sqlite3.connect(DBPath) as cardDBConnect:
        cardDBCursor = cardDBConnect.cursor()
        for rawRow in cardDBCursor.execute('SELECT LocId,Formatted,Loc FROM Localizations_enUS;'):
            # if Formatted == 0,the oracle text maybe contain non-ASCII character.
            # if Formatted == 1,the oracle text maybe contain style label and non-ASCII character.
            # if Formatted == 2,the oracle text is ASCII string.
            # client only use Formatted == 1 entry to display.
            # if a entry 0,1,2 text is equal,its maybe only have 1.
            # for convenience(this will cause lose style label) we just keep last entry then set it Formatted = 1.
            RawData[rawRow[0]] = {
                'Formatted': 1,
                'KnownTitleId': rawRow[1],
                'enUS': rawRow[2],
            }

        for rawRow in cardDBCursor.execute('SELECT LocId,Formatted,Loc FROM Localizations_jaJP;'):
            RawData[rawRow[0]]['jaJp'] = rawRow[2]

        # remove useless tables
        cardDBCursor.execute('DROP TABLE Localizations_deDE')
        cardDBCursor.execute('DROP TABLE Localizations_esES')
        cardDBCursor.execute('DROP TABLE Localizations_frFR')
        cardDBCursor.execute('DROP TABLE Localizations_itIT')
        cardDBCursor.execute('DROP TABLE Localizations_koKR')
        cardDBCursor.execute('DROP TABLE Localizations_ptBR')
        # recreate table
        cardDBCursor.execute('DROP TABLE Localizations_jaJP')
        cardDBCursor.execute(
            'CREATE TABLE Localizations_jaJP(LocId INT NOT NULL, Formatted INT NOT NULL, Loc TEXT, PRIMARY KEY (LocId, Formatted));')
        cardDBCursor.execute("CREATE INDEX idx_loc_jaJP ON Localizations_jaJP(Loc);")

        for rawKey, rawValue in RawData.items():
            strKey = str(rawKey)
            # patch translations
            if not TSInfo.__contains__(strKey):
                TSInfo[strKey] = {'oracleText': rawValue['enUS'],
                                  'translation': rawValue['enUS']}
                TSChangeInfo[strKey] = {'oracleText': rawValue['enUS'],
                                  'translation': rawValue['enUS']}
            elif TSInfo[strKey]['oracleText'] != rawValue['enUS']:
                TSInfo[strKey] = {'oracleText': rawValue['enUS'],
                                  'translation': rawValue['enUS']}
                TSChangeInfo[strKey] = {'oracleText': rawValue['enUS'],
                                  'translation': rawValue['enUS']}

            rawValue['jaJP'] = TSInfo[strKey]['translation']

            # write data to database
            cardDBCursor.execute('INSERT INTO Localizations_jaJP(LocId, Formatted, Loc) VALUES(:LocId, :Formatted, :jaJP);',
                                 {'LocId': rawKey, 'Formatted': rawValue['Formatted'], 'jaJP': rawValue['jaJP']})

        # patch extra loc texts
        for locId, row in ExtraLocalizationTexts.items():
            cardDBCursor.execute('INSERT INTO Localizations_enUS(LocId, Formatted, Loc) VALUES(:LocId, :Formatted, :enUS);',
                                 {'LocId': locId, 'Formatted': 1, 'enUS': row['enUS']})
            cardDBCursor.execute('INSERT INTO Localizations_jaJP(LocId, Formatted, Loc) VALUES(:LocId, :Formatted, :jaJP);',
                                 {'LocId': locId, 'Formatted': 1, 'jaJP': row['jaJP']})

        # remove pre-8ed card style
        # cardDBCursor.execute('UPDATE Cards SET AdditionalFrameDetails  = \'\' WHERE ExpansionCode = "BRR";')

        # patch the conflicting SubtypeTextId
        for oldKey, NewKey in SubtypeTextPatchRules.items():
            cardDBCursor.execute('UPDATE Cards SET SubtypeTextId = ? WHERE SubtypeTextId = ?;', (NewKey, oldKey))
            cardDBCursor.execute('UPDATE Enums SET LocId = ? WHERE LocId = ?;', (NewKey, oldKey))

        # patch the conflicting TitleId
        for oldKey, NewKey in TitleIDPatchRules.items():
            cardDBCursor.execute('UPDATE Cards SET TitleId = ? WHERE TitleId = ?;', (NewKey, oldKey))

        # 'GC' database file
        cardDBConnect.isolation_level = None
        cardDBCursor.execute('VACUUM')
        cardDBConnect.commit()

    # remove unused entry
    for rawKey in list(TSInfo.keys()):
        intKey = int(rawKey)
        if not RawData.__contains__(intKey):
            TSInfo.pop(rawKey)

    sortTS = collections.OrderedDict()
    sortChanges = collections.OrderedDict()
    for i in sorted(TSInfo, key=lambda x: int(x)):
        sortTS[i] = TSInfo[i]
    for i in sorted(TSChangeInfo, key=lambda x: int(x)):
        sortChanges[i] = TSChangeInfo[i]

    if sortChanges:
        TSFile.SaveTSInfo(sortTS, 'CardTS', TSFile.TSFileType.JSON)
        TSFile.SaveTSInfo(sortChanges, 'CardTSChange', TSFile.TSFileType.JSON)
