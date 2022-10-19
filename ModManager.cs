using System;
using System.IO;
using System.Text;
using TMPro;
using UnityEngine;

public class ModManager
{
	private ModManager()
	{
	}

	public static ModManager Instance
	{
		get
		{
			object obj = ModManager.lockObj;
			lock (obj)
			{
				if (ModManager.instance == null)
				{
					ModManager.instance = new ModManager();
					if (ModManager.instance.config == null)
					{
						try
						{
							string configContent = File.ReadAllText(ModManager.configFilePath, Encoding.UTF8);
							ModManager.instance.config = JsonUtility.FromJson<ModManager.ModConfig>(configContent);
						}
						catch (Exception)
						{
							ModManager.instance.config = new ModManager.ModConfig();
						}
					}
					if (ModManager.instance.zhCNFont == null)
					{
						string fontFileName = ModManager.instance.config.fontName;
						AssetBundle assetBundle = AssetBundle.LoadFromFile(Application.dataPath + "/" + fontFileName);
						if (assetBundle == null)
						{
							Debug.LogWarning(Application.dataPath + "/" + fontFileName + " don't exist");
						}
						ModManager.instance.zhCNFont = assetBundle.LoadAsset<TMP_FontAsset>(fontFileName + " SDF");
					}
				}
			}
			return ModManager.instance;
		}
	}

	public TMP_FontAsset zhCNFont;

	private static ModManager instance = null;

	private static readonly object lockObj = new object();

	private static string configFilePath = Application.dataPath + "/modconfig.json";

	public ModManager.ModConfig config;

	[Serializable]
	public class ModConfig
	{
		public string fontName = "sourcehansans-medium";

		public uint plainsId = 81179U;

		public uint islandId = 81180U;

		public uint swampId = 81181U;

		public uint mountainId = 81182U;

		public uint forestId = 81183U;

		public string defaultFormatName = "Standard";
	}
}
