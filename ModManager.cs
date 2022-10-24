using System;
using System.Collections.Generic;
using System.IO;
using System.Net.Http;
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

	public Dictionary<string, double> getCardRankMap(string setCode, string draftType)
	{
		if (!ModManager.cardRankMap.TryGetValue(setCode + "_" + draftType, out Dictionary<string, double> eventCardRankMap))
		{
			bool exist = false;
			lock (ModManager.lockObj)
			{
				exist = ModManager.fetchingTask.ContainsKey(setCode + "_" + draftType)
			}
			if (!exist)
			{
				lock (ModManager.lockObj)
				{
					ModManager.fetchingTask[setCode + "_" + draftType] = true;
				}
				ModManager.instance.fetchCardRankInfo(setCode, draftType);
			}
			return null;
		}
		return eventCardRankMap;
	}

	public async void fetchCardRankInfo(string setCode, string draftModeName)
	{
		string requestUrl = string.Format(ModManager.apiUri, new object[]
		{
			setCode,
			draftModeName,
			ModManager.startDate,
			ModManager.endDate
		});
		try
		{
			string responseBody = await ModManager.client.GetStringAsync(requestUrl);
			responseBody = string.Format("{{ \"data\": {0}}}", responseBody);
			ModManager.CardInfoList rankList = JsonUtility.FromJson<ModManager.CardInfoList>(responseBody);
			if (rankList != null)
			{
				Dictionary<string, double> eventCardRankMap = new Dictionary<string, double>();
				foreach (ModManager.CardInfo cardInfo in rankList.data)
				{
					if ((cardInfo.ever_drawn_game_count < 200) || (cardInfo.never_drawn_game_count < 200))
					{
						//discard invalid data
						continue;
					}
					double iwd = (cardInfo.ever_drawn_win_rate - cardInfo.never_drawn_win_rate) * 100.0;
					eventCardRankMap[cardInfo.name] = iwd;
				}
				ModManager.cardRankMap[setCode + "_" + draftModeName] = eventCardRankMap;
			}
		}
		catch (HttpRequestException e)
		{
			Debug.LogWarning("fetch " + setCode + "_" + draftModeName + "card rank info failure.");
		}
		lock (ModManager.lockObj)
		{
			ModManager.fetchingTask.Remove(setCode + "_" + draftModeName);
		}
	}

	public TMP_FontAsset zhCNFont;

	private static ModManager instance = null;

	private static readonly object lockObj = new object();

	private static string configFilePath = Application.dataPath + "/modconfig.json";

	public ModManager.ModConfig config;

	// <eventName, <cardName, cardIWD>>
	private static Dictionary<string, Dictionary<string, double>> cardRankMap = new Dictionary<string, Dictionary<string, double>>();
	private static Dictionary<string, bool> fetchingTask = new Dictionary<string, bool>();

	private static string startDate = "2016-09-01";

	private static string endDate = DateTime.Now.ToString("yyyy-MM-dd");

	private static string apiUri = "https://www.17lands.com/card_ratings/data?expansion={0}&format={1}&start_date={2}&end_date={3}";

	private static readonly HttpClient client = new HttpClient();

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

	[Serializable]
	private class CardInfo
	{
		public int seen_count;

		public int pick_count;

		public int game_count;

		public int sideboard_game_count;

		public int opening_hand_game_count;

		public int drawn_game_count;

		public int ever_drawn_game_count;

		public int never_drawn_game_count;

		public string name;

		public string color;

		public string rarity;

		public string url;

		public string url_back;

		public double avg_seen;

		public double avg_pick;

		public double win_rate;

		public double sideboard_win_rate;

		public double opening_hand_win_rate;

		public double drawn_win_rate;

		public double ever_drawn_win_rate;

		public double never_drawn_win_rate;

		public double drawn_improvement_win_rate;
	}

	[Serializable]
	private class CardInfoList
	{
		public List<ModManager.CardInfo> data;
	}
}
