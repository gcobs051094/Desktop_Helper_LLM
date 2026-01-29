## 1. OpenSpec 規範文檔
- [x] 1.1 創建 proposal.md
- [x] 1.2 創建 design.md
- [x] 1.3 創建 spec.md
- [x] 1.4 創建 tasks.md

## 2. UI 組件實現
- [x] 2.1 創建文本輸入框組件
- [x] 2.2 創建語音輸入按鈕（麥克風圖標）
- [x] 2.3 創建對話泡泡框組件
- [x] 2.4 整合 UI 組件到桌面視窗

## 3. Gemini API 整合
- [x] 3.1 添加 google-generativeai 依賴
- [x] 3.2 創建 LLM 客戶端模組
- [x] 3.3 實現 API 配置管理（API Key，使用環境變數）
- [x] 3.4 實現對話發送和接收功能

## 4. 對話流程實現
- [x] 4.1 實現文本輸入處理
- [x] 4.2 實現 API 請求發送
- [x] 4.3 實現回應顯示（泡泡框）
- [x] 4.4 實現錯誤處理

## 5. GitHub 連接
- [x] 5.1 創建 .gitignore 文件
- [x] 5.2 創建 GIT_SETUP.md 連接指南
- [x] 5.3 創建 .env.example 範例文件
- [ ] 5.4 用戶手動執行 Git 命令連接倉庫（見 GIT_SETUP.md）

## 6. 串流對話與發送 / 停止按鈕
- [x] 6.1 在 `LLMClient` 中實作 `stream_message`，使用 Gemini Streaming API 持續產生回應片段
- [x] 6.2 在 `DesktopCharacterWindow` 中使用背景執行緒（QThread）串流接收 LLM 回應，並逐步更新對話泡泡框內容
- [x] 6.3 在視窗底部新增「發送訊息」按鈕（Enter 圖示），點擊或按 Enter 時觸發串流對話
- [x] 6.4 串流期間將發送按鈕切換為「停止」圖示（黑色方形），再次點擊時停止串流並不再更新泡泡框
- [x] 6.5 串流期間禁止角色點擊互動；串流自然結束或被停止後才恢復角色點擊
