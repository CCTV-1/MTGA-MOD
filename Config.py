import pathlib

GAME_UNITY_VERSION_STRING: str = "6000.3.14f1"
GAME_DLL_DIR = pathlib.Path(
    'C:/Program Files/Unity 6000.3.14f1/Editor/Data/Managed/UnityEngine/')
WINDOWS_DATA_DIR = pathlib.Path(
    'C:/Program Files/Wizards of the Coast/MTGA/MTGA_Data')
MACOS_RES_DIR = pathlib.Path('/Users/Shared/Epic Games/MagicTheGathering/MTGA.app/Contents/Resources/Data')
MACOS_DATA_DIR = pathlib.Path('~/Library/Application Support/com.wizards.mtga')
ANDROID_DATA_DIR = pathlib.Path('D:/Download/com.wizards.mtga/assets/bin/Data')
RESOUCE_DIR = pathlib.Path('./resource')
BACKUP_DIR = pathlib.Path('./backup')
OUT_DIR = pathlib.Path('./output')
