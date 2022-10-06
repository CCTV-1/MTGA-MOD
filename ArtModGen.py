import enum
import json
import pathlib
import shutil

import UnityPy
from PIL import Image

import Config

MTGAAssetDir = pathlib.Path(
    '{0}/Downloads/AssetBundle/'.format(Config.WINDOWS_DATA_DIR))
MTGAAltRuleDir = pathlib.Path(
    '{0}/Downloads/ALT/'.format(Config.WINDOWS_DATA_DIR))


class AssetType(enum.Enum):
    # Art ==> {artId}_CardArt_{fileCrc}-{assetUid}.mtga
    CardArt = "CardArt"
    # Data_cards_{assetUid}.mtga
    CardDataBase = "CardDataBase"
    # AssetLookupTree_Card_Parts_{PartType}_{fileCrc}-{assetUid}.mtga
    CardParts = "CardParts"


PATCH_TARGET_LIST: dict = {
    AssetType.CardArt:
    [
        ## UND
        #"410991",
        #"410992",
        #"410993",
        #"410994",
        #"410995",
        ## UST
        #"162621",
        #"162622",
        #"162623",
        #"162624",
        #"162625",
        ## GRN
        #"402471",
        #"402472",
        #"402473",
        #"402474",
        #"402475",
        ## RNA
        #"402478",
        #"402479",
        #"402480",
        #"402481",
        #"402482",
        ## ANB
        #"089172",
        #"138668",
        #"159811",
        #"401902",
        #"403289",
        # KHM
        "416564",
        "416565",
        "416566",
        "416567",
        "416568"
    ],
    AssetType.CardParts:
    {
        "ALT_Card.Parts.ArtInFramePart":
        {
            "Nodes":
            [
                {
                    "NodeType": 4,
                    "NodeId": "27b5f2ab-5476-4814-a234-fadf33b12c1c",
                    "Comment": None,
                    "ExtractorType": "AssetLookupTree.Extractors.CardData.CardData_SetCode"
                },
                {
                    "NodeType": 3,
                    "NodeId": "4553b7c2-c028-43e0-b466-27734fe2cc63",
                    "Comment": None,
                    "ExtractorType": "AssetLookupTree.Extractors.CardData.CardData_CardType"
                },
                {
                    "NodeType": 4,
                    "NodeId": "27b5f2ab-5476-4814-a234-fadf33b12c1d",
                    "Comment": None,
                    "ExtractorType": "AssetLookupTree.Extractors.CardData.CardData_SetCode"
                },
                {
                    "NodeType": 3,
                    "NodeId": "4553b7c2-c028-43e0-b466-27734fe2cc64",
                    "Comment": None,
                    "ExtractorType": "AssetLookupTree.Extractors.CardData.CardData_CardType"
                }
            ],
            "Connections":
            [
                {
                    "Parent": "55b9c04c-e2d3-4310-9f88-7566156a03d5",
                    "Child":
                    [
                        ("4553b7c2-c028-43e0-b466-27734fe2cc63", 4)
                    ]
                },
                {
                    "Parent": "b73cf4d3-b3a6-4313-941a-5ed527f2ac69",
                    "Child":
                    [
                        ("4553b7c2-c028-43e0-b466-27734fe2cc64", 6)
                    ]
                },
                {
                    "Parent": "30271f76-9c3e-4118-9022-1299d70400e1",
                    "Child":
                    {
                        "ANB": "6d03141a-96fb-4dbc-86f9-6bb7463fb44a"
                    }
                },
                {
                    "Parent": "4553b7c2-c028-43e0-b466-27734fe2cc63",
                    "Child":
                    {
                        "5": "27b5f2ab-5476-4814-a234-fadf33b12c1c"
                    }
                },
                {
                    "Parent": "27b5f2ab-5476-4814-a234-fadf33b12c1c",
                    "Child":
                    {
                        "GRN": "247bcae2-0ac9-458f-8657-2a3480970860",
                        "RNA": "247bcae2-0ac9-458f-8657-2a3480970860",
                        "ANB": "247bcae2-0ac9-458f-8657-2a3480970860"
                    }
                },
                {
                    "Parent": "4553b7c2-c028-43e0-b466-27734fe2cc64",
                    "Child":
                    {
                        "5": "27b5f2ab-5476-4814-a234-fadf33b12c1d"
                    }
                },
                {
                    "Parent": "27b5f2ab-5476-4814-a234-fadf33b12c1d",
                    "Child":
                    {
                        "GRN": "46eb8c50-bdf5-4619-8acc-a20e57a832e2",
                        "RNA": "46eb8c50-bdf5-4619-8acc-a20e57a832e2",
                        "ANB": "46eb8c50-bdf5-4619-8acc-a20e57a832e2"
                    }
                }
            ]
        },
        "ALT_Card.Parts.CardBasePart":
        {
            "Nodes":
            [
                {
                    "NodeType": 4,
                    "NodeId": "27b5f2ab-5476-4814-a234-fadf33b12c1a",
                    "Comment": None,
                    "ExtractorType": "AssetLookupTree.Extractors.CardData.CardData_SetCode"
                },
                {
                    "NodeType": 3,
                    "NodeId": "4553b7c2-c028-43e0-b466-27734fe2cc61",
                    "Comment": None,
                    "ExtractorType": "AssetLookupTree.Extractors.CardData.CardData_CardType"
                },
                {
                    "NodeType": 4,
                    "NodeId": "27b5f2ab-5476-4814-a234-fadf33b12c1b",
                    "Comment": None,
                    "ExtractorType": "AssetLookupTree.Extractors.CardData.CardData_SetCode"
                },
                {
                    "NodeType": 3,
                    "NodeId": "4553b7c2-c028-43e0-b466-27734fe2cc62",
                    "Comment": None,
                    "ExtractorType": "AssetLookupTree.Extractors.CardData.CardData_CardType"
                }
            ],
            "Connections":
            [
                {
                    "Parent": "d0079ff2-5a53-4c54-bbee-26cf984ae75e",
                    "Child":
                    {
                        "ANB": "41798323-4098-419f-afe5-fd6d73fef620"
                    }
                },
                {
                    "Parent": "71f8974a-8fcd-49e0-bd4f-99fbab58f78c",
                    "Child":
                    {
                        "ANB": "147a9d6e-e12d-4d55-b4db-394df16a8b66"
                    }
                },
                {
                    "Parent": "3d476745-8066-4fbc-b302-b71b53423ef6",
                    "Child":
                    {
                        "ANB": "0db063c3-afe4-48f8-a655-46ec9a24142f"
                    }
                },
                {
                    "Parent": "2bf8467c-b3f9-4e7d-87f8-8206e496cfb6",
                    "Child":
                    [
                        ("4553b7c2-c028-43e0-b466-27734fe2cc61", 5)
                    ]
                },
                {
                    "Parent": "2e5f79d0-c9af-4dc9-9932-db5be2836ba1",
                    "Child":
                    [
                        ("4553b7c2-c028-43e0-b466-27734fe2cc62", 10)
                    ]
                },
                {
                    "Parent": "4553b7c2-c028-43e0-b466-27734fe2cc61",
                    "Child":
                    {
                        "5": "27b5f2ab-5476-4814-a234-fadf33b12c1a"
                    }
                },
                {
                    "Parent": "27b5f2ab-5476-4814-a234-fadf33b12c1a",
                    "Child":
                    {
                        "GRN": "c5b7de3d-c32b-4165-a7b0-48421f91fd87",
                        "RNA": "c5b7de3d-c32b-4165-a7b0-48421f91fd87"
                    }
                },
                {
                    "Parent": "4553b7c2-c028-43e0-b466-27734fe2cc62",
                    "Child":
                    {
                        "5": "27b5f2ab-5476-4814-a234-fadf33b12c1b"
                    }
                },
                {
                    "Parent": "27b5f2ab-5476-4814-a234-fadf33b12c1b",
                    "Child":
                    {
                        "GRN": "43598d99-e38a-403f-b7a9-042ec60d18f8",
                        "RNA": "43598d99-e38a-403f-b7a9-042ec60d18f8"
                    }
                }
            ]
        },
        "ALT_Card.Parts.TextBoxPart":
        {
            "Nodes":
            [
                {
                    "NodeType": 4,
                    "NodeId": "27b5f2ab-5476-4814-a234-fadf33b12c17",
                    "Comment": None,
                    "ExtractorType": "AssetLookupTree.Extractors.CardData.CardData_SetCode"
                },
                {
                    "NodeType": 3,
                    "NodeId": "4553b7c2-c028-43e0-b466-27734fe2cc5e",
                    "Comment": None,
                    "ExtractorType": "AssetLookupTree.Extractors.CardData.CardData_CardType"
                }
            ],
            "Connections":
            [
                {
                    "Parent": "979f78dc-311c-41e0-b722-8b8f2cc6e4e8",
                    "Child":
                    [
                        ("4553b7c2-c028-43e0-b466-27734fe2cc5e", 6)
                    ]
                },
                {
                    "Parent": "4553b7c2-c028-43e0-b466-27734fe2cc5e",
                    "Child":
                    {
                        "5": "27b5f2ab-5476-4814-a234-fadf33b12c17"
                    }
                },
                {
                    "Parent": "27b5f2ab-5476-4814-a234-fadf33b12c17",
                    "Child":
                    {
                        "GRN": "b8713afe-90c8-491a-91f7-ffad7153953a",
                        "RNA": "b8713afe-90c8-491a-91f7-ffad7153953a"
                    }
                }
            ]
        },
        "ALT_Card.Parts.TitleBarPart":
        {
            "Nodes":
            [
                {
                    "NodeType": 4,
                    "NodeId": "27b5f2ab-5476-4814-a234-fadf33b12c18",
                    "Comment": None,
                    "ExtractorType": "AssetLookupTree.Extractors.CardData.CardData_SetCode"
                },
                {
                    "NodeType": 3,
                    "NodeId": "4553b7c2-c028-43e0-b466-27734fe2cc5f",
                    "Comment": None,
                    "ExtractorType": "AssetLookupTree.Extractors.CardData.CardData_CardType"
                },
                {
                    "NodeType": 4,
                    "NodeId": "27b5f2ab-5476-4814-a234-fadf33b12c19",
                    "Comment": None,
                    "ExtractorType": "AssetLookupTree.Extractors.CardData.CardData_SetCode"
                },
                {
                    "NodeType": 3,
                    "NodeId": "4553b7c2-c028-43e0-b466-27734fe2cc60",
                    "Comment": None,
                    "ExtractorType": "AssetLookupTree.Extractors.CardData.CardData_CardType"
                }
            ],
            "Connections":
            [
                {
                    "Parent": "9cf4275e-67d7-41ba-9901-b508ab872563",
                    "Child":
                    {
                        # "RelativePath": "Assets/Core/DuelScene/Cards/NewCDCPrefabs/CDCParts/Titlebar/Card Part - Titlebar NONE.prefab"
                        "ANB": "39e6b418-7cbb-45c1-a07e-4969ece6c002"
                    }
                },
                {
                    "Parent": "5ebad367-7f26-4ff4-bd1d-daf66d8e6781",
                    "Child":
                    {
                        # "RelativePath": "Assets/Core/DuelScene/Cards/NewCDCPrefabs/Parts/Prefabs/Custom/Title - Land Unstable.prefab"
                        "ANB": "5f886fb4-2397-4784-a00e-5e7d11283a78"
                    }
                },
                {
                    "Parent": "23680b97-ff0b-471a-a585-64008429f70c",
                    "Child":
                    [
                        ("4553b7c2-c028-43e0-b466-27734fe2cc5f", 5)
                    ]
                },
                {
                    "Parent": "4c6888d5-cfb1-418b-95a3-b2a377f0ed6f",
                    "Child":
                    [
                        ("4553b7c2-c028-43e0-b466-27734fe2cc60", 9)
                    ]
                },
                {
                    "Parent": "4553b7c2-c028-43e0-b466-27734fe2cc5f",
                    "Child":
                    {
                        "5": "27b5f2ab-5476-4814-a234-fadf33b12c18"
                    }
                },
                {
                    "Parent": "27b5f2ab-5476-4814-a234-fadf33b12c18",
                    "Child":
                    {
                        "GRN": "bb17d38f-a58c-4bb1-8ec4-2f1cb37e5baf",
                        "RNA": "bb17d38f-a58c-4bb1-8ec4-2f1cb37e5baf",
                        "ANB": "bb17d38f-a58c-4bb1-8ec4-2f1cb37e5baf"
                    }
                },
                {
                    "Parent": "4553b7c2-c028-43e0-b466-27734fe2cc60",
                    "Child":
                    {
                        "5": "27b5f2ab-5476-4814-a234-fadf33b12c19"
                    }
                },
                {
                    "Parent": "27b5f2ab-5476-4814-a234-fadf33b12c19",
                    "Child":
                    {
                        "GRN": "6954ab17-60fe-491d-b51e-0ced808d094d",
                        "RNA": "6954ab17-60fe-491d-b51e-0ced808d094d",
                        "ANB": "6954ab17-60fe-491d-b51e-0ced808d094d"
                    }
                }
            ]
        }
    },
    AssetType.CardDataBase:
    {
        # set code => art id to find json node => do json patch
        # Example: { ... "artId": 89172, ... "set": "ANB", ... } to { ... "artId": 89172, "artSize": 2, ... "set": "ANB", ... }
        "ANB":
        {
            89172: {"artSize": 421791},
            138668: {"artSize": 421789},
            159811: {"artSize": 421792},
            401902: {"artSize": 421793},
            403289: {"artSize": 421790}
        },
        "GRN":
        {
            402471: {"artId": 421802},
            402472: {"artId": 421795},
            402473: {"artId": 421801},
            402474: {"artId": 421800},
            402475: {"artId": 421798}
        },
        "RNA":
        {
            402478: {"artId": 421794},
            402479: {"artId": 421803},
            402480: {"artId": 421799},
            402481: {"artId": 421796},
            402482: {"artId": 421797}
        },
        "KHM": {
            416564: {"artSize": 2, "rawFrameDetails": "full frame"},
            416565: {"artSize": 2, "rawFrameDetails": "full frame"},
            416566: {"artSize": 2, "rawFrameDetails": "full frame"},
            416567: {"artSize": 2, "rawFrameDetails": "full frame"},
            416568: {"artSize": 2, "rawFrameDetails": "full frame"}
        }
    }
}


def patch_art(artId: str):
    assetNamePrefix = '{0}_CardArt_'.format(artId)
    replaceArtFile = pathlib.Path(
        '{0}/{1}.png'.format(Config.RESOUCE_DIR, artId))
    for assetFile in MTGAAssetDir.iterdir():
        if assetFile.name.startswith(assetNamePrefix):
            if not replaceArtFile.is_file():
                raise FileNotFoundError('can not found replace art')

            shutil.copy(assetFile, Config.BACKUP_DIR)

            assetEnv = UnityPy.load(str(assetFile))
            for obj in assetEnv.objects:
                if obj.type == UnityPy.enums.ClassIDType.Texture2D:
                    if obj.container.endswith("_AIF.tga"):
                        objData = obj.read()
                        pil_img = Image.open(str(replaceArtFile))
                        objData.set_image(img=pil_img, in_cab=True)
                        objData.save()

            with open('{0}/{1}'.format(Config.OUT_DIR, assetFile.name), 'wb') as f:
                f.write(assetEnv.file.save())
            return

    raise FileNotFoundError(
        'can not found asset file:\'{0}/Downloads/AssetBundle/{1}*.mtga\''.format(Config.WINDOWS_DATA_DIR, assetNamePrefix))


def patch_cardpart(patchContent: dict):
    for assetFile in MTGAAltRuleDir.iterdir():
        if assetFile.name.startswith('ALT_Card_'):
            ruleFileName = assetFile.name
            shutil.copy(assetFile, Config.BACKUP_DIR)

            with open(assetFile, 'r', encoding='UTF-8') as f:
                AltRules = json.load(f)

    for patchKey, patchValue in patchContent.items():
        if not AltRules.__contains__(patchKey):
            continue
        # patching
        for patchNode, patchList in patchValue.items():
            match patchNode:
                case "Nodes":
                    for patchRule in patchList:
                        AltRules[patchKey]['Nodes'].append(patchRule)
                case "Connections":
                    patchParentList = {}
                    for listId in range(0, len(patchList)):
                        patchParentList[patchList[listId]
                                        ['Parent']] = listId

                    # patch exist node
                    existNodeList = {}
                    for nodeId in range(0, len(AltRules[patchKey]["Connections"])):
                        patchId = patchParentList.get(
                            AltRules[patchKey]['Connections'][nodeId]['Parent'], -1)
                        if patchId == -1:
                            continue
                        existNodeList[patchId] = nodeId

                    missingNodeList = []
                    for nodeId in range(0, len(patchParentList)):
                        if not existNodeList.__contains__(nodeId):
                            missingNodeList.append(nodeId)

                    for patchId, nodeId in existNodeList.items():
                        patchRule = patchList[patchId]['Child']
                        if isinstance(patchRule, dict):
                            for k, v in patchRule.items():
                                AltRules[patchKey]['Connections'][nodeId]['Child'][k] = v
                        elif isinstance(patchRule, list):
                            for rule, pos in patchRule:
                                AltRules[patchKey]['Connections'][nodeId]['Child'].insert(
                                    pos, rule)
                        else:
                            raise NotImplementedError(
                                'unknown patch type:\'{0}\''.format(patchRule))

                    # patch don't exist node
                    for nodeId in missingNodeList:
                        AltRules[patchKey]['Connections'].append(
                            patchList[nodeId])
                case _:
                    raise NotImplementedError(
                        'unknown patch node:\'{0}\''.format(patchNode))

    with open('{0}/{1}'.format(Config.OUT_DIR, ruleFileName), 'w', encoding='UTF-8') as f:
        f.write(json.dumps(AltRules, ensure_ascii=False))


def patch_carddatabase(patch: dict):
    databaseDir = pathlib.Path(
        '{0}/Downloads/Raw'.format(Config.WINDOWS_DATA_DIR))
    if not databaseDir.is_dir():
        raise FileNotFoundError('can not found mtga card database dir')

    for dbAsset in databaseDir.iterdir():
        if dbAsset.name.startswith('Raw_cards_'):
            shutil.copy(dbAsset, Config.BACKUP_DIR)

            with open(dbAsset, 'r', encoding='UTF-8') as f:
                databaseContent = json.load(f)

            for setCode, setPatchs in patch.items():
                artArr = setPatchs.keys()
                for nodeId in range(0, len(databaseContent)):
                    if databaseContent[nodeId]['set'] == setCode and databaseContent[nodeId]['artId'] in artArr:
                        patchContents = setPatchs[databaseContent[nodeId]['artId']]
                        for k, v in patchContents.items():
                            databaseContent[nodeId][k] = v

            with open('{0}/{1}'.format(Config.OUT_DIR, dbAsset.name), 'w', encoding='UTF-8') as f:
                json.dump(databaseContent, f, ensure_ascii=False, indent=4)

            return

    raise FileNotFoundError(
        'can not found asset file:\'{0}/Data/Data_cards*.mtga\''.format(Config.WINDOWS_DATA_DIR))


if __name__ == "__main__":
    if not MTGAAssetDir.is_dir():
        raise FileNotFoundError('can not found mtga asset dir')
    if not Config.RESOUCE_DIR.is_dir():
        raise FileNotFoundError('can not found resource dir')
    if not Config.BACKUP_DIR.is_dir():
        Config.BACKUP_DIR.unlink(missing_ok=True)
        Config.BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    if not Config.OUT_DIR.is_dir():
        Config.OUT_DIR.unlink(missing_ok=True)
        Config.OUT_DIR.mkdir(parents=True, exist_ok=True)

    for assetType, patchDetail in PATCH_TARGET_LIST.items():
        match assetType:
            case AssetType.CardArt:
                for artId in patchDetail:
                    patch_art(artId)
            case AssetType.CardParts:
                patch_cardpart(patchDetail)
            case AssetType.CardDataBase:
                patch_carddatabase(patchDetail)
            case _:
                print('unsupport: \'{0}\':\'{1}\'\n'.format(
                    assetType, patchDetail))
