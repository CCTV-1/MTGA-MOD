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
			lock (ModManager.lockObj)
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

							if (ModManager.instance.config.userSkillLevel > UserSkillLevel.top)
							{
								ModManager.instance.config.userSkillLevel = UserSkillLevel.NONE;
							}
							if (ModManager.instance.config.draftDeckColor > DraftDeckColor.WUBRG)
							{
								ModManager.instance.config.draftDeckColor = DraftDeckColor.NONE;
							}

							if (ModManager.instance.config.userSkillLevel != UserSkillLevel.NONE)
							{
								ModManager.apiUri = string.Format("{0}&user_group={1}", new object[]
								{
									ModManager.apiUri,
									ModManager.instance.config.userSkillLevel.ToString("G")
								});
							}
							if (ModManager.instance.config.draftDeckColor != DraftDeckColor.NONE)
							{
								ModManager.apiUri = string.Format("{0}&colors={1}", new object[]
								{
									ModManager.apiUri,
									ModManager.instance.config.draftDeckColor.ToString("G")
								});
							}
						}
						catch (Exception)
						{
							ModManager.instance.config = new ModManager.ModConfig();
						}
					}
				}
			}
			return ModManager.instance;
		}
	}

	public Dictionary<string, ModManager.DraftInfo> getCardRankMap(string setCode, string draftType)
	{
		if (!this.config.displayIWDText)
		{
			return null;
		}
		if (!this.cardRankMap.TryGetValue(setCode + "_" + draftType, out Dictionary<string, ModManager.DraftInfo> eventCardRankMap))
		{
			bool exist = false;
			lock (ModManager.lockObj)
			{
				exist = this.fetchingTask.ContainsKey(setCode + "_" + draftType);
				if (!exist)
				{
					this.fetchingTask[setCode + "_" + draftType] = true;
					this.fetchCardRankInfo(setCode, draftType);
				}
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
			string responseBody = await this.client.GetStringAsync(requestUrl);
			responseBody = string.Format("{{ \"data\": {0}}}", responseBody);
			ModManager.CardInfoList rankList = JsonUtility.FromJson<ModManager.CardInfoList>(responseBody);
			if (rankList != null)
			{
				Dictionary<string, ModManager.DraftInfo> eventCardRankMap = new Dictionary<string, ModManager.DraftInfo>();
				foreach (ModManager.CardInfo cardInfo in rankList.data)
				{
					//discard untrusted data
					if ((cardInfo.ever_drawn_game_count >= this.config.maxUntrustedIWDDataAmount) || (cardInfo.never_drawn_game_count >= this.config.maxUntrustedIWDDataAmount))
					{
						double iwd = (cardInfo.ever_drawn_win_rate - cardInfo.never_drawn_win_rate) * 100.0;
						eventCardRankMap[cardInfo.name] = new ModManager.DraftInfo(iwd, cardInfo.avg_pick);
					}
				}
				this.cardRankMap[setCode + "_" + draftModeName] = eventCardRankMap;
			}
		}
		catch (HttpRequestException e)
		{
			Debug.LogWarning("fetch " + setCode + "_" + draftModeName + "card rank info failure.");
		}
		lock (ModManager.lockObj)
		{
			this.fetchingTask.Remove(setCode + "_" + draftModeName);
		}
	}

	public string getCardAvgPickInfo(string cardName)
	{
		string text = "";
		foreach (KeyValuePair<string, Dictionary<string, ModManager.DraftInfo>> keyValuePair in this.cardRankMap)
		{
			if (keyValuePair.Value != null && keyValuePair.Value.Count != 0)
			{
				ModManager.DraftInfo draftInfo;
				keyValuePair.Value.TryGetValue(cardName, out draftInfo);
				text = string.Concat(new string[]
				{
					text,
					"\n",
					keyValuePair.Key,
					"平均抓位：",
					draftInfo.ToString()
				});
			}
		}
		return text;
	}

	public TMP_FontAsset zhCNFont
	{
		get
		{
			if (this.modFont == null)
			{
				string fontFileName = this.config.fontName;
				AssetBundle assetBundle = AssetBundle.LoadFromFile(Application.dataPath + "/" + fontFileName);
				if (assetBundle == null)
				{
					this.modFont = TMP_Settings.defaultFontAsset;
					Debug.LogWarning(string.Format("{0}/{1} don't exist,use game default font:\"{2}\".", new object[]{
						Application.dataPath,
						fontFileName,
						this.modFont.name
					}));
				}
				else
				{
					this.modFont = assetBundle.LoadAsset<TMP_FontAsset>(fontFileName + " SDF");
				}
			}

			return this.modFont;
		}
	}

	public ModManager.ModConfig config;

	private static ModManager instance = null;
	private static readonly object lockObj = new object();
	private static string configFilePath = Application.dataPath + "/modconfig.json";
	private static string startDate = "2016-09-01";
	private static string endDate = DateTime.Now.ToString("yyyy-MM-dd");
	private static string apiUri = "https://www.17lands.com/card_ratings/data?expansion={0}&format={1}&start_date={2}&end_date={3}";

	private TMP_FontAsset modFont = null;
	// <eventName, <cardName, DraftInfo>>
	private Dictionary<string, Dictionary<string, ModManager.DraftInfo>> cardRankMap = new Dictionary<string, Dictionary<string, ModManager.DraftInfo>>();
	private Dictionary<string, bool> fetchingTask = new Dictionary<string, bool>();
	private HttpClient client = new HttpClient();

	public enum UserSkillLevel : uint
	{
		NONE = 0,
		bottom = 1,
		middle = 2,
		top = 3,
	}

	public enum DraftDeckColor : uint
	{
		NONE = 0,
		W,
		U,
		B,
		R,
		G,
		WU,
		WB,
		WR,
		WG,
		UB,
		UR,
		UG,
		BR,
		BG,
		RG,
		WUB,
		WUR,
		WUG,
		WBR,
		WBG,
		WRG,
		UBR,
		UBG,
		URG,
		BRG,
		WUBR,
		WUBG,
		WURG,
		WBRG,
		UBRG,
		WUBRG
	}

	public struct DraftInfo
	{
		public DraftInfo(double iwdValue, double pickValue)
		{
			this.iwd = iwdValue;
			this.avgPick = pickValue;
		}

		public double iwd;
		public double avgPick;
	}

	[Serializable]
	public class ModConfig
	{
		public string fontName = "sourcehansans-medium";

		public uint plainsId = 81179U;

		public uint islandId = 81180U;

		public uint swampId = 81181U;

		public uint mountainId = 81182U;

		public uint forestId = 81183U;

		public uint wasteId = 62531U;

		public string defaultFormatName = "Standard";

		public bool displayIWDText = true;

		public uint maxUntrustedIWDDataAmount = 200;

		public UserSkillLevel userSkillLevel = UserSkillLevel.NONE;

		public DraftDeckColor draftDeckColor = DraftDeckColor.NONE;

		public bool alwayExportEnglishDeck = false;

		public bool displayAbilityHangerExtraInfo = true;
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
