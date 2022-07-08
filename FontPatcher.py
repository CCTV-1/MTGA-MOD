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
    '{0}/Downloads/AssetBundle/Bucket_Card.FieldFont_0_6b8436a2-80b5ae3a3e2e95a1bf8bd98d3579b754.mtga'.format(Config.WINDOWS_DATA_DIR): [
        'Font_Default', 'Font_Title', 'Font_Default_JP', 'Font_Title_JP'
    ],
    '{0}/Downloads/AssetBundle/Fonts_000c0e73-559ead1d27f1e25e4eb2ee3379385e34.mtga'.format(Config.WINDOWS_DATA_DIR): [
        'Font_Default_USERNAME', 'Font_Title_USERNAME'
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
    '{0}/AssetBundle/Bucket_Card.FieldFont_0_43ae4143-80b5ae3a3e2e95a1bf8bd98d3579b754.mtga'.format(Config.ANDROID_DATA_DIR): [
        'Font_Default', 'Font_Title', 'Font_Default_JP', 'Font_Title_JP'
    ],
    '{0}/AssetBundle/Fonts_1efa7059-559ead1d27f1e25e4eb2ee3379385e34.mtga'.format(Config.ANDROID_DATA_DIR): [
        'Font_Title_USERNAME', 'Font_Default_USERNAME'
    ]
}


class FontContent():
    def __init__(self, texture: PIL.Image, monoBehavior: dict, material: dict) -> None:
        self.fontAtlas = texture
        self.fontMonoBehavior = monoBehavior
        self.fontMaterial = material


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
    material = {}
    materialPathID = 0
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
        materialPathID = objTree['material']['m_PathID']
        break

    for obj in assetEnv.objects:
        if obj.path_id not in [texturePathID, materialPathID]:
            continue
        match obj.type:
            case UnityPy.enums.ClassIDType.Texture2D:
                objData = obj.read()
                texture = objData.image
                # objData.image.save('{0} Atlas.png'.format(monoBehaviorName))
            case UnityPy.enums.ClassIDType.Material:
                objData = obj.read()
                if not objData.serialized_type.nodes:
                    with open('{0}/TMPFontMaterialTypeTree.json'.format(Config.RESOUCE_DIR), 'r', encoding='UTF-8') as f:
                        typeTree = json.load(f)
                    objData.serialized_type.nodes = typeTree
                objTree = objData.read_typetree()
                if not objTree:
                    raise NotImplementedError('cannot found typetree in {0}:{1}'.format(
                        assetPath, objData.name))
                material = objTree
            case _:
                continue
        if texture and material:
            break

    return FontContent(texture, monoBehavior, material)


def replaceTMPFont(assetPath: str, monoBehaviorNames: list[str], newFontContent: FontContent, replaceMaterial: bool = False):
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
    replacePathIDs = []
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

        replacePathIDs.append(
            objTree['m_AtlasTextures'][objTree['m_AtlasTextureIndex']]['m_PathID'])
        replacePathIDs.append(objTree['material']['m_PathID'])
        obj.save_typetree(newFontContent.fontMonoBehavior)

    for obj in assetEnv.objects:
        if obj.path_id not in replacePathIDs:
            continue
        match obj.type:
            case UnityPy.enums.ClassIDType.Texture2D:
                objData = obj.read()
                objData.set_image(img=newFontContent.fontAtlas)
                objData.m_Height = newFontContent.fontAtlas.height
                objData.m_Width = newFontContent.fontAtlas.width
                objData.save()
            case UnityPy.enums.ClassIDType.Material:
                if not replaceMaterial:
                    continue
                objData = obj.read()
                if not objData.serialized_type.nodes:
                    with open('{0}/TMPFontMaterialTypeTree.json'.format(Config.RESOUCE_DIR), 'r', encoding='UTF-8') as f:
                        typeTree = json.load(f)
                    objData.serialized_type.nodes = typeTree
                objTree = objData.read_typetree()
                if not objTree:
                    raise NotImplementedError('cannot found typetree in {0}:{1}'.format(
                        assetPath, objData.name))

                newFontContent.fontMaterial['m_Name'] = objTree['m_Name']
                newFontContent.fontMaterial['m_Shader']['m_FileID'] = objTree['m_Shader']['m_FileID']
                newFontContent.fontMaterial['m_Shader']['m_PathID'] = objTree['m_Shader']['m_PathID']
                newFontContent.fontMaterial['m_SavedProperties']['m_TexEnvs'] = objTree['m_SavedProperties']['m_TexEnvs']

                obj.save_typetree(newFontContent.fontMaterial)
            case _:
                continue
        replacePathIDs.remove(obj.path_id)
        if not replacePathIDs:
            break

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
