import collections
import enum
import json

class TSFileType(enum.Enum):
    XLSX = 0,
    JSON = 1


def loadTSInfo(filePath: str, type: TSFileType) -> dict:
    if type == TSFileType.JSON:
        with open(filePath, 'r', encoding='UTF-8') as f:
            TSInfo = json.load(f)
        return TSInfo
    else:
        import openpyxl
        TSBook = openpyxl.load_workbook(filePath, read_only=True)
        sheet = TSBook.active
        currentRow = 2
        TSInfo = {}
        while currentRow <= sheet.max_row:
            tsKey = sheet.cell(row=currentRow, column=1).value
            tsOracleText = sheet.cell(row=currentRow, column=2).value
            tsTranslation = sheet.cell(row=currentRow, column=3).value
            TSInfo[tsKey] = {'oracleText': tsOracleText,
                             'translation': tsTranslation}
            currentRow += 1
        return TSInfo


def SaveTSInfo(TSInfo: collections.OrderedDict, name: str, type: TSFileType):
    if type == TSFileType.XLSX:
        import openpyxl
        wb = openpyxl.Workbook()
        sheet = wb.create_sheet(name, 0)
        sheet.cell(1, 1, "键")
        sheet.cell(1, 2, "原文")
        sheet.cell(1, 3, "翻译")

        currentRow = 2

        for key, info in TSInfo.items():
            sheet.cell(currentRow, 1, key)
            sheet.cell(currentRow, 2, info['oracleText'])
            sheet.cell(currentRow, 3, info['translation'])
            currentRow += 1

        wb.save('{0}.xlsx'.format(name))
    elif type == TSFileType.JSON:
        with open('{0}.json'.format(name), 'w', encoding='UTF-8') as f:
            json.dump(TSInfo, f, ensure_ascii=False)
    else:
        pass