import json
import pathlib
import shutil

import PIL
import UnityPy
from UnityPy.helpers.TypeTreeGenerator import TypeTreeGenerator

import Config

GameTypeTreeGenerator:TypeTreeGenerator = None

# asset path : monoBehavior name list
WINDOWS_FONT_RULES: dict[str:list] = {
    '{0}/resources.assets'.format(Config.WINDOWS_DATA_DIR): [
        'Font_Title_JP', 'Font_Default_JP', 'Font_Default_USERNAME'
    ],
    '{0}/sharedassets0.assets'.format(Config.WINDOWS_DATA_DIR): [
        'Font_Default', 'Font_Title'
    ],
    '{0}/Downloads/AssetBundle/Bucket_Card.FieldFont_0_9941e5ad-6ca062d7528a408fb341568888828fc9.mtga'.format(Config.WINDOWS_DATA_DIR): [
        'Font_Default', 'Font_Title', 'Font_Default_JP', 'Font_Title_JP'
    ],
    '{0}/Downloads/AssetBundle/Fonts_4892b8e6-8d8c41dee669c323c880cc5f75059a99.mtga'.format(Config.WINDOWS_DATA_DIR): [
        'Font_Default_USERNAME', 'Font_Title_USERNAME'
    ]
}

WINDOWS_MATERIAL_RULES: dict[str:list] = {
    '{0}/resources.assets'.format(Config.WINDOWS_DATA_DIR): [
        'Font_Title - DropShadow', 'Font_Title_JP - DropShadow', 'Font_Default - DropShadow'
    ],
    '{0}/Downloads/AssetBundle/Bucket_Card.FontMaterialSettings_0_61349fd6-be77a0308903a6564384ca37f10efbd9.mtga'.format(
        Config.WINDOWS_DATA_DIR): [
            'Font_Title - DropShadow', 'Font_Title_JP - DropShadow'
    ],
    '{0}/Downloads/AssetBundle/Fonts_4892b8e6-8d8c41dee669c323c880cc5f75059a99.mtga'.format(
        Config.WINDOWS_DATA_DIR): [
            'Font_Default - DropShadow'
    ]
}

MACOS_FONT_RULES: dict[str:list] = {
    '{0}/resources.assets'.format(Config.MACOS_RES_DIR): [
        'Font_Title_JP', 'Font_Default_JP', 'Font_Default_USERNAME'
    ],
    '{0}/sharedassets0.assets'.format(Config.MACOS_RES_DIR): [
        'Font_Default', 'Font_Title'
    ],
    '{0}/Downloads/AssetBundle/Bucket_Card.FieldFont_0_9b535ef6-6ca062d7528a408fb341568888828fc9.mtga'.format(Config.MACOS_DATA_DIR): [
        'Font_Default', 'Font_Title', 'Font_Default_JP', 'Font_Title_JP'
    ],
    '{0}/Downloads/AssetBundle/Fonts_72211418-8d8c41dee669c323c880cc5f75059a99.mtga'.format(Config.MACOS_DATA_DIR): [
        'Font_Default_USERNAME', 'Font_Title_USERNAME'
    ]
}

MACOS_MATERIAL_RULES: dict[str:list] = {
    '{0}/resources.assets'.format(Config.MACOS_RES_DIR): [
        'Font_Title - DropShadow', 'Font_Title_JP - DropShadow', 'Font_Default - DropShadow'
    ],
    '{0}/Downloads/AssetBundle/Bucket_Card.FontMaterialSettings_0_4bba7691-be77a0308903a6564384ca37f10efbd9.mtga'.format(
        Config.MACOS_DATA_DIR): [
            'Font_Title - DropShadow', 'Font_Title_JP - DropShadow'
    ],
    '{0}/Downloads/AssetBundle/Fonts_72211418-8d8c41dee669c323c880cc5f75059a99.mtga'.format(
        Config.MACOS_DATA_DIR): [
            'Font_Default - DropShadow'
    ]
}

# extract apk to Config.ANDROID_DATA_DIR/../../.. ,then extract obb/assets/bin/Data/* to
# Config.ANDROID_DATA_DIR,then extract obb/assets/assets/AssetBundle/Font_* to
# Config.ANDROID_DATA_DIR/AssetBundle
# asset path : monoBehavior name list,
ANDROID_FONT_RULES: dict[str:list] = {
    '{0}/805e1ce96cdd34dcdb7cd9f07bd03fe1'.format(Config.ANDROID_DATA_DIR): [
        'Font_Default_JP'
    ],
    '{0}/8f44988fc45234399b8d9b6b5bf64439'.format(Config.ANDROID_DATA_DIR): [
        'Font_Title_JP'
    ],
    '{0}/sharedassets0.assets'.format(Config.ANDROID_DATA_DIR): [
        'Font_Default', 'Font_Title'
    ],
    '{0}/AssetBundle/Bucket_Card.FieldFont_0_9aa2c83f-6ca062d7528a408fb341568888828fc9.mtga'.format(Config.ANDROID_DATA_DIR): [
        'Font_Default', 'Font_Title', 'Font_Default_JP', 'Font_Title_JP'
    ],
    '{0}/AssetBundle/Fonts_644f8fb2-8d8c41dee669c323c880cc5f75059a99.mtga'.format(Config.ANDROID_DATA_DIR): [
        'Font_Title_USERNAME', 'Font_Default_USERNAME'
    ]
}


ANDROID_MATERIAL_RULES: dict[str:list] = {
    '{0}/b23dd914b3aab694da0048175882674f'.format(Config.ANDROID_DATA_DIR): [
        'Font_Title - DropShadow'
    ],
    '{0}/3c076afdcf4ccb14ca714feb8769bc6b'.format(Config.ANDROID_DATA_DIR): [
        'Font_Title_JP - DropShadow'
    ],
    '{0}/351f23bf48c7814428089374c54eefa9'.format(Config.ANDROID_DATA_DIR): [
        'Font_Default - DropShadow'
    ],
    '{0}/AssetBundle/Bucket_Card.FontMaterialSettings_0_523fd1ac-be77a0308903a6564384ca37f10efbd9.mtga'.format(
        Config.ANDROID_DATA_DIR): [
            'Font_Title - DropShadow', 'Font_Title_JP - DropShadow'
    ],
    '{0}/AssetBundle/Fonts_644f8fb2-8d8c41dee669c323c880cc5f75059a99.mtga'.format(
        Config.ANDROID_DATA_DIR): [
            'Font_Default - DropShadow'
    ]
}


class FontContent():
    def __init__(self, texture: PIL.Image, monoBehavior: dict, material: dict) -> None:
        self.fontAtlas = texture
        self.fontMonoBehavior = monoBehavior
        self.fontMaterial = material


def loadTMPFont(assetPath: str, monoBehaviorName: str) -> FontContent:
    """
        if you want load splitN asset,and edit it,code as follows(you can also use\n
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
    assetEnv.typetree_generator = GameTypeTreeGenerator
    texture = None
    monoBehavior = {}
    material = {}
    materialPathID = 0
    texturePathID = 0
    for obj in assetEnv.objects:
        if obj.type != UnityPy.enums.ClassIDType.MonoBehaviour:
            continue
        try:
            if obj.peek_name() not in monoBehaviorName:
                continue
        except:
            #some rich type can't generate typetree
            continue
        objData = obj.parse_as_dict()
        if not objData:
            raise NotImplementedError('cannot found typetree in {0}:{1}'.format(
                assetPath, monoBehaviorName))
        monoBehavior = objData
        texturePathID = objData['m_AtlasTextures'][objData['m_AtlasTextureIndex']]['m_PathID']
        materialPathID = objData['m_Material']['m_PathID']
        break

    for obj in assetEnv.objects:
        if obj.path_id not in [texturePathID, materialPathID]:
            continue
        match obj.type:
            case UnityPy.enums.ClassIDType.Texture2D:
                textureData = obj.parse_as_object()
                texture = textureData.image
                # objData.image.save('{0} Atlas.png'.format(monoBehaviorName))
            case UnityPy.enums.ClassIDType.Material:
                objData = obj.parse_as_dict()
                material = objData
            case _:
                continue
        if texture and material:
            break

    return FontContent(texture, monoBehavior, material)


def replaceTMPFont(assetPath: str, monoBehaviorNames: list[str], newFontContent: FontContent, replaceMaterial: bool = False):
    """
        if you want load splitN asset,and edit it,code as follows(you can also use\n
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
    if not pathlib.Path(assetPath).is_file():
        print("{0} not found,skip it.".format(assetPath))
        return

    assetEnv = UnityPy.load(assetPath)
    assetEnv.typetree_generator = GameTypeTreeGenerator
    replacePathIDs = []
    for obj in assetEnv.objects:
        if obj.type != UnityPy.enums.ClassIDType.MonoBehaviour:
            continue
        try:
            if obj.peek_name() not in monoBehaviorNames:
                continue
        except:
            #some rich type can't generate typetree
            continue
        objTree = obj.parse_as_dict()
        if not objTree:
            raise NotImplementedError('cannot found typetree in {0}'.format(
                assetPath, monoBehaviorNames))

        # patch FileID,PathID,Name
        newFontContent.fontMonoBehavior['m_GameObject']['m_FileID'] = objTree['m_GameObject']['m_FileID']
        newFontContent.fontMonoBehavior['m_GameObject']['m_PathID'] = objTree['m_GameObject']['m_PathID']

        newFontContent.fontMonoBehavior['m_Name'] = objTree['m_Name']
        #newFontContent.fontMonoBehavior['hashCode'] = objTree['hashCode']
        #newFontContent.fontMonoBehavior['materialHashCode'] = objTree['materialHashCode']
        #newFontContent.fontMonoBehavior['m_SourceFontFileGUID'] = objTree['m_SourceFontFileGUID']

        newFontContent.fontMonoBehavior['m_Script']['m_FileID'] = objTree['m_Script']['m_FileID']
        newFontContent.fontMonoBehavior['m_Script']['m_PathID'] = objTree['m_Script']['m_PathID']

        newFontContent.fontMonoBehavior['m_Material']['m_FileID'] = objTree['m_Material']['m_FileID']
        newFontContent.fontMonoBehavior['m_Material']['m_PathID'] = objTree['m_Material']['m_PathID']

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
        replacePathIDs.append(objTree['m_Material']['m_PathID'])
        obj.patch(newFontContent.fontMonoBehavior)

    for obj in assetEnv.objects:
        if obj.path_id not in replacePathIDs:
            continue
        match obj.type:
            case UnityPy.enums.ClassIDType.Texture2D:
                textureData = obj.parse_as_object()
                textureData.image = newFontContent.fontAtlas
                textureData.m_Height = newFontContent.fontAtlas.height
                textureData.m_Width = newFontContent.fontAtlas.width
                textureData.save()
            case UnityPy.enums.ClassIDType.Material:
                if not replaceMaterial:
                    continue
                objTree = obj.parse_as_dict()
                if not objTree:
                    raise NotImplementedError('cannot found typetree in {0}:{1} material'.format(
                        assetPath, monoBehaviorNames))

                newFontContent.fontMaterial['m_Name'] = objTree['m_Name']
                #newFontContent.fontMaterial['m_ShaderKeywords'] = objTree['m_ShaderKeywords']
                newFontContent.fontMaterial['m_Shader']['m_FileID'] = objTree['m_Shader']['m_FileID']
                newFontContent.fontMaterial['m_Shader']['m_PathID'] = objTree['m_Shader']['m_PathID']

                for i in range(0, len(newFontContent.fontMaterial['m_SavedProperties']['m_TexEnvs'])):
                    newFontContent.fontMaterial['m_SavedProperties']['m_TexEnvs'][i][1]['m_Texture'][
                        'm_FileID'] = objTree['m_SavedProperties']['m_TexEnvs'][i][1]['m_Texture']['m_FileID']
                    newFontContent.fontMaterial['m_SavedProperties']['m_TexEnvs'][i][1]['m_Texture'][
                        'm_PathID'] = objTree['m_SavedProperties']['m_TexEnvs'][i][1]['m_Texture']['m_PathID']

                obj.patch(newFontContent.fontMaterial)
            case _:
                continue
        replacePathIDs.remove(obj.path_id)
        if not replacePathIDs:
            break

    shutil.copy(assetPath, Config.BACKUP_DIR)
    assetName = pathlib.Path(assetPath).name
    with open('{0}/{1}'.format(Config.OUT_DIR, assetName), "wb") as f:
        f.write(assetEnv.file.save())
    shutil.copy('{0}/{1}'.format(Config.OUT_DIR, assetName), assetPath)


def replaceTMPMaterial(assetPath: str, materialNames: str, newFontContent: FontContent):
    if not pathlib.Path(assetPath).is_file():
        print("{0} not found,skip it.".format(assetPath))
        return
    assetEnv = UnityPy.load(assetPath)
    assetEnv.typetree_generator = GameTypeTreeGenerator
    for obj in assetEnv.objects:
        try:
            if obj.peek_name() not in materialNames:
                continue
        except:
            #some rich type can't generate typetree
            continue
        if obj.type != UnityPy.enums.ClassIDType.Material:
            continue
        objTree = obj.parse_as_dict()

        newFontContent.fontMaterial['m_Name'] = objTree['m_Name']
        #newFontContent.fontMaterial['m_ShaderKeywords'] = objTree['m_ShaderKeywords']
        newFontContent.fontMaterial['m_Shader']['m_FileID'] = objTree['m_Shader']['m_FileID']
        newFontContent.fontMaterial['m_Shader']['m_PathID'] = objTree['m_Shader']['m_PathID']

        for i in range(0, len(newFontContent.fontMaterial['m_SavedProperties']['m_TexEnvs'])):
            newFontContent.fontMaterial['m_SavedProperties']['m_TexEnvs'][i][1]['m_Texture'][
                'm_FileID'] = objTree['m_SavedProperties']['m_TexEnvs'][i][1]['m_Texture']['m_FileID']
            newFontContent.fontMaterial['m_SavedProperties']['m_TexEnvs'][i][1]['m_Texture'][
                'm_PathID'] = objTree['m_SavedProperties']['m_TexEnvs'][i][1]['m_Texture']['m_PathID']

        obj.patch(newFontContent.fontMaterial)

    assetName = pathlib.Path(assetPath).name
    if not pathlib.Path('{0}/{1}'.format(Config.BACKUP_DIR, assetName)).exists():
        shutil.copy(assetPath, Config.BACKUP_DIR)
    with open('{0}/{1}'.format(Config.OUT_DIR, assetName), "wb") as f:
        f.write(assetEnv.file.save())
    shutil.copy('{0}/{1}'.format(Config.OUT_DIR, assetName), assetPath)


if __name__ == '__main__':
    UnityPy.config.FALLBACK_UNITY_VERSION = Config.GAME_UNITY_VERSION_STRING
    GameTypeTreeGenerator = TypeTreeGenerator(Config.GAME_UNITY_VERSION_STRING)
    GameTypeTreeGenerator.load_local_dll_folder(Config.GAME_DLL_DIR)

    if not Config.BACKUP_DIR.is_dir():
        Config.BACKUP_DIR.unlink(missing_ok=True)
        Config.BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    if not Config.OUT_DIR.is_dir():
        Config.OUT_DIR.unlink(missing_ok=True)
        Config.OUT_DIR.mkdir(parents=True, exist_ok=True)

    newFontContent = loadTMPFont(
        '{0}/msyh'.format(Config.WINDOWS_DATA_DIR), 'msyh SDF')

    for path, fontNames in MACOS_FONT_RULES.items():
        replaceTMPFont(path, fontNames, newFontContent, True)

    for path, materialName in MACOS_MATERIAL_RULES.items():
        replaceTMPMaterial(path, materialName, newFontContent)
