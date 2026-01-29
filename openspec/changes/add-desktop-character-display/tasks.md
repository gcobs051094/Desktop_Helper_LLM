## 1. 專案設置
- [x] 1.1 創建 requirements.txt 並添加必要依賴（PyQt6, live2d-py, PyOpenGL, numpy）
- [x] 1.2 設置專案目錄結構（src/, openspec/）

## 2. OpenSpec 規範文檔
- [x] 2.1 創建 proposal.md（變更提案）
- [x] 2.2 創建 design.md（技術設計決策）
- [x] 2.3 創建 spec.md（需求規範）
- [x] 2.4 創建 tasks.md（實施檢查清單）

## 3. 桌面視窗實現
- [x] 3.1 創建 DesktopCharacterWindow 類（透明背景、無邊框）
- [x] 3.2 實現視窗置頂功能（WindowStaysOnTopHint）
- [x] 3.3 實現視窗可拖動功能（滑鼠事件處理）
- [x] 3.4 設置視窗初始位置（桌面右下角）

## 4. Live2D 整合
- [x] 4.1 研究並選擇 Live2D Python 庫（選擇 live2d-py）
- [x] 4.2 創建 Live2DWidget 類（QOpenGLWidget）
- [x] 4.3 實現 OpenGL 初始化（initializeGL）
- [x] 4.4 實現角色模型載入功能（LoadModelJson）
- [x] 4.5 實現角色渲染循環（paintGL, Update, Draw）
- [x] 4.6 實現動畫播放（StartRandomMotion）
- [x] 4.7 整合 Live2DWidget 到 DesktopCharacterWindow

## 5. 角色資源管理
- [x] 5.1 創建 CharacterLoader 類（模型配置載入）
- [x] 5.2 實現模型路徑解析和驗證
- [x] 5.3 實現資源文件路徑獲取（moc, textures, motions, expressions）

## 6. 多角色與角色切換
- [x] 6.1 設計角色素材庫資料結構（以程式碼集中管理可用角色）
- [x] 6.2 在 `src/character_library.py` 中實作角色清單與預設角色選擇邏輯
- [x] 6.3 更新 `main.py` 由角色素材庫取得預設角色與角色清單
- [x] 6.4 在 `DesktopCharacterWindow` 中新增角色切換按鈕與切換邏輯（單一視窗輪流切換角色）

## 6. 主程式
- [x] 6.1 創建 main.py 入口點
- [x] 6.2 實現角色資源路徑配置
- [x] 6.3 實現應用程式初始化和事件循環
- [x] 6.4 實現錯誤處理和用戶提示

## 7. 文檔和測試
- [x] 7.1 更新 README.md（使用說明、技術堆疊）
- [ ] 7.2 測試完整流程（需要用戶驗證）
