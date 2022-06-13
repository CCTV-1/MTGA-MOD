import json
import pathlib
import shutil

import PIL
import UnityPy

import Config


# asset path : monoBehavior name list
WINDOWS_REPLACE_RULES: dict[str:list] = {
    '{0}/resources.assets'.format(Config.WINDOWS_DATA_DIR): [
        'Font_Title_JP', 'Font_Default_JP', 'Font_Title_USERNAME', 'Font_Default_USERNAME'
    ],
    '{0}/sharedassets0.assets'.format(Config.WINDOWS_DATA_DIR): [
        'Font_Default', 'Font_Title'
    ],
    '{0}/Downloads/AssetBundle/Font_Font_Default_bdf9cfbb-5a0453a81269c26196a0f7339b3d7ef3.mtga'.format(Config.WINDOWS_DATA_DIR): [
        'Font_Default'
    ],
    '{0}/Downloads/AssetBundle/Font_Font_Title_153ccb23-5a8fd0b79202a37d39f8ac03b0471c5c.mtga'.format(Config.WINDOWS_DATA_DIR): [
        'Font_Title'
    ],
    '{0}/Downloads/AssetBundle/Font_Font_Default_JP_27d90eff-3211d70efd36e641d3112f62d96c7285.mtga'.format(Config.WINDOWS_DATA_DIR): [
        'Font_Default_JP'
    ],
    '{0}/Downloads/AssetBundle/Font_Font_Title_JP_4b112539-6a3448b361b09d436c45f92df9bfb891.mtga'.format(Config.WINDOWS_DATA_DIR): [
        'Font_Title_JP'
    ],
    '{0}/Downloads/AssetBundle/Font_Font_Default_USERNAME_debf830d-aaa57006d5c1d3afbf868e579d63f379.mtga'.format(Config.WINDOWS_DATA_DIR): [
        'Font_Default_USERNAME'
    ],
    '{0}/Downloads/AssetBundle/Font_Font_Title_USERNAME_eb0101e1-8853c9993afeda6cd0ecae186586988e.mtga'.format(Config.WINDOWS_DATA_DIR): [
        'Font_Title_USERNAME'
    ]
}

# extract apk to Config.ANDROID_DATA_DIR/../../.. ,then extract obb/assets/bin/Data/* to
# Config.ANDROID_DATA_DIR,then extract obb/assets/assets/AssetBundle/Font_* to
# Config.ANDROID_DATA_DIR/AssetBundle
# asset path : monoBehavior name list,
ANDROID_REPLACE_RULES: dict[str:list] = {
    '{0}/805e1ce96cdd34dcdb7cd9f07bd03fe1'.format(Config.ANDROID_DATA_DIR): [
        'Font_Default_JP'
    ],
    '{0}/8f44988fc45234399b8d9b6b5bf64439'.format(Config.ANDROID_DATA_DIR): [
        'Font_Title_JP'
    ],
    '{0}/d97c7fc66ef7bc147bfaec4c01d81061'.format(Config.ANDROID_DATA_DIR): [
        'Font_Title_USERNAME'
    ],
    '{0}/d8b63e10eaa567c4aa3ae8bd30be8009'.format(Config.ANDROID_DATA_DIR): [
        'Font_Title_USERNAME'
    ],
    '{0}/sharedassets0.assets'.format(Config.ANDROID_DATA_DIR): [
        'Font_Default', 'Font_Title'
    ],
    '{0}/AssetBundle/Font_Font_Default_2736e360-e0c808dc17939a7ea0a76402dbfcb405.mtga'.format(Config.ANDROID_DATA_DIR): [
        'Font_Default'
    ],
    '{0}/AssetBundle/Font_Font_Title_6950d97e-764baef053777a11d1c0a37e221148b5.mtga'.format(Config.ANDROID_DATA_DIR): [
        'Font_Title'
    ],
    '{0}/AssetBundle/Font_Font_Default_JP_d679d304-95703669021cbb5be7df6c342b187602.mtga'.format(Config.ANDROID_DATA_DIR): [
        'Font_Default_JP'
    ],
    '{0}/AssetBundle/Font_Font_Title_JP_18686823-2023f195934254e9089e663c502d42d0.mtga'.format(Config.ANDROID_DATA_DIR): [
        'Font_Title_JP'
    ],
    '{0}/AssetBundle/Font_Font_Default_USERNAME_d3398052-f89e675d31e3765edec09f0310e8e8bb.mtga'.format(Config.ANDROID_DATA_DIR): [
        'Font_Default_USERNAME'
    ],
    '{0}/AssetBundle/Font_Font_Title_USERNAME_2d152669-0cfbbd7dcceb9ab38e44c0398b6e55ba.mtga'.format(Config.ANDROID_DATA_DIR): [
        'Font_Title_USERNAME'
    ]
}


class FontContent():
    def __init__(self, texture: PIL.Image, monoBehavior: dict) -> None:
        self.fontAtlas = texture
        self.fontMonoBehavior = monoBehavior


def loadTMPFont(assetPath: str, monoBehaviorName: str) -> FontContent:
    """
        if you want load splitN asset,and edit it,code as follows(you can also use\ 
        other tools to binray merge files,then use `UnityPy.load(path)`):
        ```
        files = []
        #exist split0 ... split21
        for index in range(0,22):
            files.append('C:/sharedassets0.assets.split{0}'.format(index))
        env = UnityPy.load()
        env.load_files(files)
        for obj in env.objects:
            #do something
            pass
        for filePath in env.files.keys():
            with open(filePath, "wb") as f:
                f.write(env.files[filePath].save())
        ```
    """
    assetEnv = UnityPy.load(assetPath)
    texture = None
    monoBehavior = {}
    texturePathID = 0
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
            with open('{0}/TMPFontAssetTypeTree.json'.format(Config.RESOUCE_DIR), 'r', encoding='UTF-8') as f:
                typeTree = json.load(f)
            objData.serialized_type.nodes = typeTree
        objTree = objData.read_typetree()
        # with open('{0}.json'.format(monoBehaviorName), 'w', encoding='UTF-8') as f:
        #    json.dump(objTree, f, ensure_ascii=False)
        if not objTree:
            raise NotImplementedError('cannot found typetree in {0}:{1}'.format(
                assetPath, monoBehaviorName))
        monoBehavior = objTree
        texturePathID = objTree['m_AtlasTextures'][objTree['m_AtlasTextureIndex']]['m_PathID']
        break

    for obj in assetEnv.objects:
        if obj.path_id != texturePathID:
            continue
        if obj.type != UnityPy.enums.ClassIDType.Texture2D:
            continue
        objData = obj.read()
        texture = objData.image
        # objData.image.save('{0} Atlas.png'.format(monoBehaviorName))
    return FontContent(texture, monoBehavior)


def replaceTMPFont(assetPath: str, monoBehaviorNames: list[str], newFontContent: FontContent):
    """
        if you want load splitN asset,and edit it,code as follows(you can also use\ 
        other tools to binray merge files,then use `UnityPy.load(path)`):
        ```
        files = []
        #exist split0 ... split21
        for index in range(0,22):
            files.append('C:/sharedassets0.assets.split{0}'.format(index))
        env = UnityPy.load()
        env.load_files(files)
        for obj in env.objects:
            #do something
            pass
        for filePath in env.files.keys():
            with open(filePath, "wb") as f:
                f.write(env.files[filePath].save())
        ```
    """
    assetEnv = UnityPy.load(assetPath)
    texturePathIDs = []
    for obj in assetEnv.objects:
        if obj.type != UnityPy.enums.ClassIDType.MonoBehaviour:
            continue
        objData = obj.read()
        if objData.name not in monoBehaviorNames:
            continue
        if not objData.serialized_type.nodes:
            # see function:LoadTMPFont Notes
            with open('{0}/TMPFontAssetTypeTree.json'.format(Config.RESOUCE_DIR), 'r', encoding='UTF-8') as f:
                typeTree = json.load(f)
            objData.serialized_type.nodes = typeTree

        objTree = objData.read_typetree()
        if not objTree:
            raise NotImplementedError('cannot found typetree in {0}:{1}'.format(
                assetPath, objData.name))

        # patch FileID,PathID,Name
        newFontContent.fontMonoBehavior['m_GameObject']['m_FileID'] = objTree['m_GameObject']['m_FileID']
        newFontContent.fontMonoBehavior['m_GameObject']['m_PathID'] = objTree['m_GameObject']['m_PathID']

        newFontContent.fontMonoBehavior['m_Name'] = objTree['m_Name']

        newFontContent.fontMonoBehavior['m_Script']['m_FileID'] = objTree['m_Script']['m_FileID']
        newFontContent.fontMonoBehavior['m_Script']['m_PathID'] = objTree['m_Script']['m_PathID']

        newFontContent.fontMonoBehavior['material']['m_FileID'] = objTree['material']['m_FileID']
        newFontContent.fontMonoBehavior['material']['m_PathID'] = objTree['material']['m_PathID']

        newFontAtlasTextureIndex = newFontContent.fontMonoBehavior['m_AtlasTextureIndex']
        oldFontAtlasTextureIndex = objTree['m_AtlasTextureIndex']
        newFontContent.fontMonoBehavior['m_AtlasTextures'][newFontAtlasTextureIndex][
            'm_FileID'] = objTree['m_AtlasTextures'][oldFontAtlasTextureIndex]['m_FileID']
        newFontContent.fontMonoBehavior['m_AtlasTextures'][newFontAtlasTextureIndex][
            'm_PathID'] = objTree['m_AtlasTextures'][oldFontAtlasTextureIndex]['m_PathID']

        newFontContent.fontMonoBehavior['atlas']['m_FileID'] = objTree['atlas']['m_FileID']
        newFontContent.fontMonoBehavior['atlas']['m_PathID'] = objTree['atlas']['m_PathID']

        texturePathIDs.append(
            objTree['m_AtlasTextures'][objTree['m_AtlasTextureIndex']]['m_PathID'])
        obj.save_typetree(newFontContent.fontMonoBehavior)

    for obj in assetEnv.objects:
        if obj.path_id not in texturePathIDs:
            continue
        if obj.type != UnityPy.enums.ClassIDType.Texture2D:
            continue
        objData = obj.read()
        objData.set_image(img=newFontContent.fontAtlas)
        objData.m_Height = newFontContent.fontAtlas.height
        objData.m_Width = newFontContent.fontAtlas.width
        objData.save()

    shutil.copy(assetPath, Config.BACKUP_DIR)
    assetName = pathlib.Path(assetPath).name
    with open('{0}/{1}'.format(Config.OUT_DIR, assetName), "wb") as f:
        f.write(assetEnv.file.save())


if __name__ == '__main__':
    if not Config.BACKUP_DIR.is_dir():
        Config.BACKUP_DIR.unlink(missing_ok=True)
        Config.BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    if not Config.OUT_DIR.is_dir():
        Config.OUT_DIR.unlink(missing_ok=True)
        Config.OUT_DIR.mkdir(parents=True, exist_ok=True)

    newFontContent = loadTMPFont(
        '{0}/msyh'.format(Config.WINDOWS_DATA_DIR), 'msyh SDF')

    for path, fontNames in WINDOWS_REPLACE_RULES.items():
        replaceTMPFont(path, fontNames, newFontContent)
