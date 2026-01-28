# Design: 桌面角色顯示功能

## Context
需要實現一個在 Windows 桌面上顯示動漫角色的功能，作為後續 LLM 助手互動的視覺基礎。角色需要以透明背景形式顯示，不阻擋桌面內容，並且可以與使用者互動（拖動、點擊等）。

## Goals / Non-Goals

### Goals
- 在 Windows 桌面上顯示透明背景的動漫角色
- 支援 Live2D 格式的角色模型（Cubism 3.0+）
- 實現視窗置頂、拖動等基本互動功能
- 角色動畫自動播放（待機動畫）
- 模組化設計，便於後續擴展

### Non-Goals
- 不實現 LLM 對話功能（後續變更）
- 不實現語音互動（後續變更）
- 不支援多角色同時顯示（未來可擴展）
- 不實現複雜的動畫控制（基本動畫即可）

## Decisions

### Decision: 使用 PyQt6 + OpenGL 進行渲染
**What**: 選擇 PyQt6 作為桌面應用框架，使用 QOpenGLWidget 提供 OpenGL 上下文進行 Live2D 渲染。

**Why**: 
- PyQt6 提供完整的桌面應用程式功能，支援透明視窗、置頂等特性
- QOpenGLWidget 提供 OpenGL 渲染上下文，符合 Live2D 的渲染需求
- PyQt6 在 Windows 平台有良好的支援和穩定性

**Alternatives considered**:
- PyQt5: 較舊版本，PyQt6 是更好的選擇
- Tkinter: 不支援 OpenGL 渲染
- Electron: 過於龐大，不符合純本地端架構需求

### Decision: 使用 live2d-py 庫
**What**: 選擇 `live2d-py` 作為 Live2D 的 Python 綁定庫。

**Why**:
- 官方支援 Cubism 3.0+ 格式（.moc3, .model3.json）
- 提供完整的 Python API，易於整合
- 支援 OpenGL 渲染
- 活躍的社群維護

**Alternatives considered**:
- 直接使用 Cubism SDK C++ 綁定: 需要自行編譯和綁定，複雜度高
- Web 版本轉換: 不符合本地端架構需求

### Decision: 模組化架構設計
**What**: 將功能分離為獨立模組：
- `desktop_window.py`: 桌面視窗管理
- `live2d_widget.py`: Live2D 渲染引擎
- `character_loader.py`: 角色資源載入

**Why**:
- 職責分離，易於維護和測試
- 便於後續擴展（如添加多角色支援）
- 符合單一職責原則

**Alternatives considered**:
- 單一文件實現: 不利於維護和擴展

### Decision: 透明背景實現方式
**What**: 使用 PyQt6 的 `WA_TranslucentBackground` 屬性配合 OpenGL 透明緩衝區。

**Why**:
- PyQt6 原生支援，實現簡單
- 性能良好，不影響渲染效率
- 與 OpenGL 渲染兼容

**Alternatives considered**:
- 使用遮罩: 複雜度高，性能較差

## Risks / Trade-offs

### Risk: live2d-py 依賴 Live2D SDK
**Mitigation**: 
- 在 README 中明確說明 SDK 下載和配置步驟
- 提供清晰的錯誤提示和故障排除指南

### Risk: OpenGL 上下文初始化時機
**Mitigation**:
- 在 `initializeGL` 中正確初始化 Live2D
- 處理模型載入的時序問題（等待 OpenGL 上下文就緒）

### Risk: 性能問題（高頻率動畫渲染）
**Mitigation**:
- 使用 60 FPS 的計時器（16ms 間隔）
- 優化渲染循環，避免不必要的重繪

## Migration Plan

### 實施步驟
1. ✅ 創建專案結構和依賴配置
2. ✅ 實現透明桌面視窗
3. ✅ 整合 Live2D 渲染引擎
4. ✅ 實現角色載入和顯示
5. ⏳ 測試和優化

### Rollback
如果實現出現問題，可以：
- 回退到僅顯示佔位符的版本
- 保持視窗框架，暫時禁用 Live2D 渲染

## Open Questions

- [ ] 是否需要支援角色點擊互動（如點擊觸發動畫）？
- [ ] 視窗大小是否應該根據角色模型自動調整？
- [ ] 是否需要保存視窗位置到配置文件？
