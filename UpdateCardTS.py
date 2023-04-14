import collections
import pathlib
import shutil
import sqlite3

import Config
import TSFile

# LocId : new row
ExtraLocalizationTexts: dict[int:dict[str, str]] = {
    9000000: {'enUS': 'Dragon Turtle', 'jaJP': '龙／龟'},
    9000001: {'enUS': 'Manticore', 'jaJP': '翼狮'},
    9000002: {'enUS': 'Zombie Ogre', 'jaJP': '灵俑／食人魔'},
    9000003: {'enUS': 'Skeleton Archer', 'jaJP': '骷髅妖／弓箭手'},
    9000004: {'enUS': 'Dragon Egg', 'jaJP': '龙／蛋'},
    9000005: {'enUS': 'Phyrexian Pegasus', 'jaJP': '非瑞人／飞马'}
}

# old SubtypeTextId : new SubtypeTextId
SubtypeTextPatchRules: dict[int:int] = {
    498439: 9000000,
    20912: 9000001,
    286058: 9000002,
    229573: 9000003,
    42935: 9000004,
    704311: 9000005
}

if __name__ == "__main__":
    if not Config.BACKUP_DIR.is_dir():
        Config.BACKUP_DIR.unlink(missing_ok=True)
        Config.BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    TSInfo = TSFile.loadTSInfo(
        '{0}/CardTS.json'.format(Config.RESOUCE_DIR), TSFile.TSFileType.JSON)
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
        for rawRow in cardDBCursor.execute('SELECT LocId,Formatted,KnownTitleId,enUS,jaJP,phyrexian FROM Localizations;'):
            RawData[rawRow[0]] = {
                'Formatted': rawRow[1],
                'KnownTitleId': rawRow[2],
                'enUS': rawRow[3],
                'jaJP': rawRow[4],
                'phyrexian': rawRow[5]
            }

        # remove useless rows
        cardDBCursor.execute('DROP TABLE Localizations')
        cardDBCursor.execute(
            'CREATE TABLE Localizations(LocId INT NOT NULL, Formatted INT NOT NULL, KnownTitleId INT,enUS TEXT, jaJP TEXT, phyrexian TEXT, PRIMARY KEY (LocId, Formatted));')
        cardDBCursor.execute('CREATE UNIQUE INDEX idx_loc ON Localizations (LocId, Formatted);')
        cardDBCursor.execute("CREATE INDEX idx_loc_enUS ON Localizations(enUS);")
        cardDBCursor.execute("CREATE INDEX idx_loc_jaJP ON Localizations(jaJP);")
        cardDBCursor.execute("CREATE INDEX idx_loc_phyrexian ON Localizations(phyrexian);")

        for rawKey, rawValue in RawData.items():
            strKey = str(rawKey)
            # patch translations
            if not TSInfo.__contains__(strKey):
                TSInfo[strKey] = {'oracleText': rawValue['enUS'],
                                  'translation': rawValue['enUS']}
            elif TSInfo[strKey]['oracleText'] != rawValue['enUS']:
                TSInfo[strKey] = {'oracleText': rawValue['enUS'],
                                  'translation': rawValue['enUS']}

            rawValue['jaJP'] = TSInfo[strKey]['translation']

            # write data to database
            cardDBCursor.execute('INSERT INTO Localizations(LocId, Formatted, KnownTitleId, enUS, jaJP, phyrexian) VALUES(:LocId, :Formatted, :KnownTitleId, :enUS, :jaJP, :phyrexian);',
                                 {'LocId': rawKey, 'Formatted': rawValue['Formatted'], 'KnownTitleId': rawValue['KnownTitleId'], 'enUS': rawValue['enUS'], 'jaJP': rawValue['jaJP'], "phyrexian": rawValue['phyrexian']})

        # patch extra loc texts
        for locId, row in ExtraLocalizationTexts.items():
            cardDBCursor.execute('INSERT INTO Localizations(LocId, Formatted, KnownTitleId, enUS, jaJP, phyrexian) VALUES(:LocId, :Formatted, :KnownTitleId, :enUS, :jaJP, :phyrexian);',
                                 {'LocId': locId, 'Formatted': 1, 'KnownTitleId': 1, 'enUS': row['enUS'], 'jaJP': row['jaJP'], "phyrexian": ""})

        # remove pre-8ed card style
        cardDBCursor.execute('UPDATE Cards SET AdditionalFrameDetails  = \'\' WHERE ExpansionCode = "BRR";')

        # patch the conflicting SubtypeTextId
        for oldKey, NewKey in SubtypeTextPatchRules.items():
            cardDBCursor.execute('UPDATE Cards SET SubtypeTextId = ? WHERE SubtypeTextId = ?;', (NewKey, oldKey))
            cardDBCursor.execute('UPDATE Enums SET LocId = ? WHERE LocId = ?;', (NewKey, oldKey))

        # 'GC' database file
        cardDBConnect.isolation_level = None
        cardDBCursor.execute('VACUUM')
        cardDBConnect.commit()

    sortTS = collections.OrderedDict()
    for i in sorted(TSInfo, key=lambda x: int(x)):
        sortTS[i] = TSInfo[i]

    TSFile.SaveTSInfo(sortTS, 'CardTS', TSFile.TSFileType.JSON)
