import collections
import pathlib
import shutil
import sqlite3

import Config
import TSFile

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
        for rawRow in cardDBCursor.execute('SELECT LocId,Formatted,KnownTitleId,enUS,jaJP FROM Localizations;'):
            RawData[rawRow[0]] = {
                'Formatted': rawRow[1],
                'KnownTitleId': rawRow[2],
                'enUS': rawRow[3],
                'jaJP': rawRow[4]
            }

        # remove useless line
        cardDBCursor.execute('DROP TABLE Localizations')
        cardDBCursor.execute(
            'CREATE TABLE Localizations(LocId INT NOT NULL, Formatted INT NOT NULL, KnownTitleId INT,enUS TEXT, jaJP TEXT, PRIMARY KEY (LocId, Formatted));')
        cardDBCursor.execute(
            'CREATE UNIQUE INDEX idx_loc ON Localizations (LocId, Formatted);')

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
            cardDBCursor.execute('INSERT INTO Localizations(LocId, Formatted, KnownTitleId, enUS, jaJP) VALUES(:LocId, :Formatted, :KnownTitleId, :enUS, :jaJP);',
                                 {'LocId': rawKey, 'Formatted': rawValue['Formatted'], 'KnownTitleId': rawValue['KnownTitleId'], 'enUS': rawValue['enUS'], 'jaJP': rawValue['jaJP']})

        # 'GC' database file
        cardDBConnect.isolation_level = None
        cardDBCursor.execute('VACUUM')
        cardDBConnect.commit()

    TSFile.SaveTSInfo(TSInfo, 'CardTS', TSFile.TSFileType.JSON)
