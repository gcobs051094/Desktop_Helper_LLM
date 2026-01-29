# Design: 角色互動功能和 UI 改進

## Context
使用者需要能夠與桌面角色進行更豐富的互動，包括點擊角色不同部位觸發動畫和回應。同時需要改進 UI 的可讀性和顯示效果，特別是文本輸入框和對話泡泡框。

## Goals / Non-Goals

### Goals
- 修復文本輸入框文字顏色問題，確保可讀性
- 實現角色部位點擊檢測和互動
- 不同部位觸發不同的動作和回應
- 改進對話泡泡框：支持滾動、調整寬度、格式化顯示

### Non-Goals
- 不實現複雜的動畫序列（單個動作觸發即可）
- 不實現自定義互動映射配置（使用預定義映射）

## Decisions

### Decision: 使用 Live2D HitPart API 進行點擊檢測
**What**: 使用 live2d-py 提供的 `HitPart` 方法檢測點擊的部位。

**Why**: 
- Live2D SDK 原生支持 Hit Areas 檢測
- 準確度高，性能好
- 符合 Live2D 標準實現

**Alternatives considered**:
- 手動計算點擊位置: 複雜度高，準確度低
- 使用圖像識別: 過於複雜，不符合需求

### Decision: 泡泡框使用自定義繪製而非 QTextEdit
**What**: 繼續使用 QWidget 的自定義 paintEvent 繪製泡泡框，但添加滾動支持。

**Why**:
- 保持透明背景和自定義樣式
- 可以精確控制繪製效果
- 性能較好

**Alternatives considered**:
- 使用 QTextEdit: 難以實現透明背景和自定義樣式
- 使用 QLabel: 不支持滾動

### Decision: 動作映射使用預定義字典
**What**: 在 `character_interaction.py` 中定義部位到動作和回應的映射字典。

**Why**:
- 簡單直接，易於維護
- 可以根據不同模型調整
- 不需要複雜的配置文件

**Alternatives considered**:
- 使用配置文件: 對於簡單映射過於複雜
- 使用數據庫: 不符合本地端架構需求

## Risks / Trade-offs

### Risk: Hit Areas 可能不完整
**Mitigation**: 
- 根據實際模型配置調整映射
- 提供預設動作和回應作為後備

### Risk: 泡泡框滾動可能不夠流暢
**Mitigation**:
- 使用適當的滾動步長
- 考慮後續優化為 QScrollArea（如果需要）

### Risk: 格式化顯示可能不完美
**Mitigation**:
- 實現基本的 JSON 格式化
- 保留換行符
- 後續可以增強格式化支持

## Migration Plan

### 實施步驟
1. ✅ 修復文本輸入框顏色
2. ✅ 改進泡泡框顯示功能
3. ✅ 實現角色互動功能
4. ⏳ 測試和優化

### Rollback
如果實現出現問題，可以：
- 暫時禁用點擊互動功能
- 恢復簡單的泡泡框顯示

## Open Questions

- [ ] 是否需要支持自定義互動映射？
- [ ] 泡泡框的最大高度是否合適？
- [ ] 是否需要添加點擊動畫效果？
