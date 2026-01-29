# Change: 新增角色互動功能和 UI 改進

## Why
使用者需要能夠與桌面角色進行更豐富的互動，包括點擊角色不同部位觸發動畫和回應。同時需要改進 UI 的可讀性和顯示效果。

## What Changes
- 修復文本輸入框文字顏色問題（改為黑色）
- 實現角色部位點擊檢測功能
- 實現不同部位對應的動作和回應（頭、肩膀、手、腳、肚子、胸部等）
- 改進對話泡泡框：支持滾動、調整寬度、格式化顯示（換行、JSON等）

## Impact
- 受影響的規範：修改 `desktop-display` 和 `llm-chat` 能力
- 受影響的代碼：
  - 修改 `src/desktop_window.py`（添加點擊檢測和互動邏輯）
  - 修改 `src/chat_bubble.py`（改進顯示功能）
  - 新建 `src/character_interaction.py`（互動邏輯）
