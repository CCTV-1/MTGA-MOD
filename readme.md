# 一、让MTGA使用支持中文的字体

## 方案1：注入代码使游戏加载并使用自己制作的字体(以`MONO`构建的情况为例)
### 手动注入代码
1. 使用`dnSpy`给`Assembly-CSharp.dll`插入类[ModManager](./ModManager.cs)。
2. 在合适的位置修改各处TMP_Text对象(直接或间接使用)的`font`成员为`ModManager.Instance.zhCNFont`([当前修补的位置](./0001-mod-patch.patch))。若想精细控制具体区域使用什么字体，只需要向`ModManager`类添加`TMP_FontAsset`类型的成员并加载相关字体，然后在设置`font`成员的各处改为想设置的字体(`ModManager.Instance.TitleFont`、`ModManager.Instance.RuleTextFont`之类的)即可。
3. 使用与MTGA同样的Unity版本(`2021.3.14 f1`)制作字体。放于`ModManager`类要求的位置。

### 自动注入代码
1. 安装`.NET SDK`(当前的LTS版)，然后`cd`到`Assembly-CSharp.Mod.mm`文件夹。
2. `dotnet build`编译生成`Assembly-CSharp.Mod.mm.dll`。
3. 按[MonoMod](https://github.com/MonoMod/MonoMod)的说明生成修补后的`MONOMODDED_Assembly-CSharp.dll`备份原`Assembly-CSharp.dll`后将其改为`Assembly-CSharp.dll`即可。

PS: 对于使用了使用`IL2CPP`构建的平台，如果`BepInEx`、`MelonLoader`以及其他类似物可用，可以使用他们提供的API在运行时替换字体和修补代码以减少工作量。

## 方案2：通过修改资源文件将游戏已有的字体替换为自己制作的字体
1. 使用与MTGA同样的Unity版本(`2021.3.14 f1`)制作字体`msyh`(取个名字方便下文指代，不一定要是这个名字)。
2. 接下来以手动修改安卓端字体为例：于安卓安装包的`/assets/bin/Data/`(其他平台可能在其他路径或需安装好MTGA后在安装目录下查找)下找到`sharedassets0.assets`文件(有些平台会将`sharedassets0.assets`拆分，但是在使用`UABEA`编辑时`UABEA`会提示生成合并后的文件。操作好后用生成的`sharedassets0.assets`即可。无须再次拆分。)。
3. 使用`Cpp2IL.exe`、`Il2CppDumper`等工具之一生成虚拟`dll`用于支持`UABEA`反序列`MonoBehaviour`对象(使用了`IL2CPP`构建的情况下才需要进行这一步)。
4. 使用`UABEA`打开`sharedassets0.assets`，找到`Font_Default(MonoBehaviour)`和`Font_Default Atlas(Texture2D)`，将`Font_Default`给`Export Dump`。(之所以是Font_Default，是因为TMP_Setting记录的默认字体为Font_Default)
5. 使用`UABEA`打开制作的字体`msyh`，找到`msyh SDF(MonoBehaviour)`使用`Export Dump`导出。找到`msyh SDF Atlas(Texture2D)`使用`Plugins -> Export texture`导出。
6. 使用文本编辑器打开导出的两个`MonoBehaviour`文件，将`msyh SDF(MonoBehaviour)`中的`m_PathID`字段和`m_FileID`字段修改为`Font_Default(MonoBehaviour)`中对应字段的值，再修改`m_Name`为`"Font_Default"`，最后复制`Font_Default(MonoBehaviour)`中的`m_FallbackFontAssetTable`字段内容给`msyh SDF(MonoBehaviour)`。
7. 使用`UABEA`打开`sharedassets0.assets`，找到`Font_Default(MonoBehaviour)`和`Font_Default Atlas(Texture2D)`，选中`Font_Default(MonoBehaviour)`使用`Import Dump`将修改后的`msyh SDF(MonoBehaviour)`导入，再选中`Font_Default Atlas(Texture2D)`使用`Plugins -> Edit texture`导入`msyh SDF Atlas(Texture2D)`。最后保存为新的`sharedassets0.assets`。
8. 对所有存在于资源文件中的字体重复上述替换字体操作，可以达到字体样式统一的效果。但要注意，将过多的字体替换为中文字体会导致游戏运行时的内存占用变大很多，这在移动端会造成特别大的影响，最好只替换需要替换的，且制作的字体尽可能只包含需要的字形。在2022/4/28 PC客户端上，要做到基本一致需要替换的字体为:`Font_Default`、`Font_Default_JP`、`Font_Default_USERNAME`、`Font_Title`、`Font_Title_JP`、`Font_Title_USERNAME`，如果要完全一致(有很多字体只用于特殊样式牌张和特殊UI控件上)需要替换前述字体后再将除`Font_***_$(LangCode)`外的绝大多数字体都进行替换。PC端这些字体在`MTGA安装目录/MTGA_Data/resources.assets`内和`MTGA安装目录/MTGA_Data/Downloads/AssetBundle/`目录下都存在，各自应用于不同位置，所以都需要替换。而在安卓端这些字体分别位于apk、obb文件和运行后下载的资源文件中([PC端替换字体脚本(基本一致)](./FontPatcher.py))。
9. 将修改后的资源文件替换原文件(2022/4/28:目前mtga并没有对文件、签名做校验和加密，如果未来进行了校验/加密则需要先去除校验/进行解密，校验/加密手段、对象太多无法一一列举)。

PS: 在`IL2CPP`构建的ARM设备上使用此方案会比通过各种hook手段实现方案1要便捷的多，因为目前`BepInEx`、`MelonLoader`以及其他类似物在ARM设备上都不可用，不过可以使用`frida`，利用`frida-il2cpp-bridge`提供的封装实现（但这么做有相当大的运行时开销）。

# 二、 翻译文本
1. ~~翻译位于`"{0}/Downloads/Loc".format(Application.dataPath)`和`"{0}/Downloads/Data".format(Application.dataPath)`下的所有位于.mtga文件内的文本(实际上是json文件)，使用脚本合并已存在的翻译/导出未进行翻译的文本。~~ 2022/6/2更新后，文本被放置于`sqlite3`数据库文件和资源文件的`MonoBehavior`脚本中(位于`"{0}/Downloads/Raw/Raw_CardDatabase_***".format(Application.dataPath)`、`"{0}/Downloads/Raw/Raw_ClientLocalization_***".format(Application.dataPath)`，以及`"{0}/resources.assets".format(Application.dataPath)`中类别为`MonoBehavior`的`LocLibrary`)，无法再使用文本编辑器直接编辑，需要使用相关软件编辑或者使用[脚本](./UpdateCardTS.py)和[脚本](./UpdateUITS.py)导出成文本文件后进行翻译，再使用脚本导入回资源文件中。
2. 翻译注意事项：~~ `Wotc.Mtga.Cards.Text::AbilityTextData::ColorizeModalAbilityText`中有一行`text = "• " + text;`要求选择模式牌张的翻译不能使用`•增殖`必须留有空格`• 增殖`。~~(对应原文里不再保留`•`)。文本中被`{}`包围的文本需原样保留(可调整位置)。~~文本中的HTML标签(`<i>`等)也需原样保留(若不想要与英文样式一致，则HTML标签也可不保留)~~(2022/6/2更新后删除了所有牌张文本中的HTML标签)。被用于牌张类别栏的文本若包含有`(`和`)`不能改成`（`和`）`否则会被`GreClient.CardData::CardUtilities::FormatComplexTitle`和`GreClient.CardData::CardUtilities::FormatComplexTitleVertical`强制修改样式。

# 三、 其他功能补丁

1. ~~修改`NavBarController::RefreshVaultProgress`为以下所示，使暗窖一直显示~~(于2022/4/28客户端更新后,不再需要):
	```csharp
	public void RefreshVaultProgress(double pct)
	{
		this.UpdateVaultDisplay(pct);
		bool flag = this._onboardingState == NavBarController.OnboardingState.HiddenBar;
		if (pct >= 0.0 && !flag && WrapperController.Instance.NPEState.ActiveNPEGame == null)
		{
			this._vaultContainer.gameObject.SetActive(true);
			if (this._vaultAnimator.isActiveAndEnabled)
			{
				this._vaultAnimator.SetBool("Active", true);
				return;
			}
		}
		else
		{
			if (this._vaultAnimator.isActiveAndEnabled)
			{
				this._vaultAnimator.SetBool("Active", false);
			}
			this._vaultContainer.gameObject.SetActive(false);
		}
	}
	```

2. 修改 ~~`GreClient.Network::GREConnection::HandleMatchServiceMessage`和~~`MatchManager.PlayerInfo.ScreenName`使得对局中显示玩家的ID~~和隐藏分~~(2022/8/4更新后，服务器不再告知客户端对局内玩家的隐藏分)：
	```csharp
	private void HandleMatchServiceMessage(MatchServiceToClientMessage msg)
	{
		/*无关代码，省略*/
		MatchServiceToClientMessage.MessageOneofCase messageCase = msg.MessageCase;
		switch (messageCase)
		{
			/*无关代码，省略*/
			case MatchServiceToClientMessage.MessageOneofCase.MatchGameRoomStateChangedEvent:
			{
				foreach (MatchGameRoomPlayerInfo playerInfo in msg.MatchGameRoomStateChangedEvent.GameRoomInfo.GameRoomConfig.ReservedPlayers)
				{
					string userId = playerInfo.UserId;
					string playerName = playerInfo.PlayerName;
					string playerMMR = "0";
					if (msg.MatchGameRoomStateChangedEvent.GameRoomInfo.GameRoomConfig.ServiceMetadata.TryGetValue(userId + "_Rating", out playerMMR))
					{
						//保留整数
						//playerMMR = ((int)float.Parse(playerMMR)).ToString();
						MMRMap.Instance.cache[playerName] = playerMMR;
					}
				}
				break;
			}
			/*无关代码，省略*/
		}
		/*无关代码，省略*/
	}
	```

	然后将`MatchManager::PlayerInfo.ScreenName`修改为：
	```csharp
	public string ScreenName
	{
		get
		{
			if (MMRMap.Instance.cache.ContainsKey(_screenName))
			{
				return _screenName + "(" + MMRMap.Instance.cache[_screenName] + ")";
			}
			return _screenName;
		}
		set
		{
			_screenName = value;
		}
	}
	```

3. 修改`Wotc.Mtga.Wrapper.Draft.DraftContentController::SettingCards_OnComplete`为以下所示，使轮抓过程中始终显示玩家收藏情况：
	```csharp
	private void SettingCards_OnComplete()
	{
		this._settingCardsCoroutine = null;
		this._okToPickCard = true;
		this.UpdateCardCollectionInfo(true);
		base.StartCoroutine(this.Coroutine_StartTimer());
	}
	```

4. 在威世智修复音效bug之前，修改`AudioManager::LoadBnk`的以下部分，避免游戏频繁进行自检恢复被mod替换的文件(2022/9/1更新后似乎已经修复了)
	```csharp
	private static bool LoadBnk(string Bnkname)
	{
		/*无关代码，省略*/
		if (akresult != AKRESULT.AK_Success)
		{
			if (akresult != AKRESULT.AK_BankAlreadyLoaded)
			{
				MDNPlayerPrefs.HashAllFilesOnStartup = false;
				/*无关代码，省略*/
			}
			/*无关代码，省略*/
		}
		/*无关代码，省略*/
	}
	```

5. 修改`CardUtilities.IsCardCraftable`函数为总是返回`true`，解除某些单卡不可使用野卡合成的限制(有封号风险)。
	```csharp
	private void RefreshCraftMode()
	{
		/*无关代码，省略*/
		if (this._printingData.IsBasicLand)
		{
			list.Add(Languages.ActiveLocProvider.GetLocalizedText("SystemMessage/System_Invalid_Redemption_Text", Array.Empty<ValueTuple<string, string>>()));
		}
		else if (!CardUtilities.IsCardCraftable(this._printingData))
		{
			flag3 = true;
			list.Add(Languages.ActiveLocProvider.GetLocalizedText("SystemMessage/System_Invalid_Redemption_Text", Array.Empty<ValueTuple<string, string>>()));
		}
		else if (this._collectedQuantity < 4)
		{
			flag3 = true;
			flag4 = true;
			/*无关代码，省略*/
		}
		/*无关代码，省略*/
		this._craftButton.gameObject.SetActive(flag4);
		if (flag4)
		{
			this._craftButton.Interactable = flag5;
		}
		/*无关代码，省略*/
	}
	```

6. ~~修改`DeckBuilderWidget::SuggestLand`以支持设置默认基本地。~~(2023.2.28更新后客户端提供了此功能)
	```csharp
	private void SuggestLand()
	{
		List<CardList.CardPrintingQuantity> filteredMainDeck = _model.GetFilteredMainDeck();
		List<CardList.CardPrintingQuantity> filteredCommandZone = _model.GetFilteredCommandZone();
		IEnumerable<CardList.CardPrintingQuantity> cards;
		if (filteredCommandZone == null)
		{
			IEnumerable<CardList.CardPrintingQuantity> enumerable = filteredMainDeck;
			cards = enumerable;
		}
		else
		{
			cards = filteredMainDeck.Concat(filteredCommandZone);
		}

		Dictionary<ManaColor, uint> suggesContent = BasicLandSuggester.Calculate(cards, _context.Format);
		List<uint> list = new List<uint>();
		foreach (CardList.CardPrintingQuantity item2 in filteredMainDeck)
		{
			if (item2.Printing.IsBasicLandUnlimited || IsSuggestibleWaste(item2))
			{
				for (int j = 0; j < item2.Quantity; j++)
				{
					list.Add(item2.Printing.GrpId);
				}
			}
		}
		foreach (uint item3 in list)
		{
			_model.RemoveCardFromMainDeck(item3);
		}
		foreach (KeyValuePair<ManaColor, uint> suggestion in suggesContent)
		{
			ManaColor suggestionColor = suggestion.Key;
			CardPrintingData cardPrintingData = null;
			uint defaultLandId = 0;
			switch (suggestionColor)
			{
				case ManaColor.ManaColor_White:
				{
					defaultLandId = ModManager.Instance.config.plainsId;
					break;
				}
				case ManaColor.ManaColor_Blue:
				{
					defaultLandId = ModManager.Instance.config.islandId;
					break;
				}
				case ManaColor.ManaColor_Black:
				{
					defaultLandId = ModManager.Instance.config.swampId;
					break;
				}
				case ManaColor.ManaColor_Red:
				{
					defaultLandId = ModManager.Instance.config.mountainId;
					break;
				}
				case ManaColor.ManaColor_Green:
				{
					defaultLandId = ModManager.Instance.config.forestId;
					break;
				}
				case ManaColor.ManaColor_None:
				default:
				{
					if (this._context.IsConstructed)
					{
						defaultLandId = ModManager.Instance.config.wasteId;
					}
					else
					{
						defaultLandId = ModManager.Instance.config.plainsId;
					}
					break;
				}
			}
			//if player not own seleced land,failback to use he last obtained land.
			if (!_inventoryManager.Cards.TryGetValue(defaultLandId, out var cardQuantity) || (cardQuantity <= 0))
			{
				cardPrintingData = _cardDatabase.DatabaseUtilities.GetPrimaryPrintings().LastOrDefault((CardPrintingData kvp) => kvp.IsBasicLandUnlimited && kvp.ColorIdentity.FirstOrDefault().ToManaColor() == suggestion.Key && _inventoryManager.Cards.TryGetValue(kvp.GrpId, out var cardQuantity) && cardQuantity > 0);

				if (cardPrintingData == null && suggestion.Key == ManaColor.ManaColor_None)
				{
					if (_context.IsConstructed)
					{
						cardPrintingData = _cardDatabase.DatabaseUtilities.GetPrimaryPrintings().LastOrDefault((CardPrintingData kvp) => kvp.IsBasicLand && kvp.ColorIdentity.FirstOrDefault().ToManaColor() == ManaColor.ManaColor_None && _inventoryManager.Cards.TryGetValue(kvp.GrpId, out var value4) && value4 > 0);
					}
					if (cardPrintingData == null)
					{
						cardPrintingData = _cardDatabase.DatabaseUtilities.GetPrimaryPrintings().LastOrDefault((CardPrintingData kvp) => kvp.IsBasicLandUnlimited && kvp.ColorIdentity.FirstOrDefault().ToManaColor() == ManaColor.ManaColor_White && _inventoryManager.Cards.TryGetValue(kvp.GrpId, out var value3) && value3 > 0);
					}
				}
				if (cardPrintingData == null)
				{
					continue;
				}
				defaultLandId = cardPrintingData.GrpId;
			}
			for (int k = 0; k < suggestion.Value; k++)
			{
				_model.AddCardToMainDeck(defaultLandId);
			}
		}
		_model.UpdateMainDeck();
		_companionUtil.UpdateValidation(_model, _context?.Format);
		WrapperDeckBuilder.CacheDeck(_model, _context);

		bool IsSuggestibleWaste(CardList.CardPrintingQuantity card)
		{
			if (_context.IsConstructed && card.Printing.IsBasicLand)
			{
				return card.Printing.ColorIdentity.Count == 0;
			}
			return false;
		}
	}
	```

7. 修改`WrapperDeckBuilder::OnNewDeck`和`DeckManagerController::OnCreateDeck`以支持指定套牌的默认赛制。
   ```csharp
	public void OnNewDeck()
	{
		if (!_decksManager.ShowDeckLimitError())
		{
			//GetDefaultFormat() ==> GetSafeFormat(ModManager.Instance.config.defaultFormat)
			DeckBuilderContext context = new DeckBuilderContext(DeckServiceWrapperHelpers.ToAzureModel(_formatManager.GetSafeFormat(ModManager.Instance.config.defaultFormat).NewDeck(_decksManager)), null, sideboarding: false, firstEdit: true, DeckBuilderMode.DeckBuilding, ambiguousFormat: true);
			SceneLoader.GetSceneLoader().GoToDeckBuilder(context, reloadIfAlreadyLoaded: true);
			AudioManager.PlayAudio(WwiseEvents.sfx_ui_generic_click, base.gameObject);
		}
	}

	private void OnCreateDeck()
	{
		if (!_decksManager.ShowDeckLimitError())
		{
			string createsFormat = _deckBuckets[_selectedBucket].CreatesFormat;
			if (_selectedBucket == 0)
			{
				createsFormat = ModManager.Instance.config.defaultFormat;
			}
			Client_Deck deck = _formatManager.GetSafeFormat(createsFormat).NewDeck(_decksManager);
			New_GoToDeckBuilder(deck, FormatUtilities.IsAmbiguous(createsFormat));
		}
	}
   ```

8. 给`Meta_CDC`添加`ShowCardRankInfo`函数并修改`Wotc.Mtga.Wrapper.Draft.DraftContentController::UpdateCardCollectionInfo`和`Wotc.Mtga.Wrapper.Draft::HumanDraftPod`的构造函数为如下所示，显示从`17Lands`获取的牌张`IWD`信息。
	```csharp
	public virtual void ShowCardRankInfo(bool active, string IWDInfo = "???")
	{
		_collectionAnchor.UpdateActive(active);
		if (active)
		{
			_collectionCheckMark.UpdateActive(active: false);
			_collectionText.transform.parent.gameObject.UpdateActive(active: true);
			this._collectionText.SetText(IWDInfo, true);
		}
	}


	public HumanDraftPod(IEventsServiceWrapper eventsServiceWrapper, WGS.Logging.ILogger logger, BILogger biLogger, string eventId, string draftId = null)
	{
		this._eventsServiceWrapper = eventsServiceWrapper;
		this._logger = logger;
		this._biLogger = biLogger;
		eventsServiceWrapper.AddDraftNotificationCallback(new Action<DraftNotification>(this.OnMsg_DraftNotification));
		this._eventId = eventId;
		//BotDraftPod::SetDraftState会设置InternalEventName而HumanDraftPod并不设置，所以要额外添加此行为
		this.InternalEventName = eventId;
		this.DraftState = DraftState.Podmaking;
		this.DraftId = draftId;
	}

	private void UpdateCardCollectionInfo(bool show)
	{
		_showCollectionInfo = show;
		if (!show)
		{
			foreach (DraftPackCardView cardView in _draftPackHolder.GetAllCardViews())
			{
				_inventoryManager.Cards.TryGetValue(cardView.Card.GrpId, out var value);
				value += _deck.MainDeckIds.Count((uint id) => id == cardView.Card.GrpId);
				value += _deck.SideboardIds.Count((uint id) => id == cardView.Card.GrpId);
				int maxCollected = (int)cardView.Card.Printing.MaxCollected;
				cardView.CardView.ShowCollectionInfo(active: true, Math.Min(value, maxCollected), maxCollected);
			}
			return ;
		}

		if (this._draftPod.InternalEventName == null)
		{
			return;
		}
		//QuickDraft_DMU_20221014
		string[] draftInfo = this._draftPod.InternalEventName.Split('_');
		Dictionary<string, ModManager.DraftInfo> rankInfo = ModManager.Instance.getCardRankMap(draftInfo[1], draftInfo[0]);
		if (rankInfo == null)
		{
			return;
		}

		foreach (DraftPackCardView cardView in _draftPackHolder.GetAllCardViews())
		{
			string cardName = this._cardDatabase.CardTitleProvider.GetCardTitle(cardView.Card.GrpId, true, "en-US");
			string iwdString = "???";
			if (rankInfo.TryGetValue(cardName, out var draftInfo))
			{
				double iwd = draftInfo.iwd;
				if (iwd <= 0.0)
				{
					iwdString = "<color=\"red\"><size=90%>" + iwd.ToString("F1");
				}
				else
				{
					iwdString = "<color=\"green\"><size=90%>" + iwd.ToString("F1");
				}
			}
			cardView.CardView.ShowCardRankInfo(active: true, iwdString);
		}
	}
	```

9. 修改`WrapperDeckUtilities::GetPrintingsByLocalizedTitle`使游戏无论在什么语言环境下都支持导入英文牌表。
    ```csharp
	private static IReadOnlyList<CardPrintingData> GetPrintingsByLocalizedTitle(CardDatabase cardDatabase, string title)
	{
		//先检查是不是英文牌名
		IReadOnlyList<CardPrintingData> printingsByLocalizedTitle = cardDatabase.DatabaseUtilities.GetPrintingsByEnglishTitle(title);
		if (printingsByLocalizedTitle == null || printingsByLocalizedTitle.Count == 0)
		{
			//不是英文牌名再检查是不是本地语言环境下的牌名
			printingsByLocalizedTitle = cardDatabase.DatabaseUtilities.GetPrintingsByLocalizedTitle(title);
		}
		if (printingsByLocalizedTitle != null)
		{
			CardPrintingData cardPrintingData = printingsByLocalizedTitle.FirstOrDefault((CardPrintingData c) => !c.IsPrimaryCard && c.DefunctRebalancedCardLink != 0U && cardDatabase.CardDataProvider.GetCardPrintingById(c.DefunctRebalancedCardLink, null).IsPrimaryCard);
			if (cardPrintingData != null)
			{
				CardPrintingData cardPrintingById = cardDatabase.CardDataProvider.GetCardPrintingById(cardPrintingData.DefunctRebalancedCardLink, null);
				return cardDatabase.DatabaseUtilities.GetPrintingsByTitleId(cardPrintingById.TitleId);
			}
		}
		return printingsByLocalizedTitle;
	}
	```

10. 修改`WrapperDeckUtilities::ToExportString_BySection`、`WrapperDeckUtilities::GetMainLabel`、`WrapperDeckUtilities::GetSideboardLabel`、`WrapperDeckUtilities::GetCommanderLabel`、`WrapperDeckUtilities::GetCompanionLabel`以支持指定游戏无论在什么语言环境下都支持导出英文牌表。
	```csharp
	//GetSideboardLabel GetCommanderLabel GetCompanionLabel都是一样的修改
	private static string GetMainLabel(IClientLocProvider localizationManager)
	{
		if (ModManager.Instance.config.alwayExportEnglishDeck)
		{
			return localizationManager.GetLocalizedTextForLanguage("MainNav/DeckBuilder/Sideboard_Label", "en-US", Array.Empty<ValueTuple<string, string>>());
		}
		return localizationManager.GetLocalizedText("MainNav/DeckBuilder/Deck_Label", Array.Empty<ValueTuple<string, string>>());
	}

	private static void ToExportString_BySection(StringBuilder builder, List<CardInDeck> cardCollection, ICardDatabaseAdapter db)
	{
		string overrideLangCode = null;
		if (ModManager.Instance.config.alwayExportEnglishDeck)
		{
			overrideLangCode = "en-US";
		}
		foreach (CardInDeck item in cardCollection)
		{
			CardPrintingData cardPrintingById = db.CardDataProvider.GetCardPrintingById(item.Id);
			builder.AppendLine(string.Format("{0} {1} ({2}) {3}", item.Quantity, (Languages.CurrentLanguage == "ja-JP") ? RemoveFurigana(db.GreLocProvider.GetLocalizedText(cardPrintingById.TitleId, overrideLangCode, formatted: false)) : db.GreLocProvider.GetLocalizedText(cardPrintingById.TitleId, overrideLangCode, formatted: false), cardPrintingById.ExpansionCode, cardPrintingById.CollectorNumber));
		}
	}
	```

11. 对牌张数据库执行`UPDATE Cards SET AdditionalFrameDetails  = '' WHERE ExpansionCode = "BRR";`以和谐兄弟之战神器秘典牌的过于难看的老框。

12. 修改`AbilityHangerBase::AddHangersInternal`以显示一些额外信息：
    ```csharp
	public void Init(ICardDatabaseAdapter cardDatabase, AssetLookupSystem assetLookupSystem, IUnityObjectPool unityObjectPool, IObjectPool genericObjectPool, IFaceInfoGenerator faceInfoGenerator, IClientLocProvider locManager, DeckFormat currentEventFormat)
	{
		//插入的私有对象
		this.rarityNameMap = new Dictionary<CardRarity, string>
		{
			{
				CardRarity.None,
				"无"
			},
			{
				CardRarity.Land,
				"地"
			},
			{
				CardRarity.Common,
				this._locManager.GetLocalizedText("Enum/Rarity/Common", Array.Empty<ValueTuple<string, string>>())
			},
			{
				CardRarity.Uncommon,
				this._locManager.GetLocalizedText("Enum/Rarity/Uncommon", Array.Empty<ValueTuple<string, string>>())
			},
			{
				CardRarity.Rare,
				this._locManager.GetLocalizedText("Enum/Rarity/Rare", Array.Empty<ValueTuple<string, string>>())
			},
			{
				CardRarity.MythicRare,
				this._locManager.GetLocalizedText("Enum/Rarity/MythicRare", Array.Empty<ValueTuple<string, string>>())
			}
		};
		/*无关的原始代码*/
	}

	protected virtual void AddHangersInternal(BASE_CDC cardView, ICardDataAdapter sourceModel, HangerSituation situation)
	{
		ICardDataAdapter model = cardView.Model;
		//插入下面这几行
		if (ModManager.Instance.config.displayAbilityHangerExtraInfo)
		{
			string body = string.Format("系列代码：{0}\n稀有度：{1}\n内部编号：{2}{3}", new object[]
			{
				model.ExpansionCode,
				this.rarityNameMap[model.Rarity],
				model.GrpId,
				ModManager.Instance.getCardAvgPickInfo(this._cardDatabase.CardTitleProvider.GetCardTitle(model.GrpId, true, "en-US"))
			});
			this._view.CreateHangerItem("Mod额外信息", false, body, false, "", false, null, 0, false, false, false);
		}
		/*无关代码*/
	}
	```

13. 修改`FrontDoorConnectionAWS`的`DefaultRpcTimeoutMs`变量的值为`15000`(原为`2000ms`)，以使与AWS服务器连接延迟很高的地方能进游戏。

14. 禁止安卓端请求Google Play更新数据：使用`Il2CppDumper`或类似工具将符号恢复到`IDA Pro`中。搜索函数`Wizards_Mtga_Platforms_PlatformContext__GetInstallationController`，使函数无条件跳转至构造返回`Wizards.Mtga.Installation.NoSupportInstallationController`而不是构造返回`Wizards.Mtga.Platforms.Android.AndroidInstallationController`。例如将下面的`B.NE loc_1438FAC`改为`B loc_1438FAC`。
	```ASM
	STR             X19, [SP,#-0x20]!
	STP             X29, X30, [SP,#0x10]
	ADD             X29, SP, #0x10
	ADRP            X19, #byte_47ACD8E@PAGE
	LDRB            W8, [X19,#byte_47ACD8E@PAGEOFF]
	TBNZ            W8, #0, loc_1438F7C
	ADRP            X0, #off_44683B8@PAGE
	LDR             X0, [X0,#off_44683B8@PAGEOFF]
	BL              sub_EDCF2C
	ADRP            X0, #off_44A3A68@PAGE
	LDR             X0, [X0,#off_44A3A68@PAGEOFF]
	BL              sub_EDCF2C
	MOV             W8, #1
	STRB            W8, [X19,#byte_47ACD8E@PAGEOFF]
	MOV             X0, XZR                 ; 0x1438F7C
	BL              UnityEngine.Application$$get_platform
	CMP             W0, #0xB
	B.NE            loc_1438FAC
	ADRP            X8, #off_44683B8@PAGE
	LDR             X8, [X8,#off_44683B8@PAGEOFF]
	LDR             X0, [X8]                ; Wizards.Mtga.Platforms.Android.AndroidInstallationController_TypeInfo
	BL              sub_EDCFFC
	MOV             X1, XZR                 ; method
	MOV             X19, X0
	BL              Wizards.Mtga.Platforms.Android.AndroidInstallationController$$.ctor
	B               loc_1438FC8
	ADRP            X8, #off_44A3A68@PAGE ; loc_1438FAC
	LDR             X8, [X8,#off_44A3A68@PAGEOFF]
	LDR             X0, [X8]                ; Wizards.Mtga.Installation.NoSupportInstallationController_TypeInfo
	BL              sub_EDCFFC
	MOV             X1, XZR                 ; method
	MOV             X19, X0
	BL              Wizards.Mtga.Installation.NoSupportInstallationController$$.ctor
	LDP             X29, X30, [SP,#0x10+0] ; 0x1438FC8
	MOV             X0, X19
	LDR             X19, [SP+0x10+-0x10],#0x20
	RET
	```

15. 安卓端禁用商店以支持无GooglePlay设备进入游戏：使用`Il2CppDumper`或类似工具将符号恢复到`IDA Pro`中。搜索函数`StoreManager$$RefreshStoreDataYield`(不同工具生成的名称会略有不同)。通过`CODE XREF`找到`WrapperController::Coroutine_StartupSequence::MoveNext`函数中对`StoreManager$$RefreshStoreDataYield`的调用并将其`NOP`。例如在`2022/4/28`更新的客户端中：`0x172B564` `BL StoreManager$$RefreshStoreDataYield`(19 3F F8 97) => `NOP`(1F 20 03 D5)


16. 安卓端强制启用图像设置：与15类似，搜索函数`SettingsMenu::Open`。将`settingsPanel.Hide`检测无效即可(也可以想办法调用`QualitySettingsUtil::ApplyVSync`)。
	```csharp
		public void Open(bool allowLogout, bool allowExit, bool allowGameConcession, bool allowMatchConcession, bool allowSkipTutorial, bool allowSkipOnboarding, bool allowDebug)
		{
			_canvasGroup.alpha = 1f;
			_canvasGroup.interactable = true;
			_canvasGroup.blocksRaycasts = true;
			base.gameObject.UpdateActive(active: true);
			foreach (SettingsPanel settingsPanel in _settingsPanels)
			{
				bool flag = !settingsPanel.DebugOnly || allowDebug;
				if (settingsPanel.Hide)
				{
					flag = false;
				}
				settingsPanel.Button.gameObject.SetActive(flag);
				bool activeSelf = settingsPanel.Panel.gameObject.activeSelf;
				if (!flag && activeSelf)
				{
					settingsPanel.Panel.HidePanel();
					settingsPanel.Panel.gameObject.SetActive(value: false);
				}
			}
			LogoutButton.SetActive(allowLogout);
			ExitGameButton.SetActive(allowExit);
			_allowMatchConcession = allowMatchConcession;
			ConcedeButton.SetActive(allowGameConcession || allowMatchConcession);
			SkipTutorialButton.SetActive(value: false);
			ExperimentalSkipTutorialButton.SetActive(allowSkipTutorial);
			SkipOnboardingButton.SetActive(allowSkipOnboarding);
			if (PlatformUtils.IsHandheld())
			{
				DetailedLoggingToggle.gameObject.SetActive(allowDebug);
			}
			GoToMainMenu();
			IsOpen = true;
		}
	```

# 四、 自动生成牌张样式MOD

参见[脚本](./ArtModGen.py)(编写教程时客户端已去除了常规启动时对资源文件的`crc`校验,所以无需另外禁用校验。)
