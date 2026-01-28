# Change: 新增桌面角色顯示功能

## Why
使用者需要一個能夠在 Windows 桌面上顯示動漫角色形象的功能，作為 LLM 助手的前置基礎。角色需要以透明背景的形式出現在桌面上，為後續的互動功能奠定基礎。

## What Changes
- 新增透明背景的桌面視窗顯示功能（PyQt6 + QOpenGLWidget）
- 整合 Live2D 角色渲染引擎（live2d-py 庫）
- 實現角色模型載入和顯示（支援 Cubism 3.0+ 格式）
- 實現視窗置頂、拖動等基本互動功能
- 實現角色動畫自動播放（待機動畫）
- 創建主程式入口點和模組化架構

## Impact
- 受影響的規範：新增 `desktop-display` 能力
- 受影響的代碼：
  - 新建 `src/desktop_window.py`（桌面視窗管理）
  - 新建 `src/live2d_widget.py`（Live2D 渲染引擎）
  - 新建 `src/character_loader.py`（角色資源載入）
  - 新建 `main.py`（主程式入口）
- 新增依賴：PyQt6, live2d-py, PyOpenGL, numpy
