# Desktop Helper - 桌面動漫角色 LLM 助手

基於OpenSpec加速開發 & 可追朔之專案架構，
一個在 Windows 桌面上顯示動漫角色形象的 LLM 助手應用程式。

## 功能特性

- 🎭 透明背景的桌面角色顯示
- 🎨 Live2D 動畫角色支持
- 💬 LLM 對話功能（Gemini API）
- 🎤 語音輸入按鈕（UI 準備完成，STT 整合待後續）
- 💭 對話泡泡框顯示回應

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

4. 確保角色模型文件位於專案目錄中：
   - 預設路徑：`mao_pro_en/mao_pro_en/runtime/mao_pro.model3.json`
   - 或修改 `main.py` 中的路徑配置

## 使用方法

執行主程式：
```bash
python main.py
```

執行後，您應該會看到一個透明背景的視窗出現在桌面上，Live2D 角色會自動載入並顯示。

### 對話功能使用

1. **文本輸入**：在視窗底部的輸入框中輸入訊息，按 Enter 發送
2. **語音輸入**：點擊麥克風按鈕（目前為 UI 準備，STT 功能待後續整合）
3. **查看回應**：LLM 的回應會以對話泡泡框的形式顯示在角色上方

### 操作說明

- **拖動視窗**：按住滑鼠左鍵拖動視窗到任意位置
- **視窗置頂**：視窗會自動保持在最上層

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
│   ├── llm_client.py       # Gemini API 客戶端
│   └── chat_bubble.py      # 對話泡泡框組件
├── mao_pro_en/            # Live2D 角色資源
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
- ✅ LLM 對話功能（Gemini API）
- ✅ 文本輸入框 UI
- ✅ 語音輸入按鈕 UI（準備完成）
- ✅ 對話泡泡框顯示

### 規劃中
- ⏳ 語音識別（Gemini STT API 整合）
- ⏳ 語音合成（TTS）
- ⏳ 角色動畫控制（根據對話觸發動畫）
- ⏳ 對話歷史保存

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
