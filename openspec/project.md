# Project Context

## Purpose
此專案旨在製作一個在 Windows 桌面上顯示動漫角色形象的 LLM 助手。使用者可以透過打字或語音與助手互動，助手將協助完成各種任務（如同一般 LLM 能夠完成的事項）。角色形象將以動畫形式呈現在桌面上，提供更親切、互動的使用體驗。

## Tech Stack
- **Python** - 主要開發語言
- **PyQt6** - 桌面應用程式框架，用於創建無邊框視窗和 UI 元件
- **live2d-py** - Live2D 動畫角色渲染和顯示
- **其他相關套件** - 用於語音輸入/輸出、API 整合等

## Project Conventions

### Code Style
- 遵循業界正規語法命名規則
- 使用清晰的變數和函數命名
- 適當的註解和文檔字串
- 遵循 PEP 8 Python 編碼規範

### Architecture Patterns
- **純本地端架構** - 所有處理都在本地執行
- **後台服務模式** - 應用程式以 exe 形式執行後，在後台持續監聽和執行
- **模組化設計** - 將角色渲染、LLM 整合、語音處理等功能分離為獨立模組
- **事件驅動** - 基於使用者互動事件（打字、語音）觸發相應處理流程

### Testing Strategy
- 單元測試覆蓋核心功能模組
- 整合測試驗證各模組間的協作
- 手動測試驗證 UI 互動和角色動畫表現

### Git Workflow
- 使用功能分支進行開發
- 提交訊息遵循約定式提交格式
- 主要分支保護，透過 Pull Request 進行代碼審查

## Domain Context
- **Live2D 角色模型** - 專案中包含 Live2D 角色資源（如 `mao_pro_en`），包含模型文件（.moc3）、動畫（.motion3.json）、表情（.exp3.json）等
- **桌面應用程式** - 需要處理視窗置頂、無邊框顯示、點擊穿透等桌面整合特性
- **LLM 整合** - 需要處理 API 請求、回應解析、對話上下文管理等
- **語音互動** - 需要整合語音識別（STT）和語音合成（TTS）功能

## Important Constraints
- **Windows 平台專用** - 目前僅支援 Windows 作業系統
- **本地執行** - 所有處理應在本地完成，不依賴遠端服務（除 LLM API 外）
- **資源效率** - 需要考慮記憶體和 CPU 使用，確保後台運行不影響系統效能
- **API 額度限制** - 使用免費額度的 Gemini/Gemma API，需要考慮請求頻率和成本控制

## External Dependencies
- **Gemini/Gemma API** - Google 的 LLM API，用於處理使用者的文字和語音輸入，生成回應
  - 使用免費額度進行初步測試
  - 需要 API Key 配置
  - 需要處理 API 請求限制和錯誤處理
