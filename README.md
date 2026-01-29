# Desktop Helper - 桌面動漫角色 LLM 助手

基於OpenSpec加速開發 & 可追朔之專案架構，
一個在 Windows 桌面上顯示動漫角色形象的 LLM 助手應用程式。

## 功能特性

- 🎭 透明背景的桌面角色顯示
- 🎨 Live2D 動畫角色支持（Cubism 3.0+）
- 👥 多角色素材庫管理（支援多個 Live2D 角色切換）
- 🔄 角色切換功能（單一視窗內切換不同角色）
- 👆 角色部位點擊互動（點擊不同部位觸發動畫與回應）
- 💬 LLM 對話功能（Gemini API，支援串流回應）
- ⏎ 發送/停止按鈕（串流期間可隨時停止生成）
- 💭 對話泡泡框顯示回應（支援滾動查看長內容）
- 🎤 語音輸入按鈕（UI 準備完成，STT 整合待後續）

## Demo 影片

<video src="sample/20260129_103316.mp4" controls width="800"></video>

*示範功能：角色顯示、角色切換、部位點擊互動、LLM 串流對話*

## 環境要求

- Python 3.8+
- Windows 10/11
- PyQt6
- Live2D 角色模型文件

## 安裝步驟

1. 克隆或下載專案到本地

2. 安裝依賴：
```bash
pip install -r requirements.txt
```

3. 配置 Gemini API Key：
   ```bash
   # 複製範例配置文件
   copy .env.example .env
   
   # 編輯 .env 文件，填入您的 Gemini API Key
   # GEMINI_API_KEY=your_api_key_here
   ```
   獲取 API Key: https://makersuite.google.com/app/apikey

4. 準備角色模型文件：
   - 將 Live2D 角色模型放置在專案根目錄下
   - 目前支援的角色資料夾：
     - `mao_pro_en/` - Mao 角色（英文版）
     - `hiyori_pro_zh/` - Hiyori 角色（繁中版）
     - `miku_pro_jp/` - Miku 角色（日文版）
   - 系統會自動掃描可用角色，若某個角色不存在會自動略過
   - 預設會優先載入 Mao 角色，若不存在則載入第一個可用角色

## 使用方法

執行主程式：
```bash
python main.py
```

執行後，您應該會看到一個透明背景的視窗出現在桌面上，Live2D 角色會自動載入並顯示。

### 對話功能使用

1. **文本輸入**：在視窗底部的輸入框中輸入訊息，按 Enter 或點擊發送按鈕（⏎）發送
2. **串流回應**：LLM 回應會以串流方式逐步顯示在對話泡泡框中，可即時看到生成過程
3. **停止生成**：串流期間，發送按鈕會變成停止按鈕（■），點擊可立即停止生成
4. **查看長回應**：若回應內容較長，可使用滑鼠滾輪在泡泡框內滾動查看完整內容
5. **語音輸入**：點擊麥克風按鈕（目前為 UI 準備，STT 功能待後續整合）

### 角色互動

1. **角色切換**：若有多個角色，輸入框左側會顯示角色切換按鈕，點擊可輪流切換角色
2. **部位點擊**：點擊角色的不同部位（頭、身體、手、腳等）會觸發對應的動作動畫與回應
3. **互動鎖定**：LLM 回應生成期間會暫時鎖定角色點擊互動，避免刷掉回應內容

### 操作說明

- **拖動視窗**：按住滑鼠左鍵拖動視窗到任意位置
- **視窗置頂**：視窗會自動保持在最上層
- **滾動查看**：在對話泡泡框上使用滑鼠滾輪可查看長內容

## 專案結構

```
Desktop_helper/
├── main.py                 # 主程式入口
├── requirements.txt        # Python 依賴
├── .env.example           # 環境變數範例
├── .gitignore             # Git 忽略文件
├── src/                    # 源代碼目錄
│   ├── desktop_window.py   # 桌面視窗模組
│   ├── live2d_widget.py   # Live2D 渲染引擎
│   ├── character_loader.py # 角色載入模組
│   ├── character_library.py # 角色素材庫管理
│   ├── character_interaction.py # 角色互動邏輯
│   ├── llm_client.py       # Gemini API 客戶端（支援串流）
│   └── chat_bubble.py      # 對話泡泡框組件（支援滾動）
├── mao_pro_en/            # Live2D 角色資源（Mao）
├── hiyori_pro_zh/         # Live2D 角色資源（Hiyori）
├── miku_pro_jp/           # Live2D 角色資源（Miku）
└── openspec/              # OpenSpec 規範文檔
```

## 開發狀態

### 已完成
- ✅ 透明背景桌面視窗
- ✅ 視窗拖動功能
- ✅ 視窗置頂功能
- ✅ 角色模型配置載入
- ✅ Live2D 角色渲染整合
- ✅ OpenGL 渲染引擎
- ✅ 多角色素材庫管理
- ✅ 角色切換功能（單一視窗內切換）
- ✅ 角色部位點擊互動（頭、身體、手、腳等）
- ✅ LLM 對話功能（Gemini API）
- ✅ LLM 串流回應（逐步顯示生成過程）
- ✅ 發送/停止按鈕（可隨時停止生成）
- ✅ 文本輸入框 UI
- ✅ 語音輸入按鈕 UI（準備完成）
- ✅ 對話泡泡框顯示（支援滾動查看長內容）

### 規劃中
- ⏳ 語音識別（Gemini STT API 整合）
- ⏳ 語音合成（TTS）
- ⏳ 角色動畫控制（根據對話內容觸發動畫）
- ⏳ 對話歷史保存
- ⏳ 角色自訂互動回應配置

## 技術堆疊

- **Python** - 主要開發語言
- **PyQt6** - 桌面應用程式框架
- **live2d-py** - Live2D Python 綁定庫
- **OpenGL** - 圖形渲染引擎
- **google-generativeai** - Gemini API Python SDK
- **python-dotenv** - 環境變數管理
- **numpy** - 數值計算支持

## 注意事項

### Live2D SDK 要求

`live2d-py` 需要 Live2D Cubism SDK 的 Core 模組。如果遇到載入錯誤，請：

1. 前往 [Live2D 官網](https://www.live2d.com/en/sdk/download/native/) 下載 Cubism SDK
2. 將 SDK 的 Core 模組放置在適當位置
3. 參考 `live2d-py` 的 [安裝文檔](https://github.com/EasyLive2D/live2d-py/wiki/%E5%AE%89%E8%A3%85) 進行配置

### 模型格式支持

- ✅ Cubism 3.0+ (.moc3, .model3.json)
- ✅ Cubism 2.1 (.moc, .model.json)

## 授權

請參考專案中的授權文件。

## 貢獻

歡迎提交 Issue 和 Pull Request！
