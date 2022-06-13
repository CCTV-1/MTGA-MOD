using System;
using System.IO;
using TMPro;
using UnityEngine;

public class ZhCN_Font
{
	private ZhCN_Font()
	{
	}

	public static ZhCN_Font Instance
	{
		get
		{
			object obj = ZhCN_Font.lockObj;
			lock (obj)
			{
				if (ZhCN_Font.instance == null)
				{
					ZhCN_Font.instance = new ZhCN_Font();
					string configFontName = ZhCN_Font.fontName;
					if (File.Exists(Application.dataPath + "/fontconfig.txt"))
					{
						configFontName = new StreamReader(Application.dataPath + "/fontconfig.txt").ReadLine();
					}
					if (ZhCN_Font.instance.zhCNFont == null)
					{
						AssetBundle assetBundle = AssetBundle.LoadFromFile(Application.dataPath + "/" + configFontName);
						if (assetBundle == null)
						{
							Debug.LogWarning(Application.dataPath + "/" + configFontName + " don't exist");
						}
						ZhCN_Font.instance.zhCNFont = assetBundle.LoadAsset<TMP_FontAsset>(configFontName + " SDF");
					}
				}
			}
			return ZhCN_Font.instance;
		}
	}

	static ZhCN_Font()
	{
		ZhCN_Font.lockObj = new object();
	}

	public TMP_FontAsset zhCNFont;

	private static ZhCN_Font instance = null;

	private static readonly object lockObj;

	private static string fontName = "sourcehansans-medium";
}
