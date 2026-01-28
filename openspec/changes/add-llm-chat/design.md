# Design: LLM 對話功能

## Context
需要在現有的桌面角色顯示基礎上，添加 LLM 對話功能，讓使用者能夠與角色進行文字和語音互動。使用 Gemini API 作為 LLM 服務提供者。

## Goals / Non-Goals

### Goals
- 實現文字輸入和 LLM 對話功能
- 以對話泡泡框形式顯示回應
- 整合 Gemini API（gemini-2.5-flash-lite）
- 準備語音輸入 UI（為後續 STT 整合做準備）
- 保持 UI 簡潔，不影響角色顯示

### Non-Goals
- 不實現語音識別功能（僅準備 UI，後續變更）
- 不實現複雜的對話歷史管理（簡單的上下文即可）
- 不實現多輪對話的複雜邏輯（單輪對話為主）

## Decisions

### Decision: 使用 google-generativeai Python SDK
**What**: 選擇官方 Google Generative AI Python SDK 進行 Gemini API 整合。

**Why**: 
- 官方維護，穩定可靠
- 支援 Gemini 2.5 Flash Lite 模型
- 簡單易用的 API
- 良好的錯誤處理

**Alternatives considered**:
- 直接使用 HTTP 請求: 需要自行處理認證和錯誤，複雜度高
- 其他 LLM SDK: Gemini 官方 SDK 最適合

### Decision: 對話泡泡框設計
**What**: 使用 PyQt6 的 QLabel 或自定義 Widget 實現對話泡泡框，顯示在角色上方。

**Why**:
- 簡單直觀的 UI 設計
- 易於實現和維護
- 可以自定義樣式（圓角、背景色等）

**Alternatives considered**:
- 使用 HTML/WebView: 過於複雜，不符合純本地端架構
- 使用 Canvas 繪製: 實現複雜度高

### Decision: API Key 配置方式
**What**: 使用環境變數或配置文件存儲 API Key。

**Why**:
- 安全性：不將 API Key 硬編碼在代碼中
- 靈活性：易於在不同環境中配置
- 符合最佳實踐

**Alternatives considered**:
- 硬編碼: 不安全，不推薦
- 加密存儲: 對於本地應用過於複雜

## Risks / Trade-offs

### Risk: API Key 安全性
**Mitigation**: 
- 使用環境變數或配置文件
- 在 .gitignore 中排除配置文件
- 提供清晰的配置說明

### Risk: API 請求失敗
**Mitigation**:
- 實現錯誤處理和重試機制
- 顯示友好的錯誤訊息
- 不阻塞應用程式運行

### Risk: UI 遮擋角色
**Mitigation**:
- 泡泡框自動定位，避免遮擋角色
- 可以設置自動消失時間
- 允許使用者手動關閉

## Migration Plan

### 實施步驟
1. 創建 OpenSpec 規範文檔
2. 實現 UI 組件（輸入框、按鈕、泡泡框）
3. 整合 Gemini API
4. 實現對話流程
5. 測試和優化

### Rollback
如果實現出現問題，可以：
- 暫時禁用對話功能
- 保持角色顯示功能正常

## Open Questions

- [ ] 對話泡泡框的顯示時長應該是多少？
- [ ] 是否需要保存對話歷史到文件？
- [ ] 語音輸入的觸發方式（按住/點擊）？
