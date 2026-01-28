# Change: 新增 LLM 對話功能

## Why
使用者需要能夠與桌面角色進行對話互動，透過文字或語音輸入與 LLM 進行交流，並以對話泡泡框的形式顯示回應，實現完整的 LLM 助手體驗。

## What Changes
- 新增文本輸入框 UI 組件
- 新增語音輸入按鈕（UI 準備，後續串接 Gemini STT）
- 整合 Gemini API（gemini-2.5-flash-lite）進行對話處理
- 實現對話泡泡框顯示 LLM 回應
- 連接 GitHub 倉庫進行版本控制

## Impact
- 受影響的規範：新增 `llm-chat` 能力，修改 `desktop-display` 能力
- 受影響的代碼：
  - 修改 `src/desktop_window.py`（添加 UI 組件）
  - 新建 `src/llm_client.py`（Gemini API 客戶端）
  - 新建 `src/chat_bubble.py`（對話泡泡框組件）
  - 新建 `src/voice_input.py`（語音輸入準備）
