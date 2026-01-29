"""
對話泡泡框組件 - 顯示 LLM 回應的對話泡泡
"""
from __future__ import annotations

from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QPainter, QColor, QFont, QPen
from PyQt6.QtWidgets import QWidget, QTextEdit, QFrame


class ChatBubble(QWidget):
    """對話泡泡框組件（支持滾動和格式化顯示）"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.text = ""
        self._opacity = 0.0
        self.auto_hide_timer = QTimer(self)
        self.auto_hide_timer.timeout.connect(self.fade_out)
        self.auto_hide_timer.setSingleShot(True)
        
        # 泡泡框大小固定（過長內容用內部文字區滾動）
        self.fixed_width = 420
        self.fixed_height = 220
        
        # 設置視窗標誌（無邊框、透明背景）
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # 設置字體
        self.font = QFont("Microsoft YaHei", 10)
        self.code_font = QFont("Consolas", 9)  # 代碼字體
        
        # 設置固定大小
        self.setFixedSize(self.fixed_width, self.fixed_height)

        # 文字顯示區：使用 QTextEdit 處理多行與滾動
        self.text_edit = QTextEdit(self)
        self.text_edit.setReadOnly(True)
        # 取消邊框外觀
        self.text_edit.setFrameShape(QFrame.Shape.NoFrame)
        self.text_edit.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAsNeeded
        )
        self.text_edit.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.text_edit.setStyleSheet("""
            QTextEdit {
                background: transparent;
                border: none;
                padding: 10px;
                color: black;
            }
        """)
        self.text_edit.setFont(self.font)
        # 讓滑鼠滾輪直接作用在文字區
        self.setMouseTracking(True)
        
        # 淡入動畫
        self.fade_in_animation = QPropertyAnimation(self, b"opacity")
        self.fade_in_animation.setDuration(300)
        self.fade_in_animation.setStartValue(0.0)
        self.fade_in_animation.setEndValue(1.0)
        self.fade_in_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
        # 淡出動畫
        self.fade_out_animation = QPropertyAnimation(self, b"opacity")
        self.fade_out_animation.setDuration(300)
        self.fade_out_animation.setStartValue(1.0)
        self.fade_out_animation.setEndValue(0.0)
        self.fade_out_animation.setEasingCurve(QEasingCurve.Type.InCubic)
        self.fade_out_animation.finished.connect(self.hide)
    
    def get_opacity(self) -> float:
        """獲取透明度"""
        return self._opacity
    
    def set_opacity(self, value: float):
        """設置透明度"""
        self._opacity = value
        self.update()
    
    opacity = pyqtProperty(float, get_opacity, set_opacity)
    
    def show_message(self, text: str, duration: int = 10000):
        """
        顯示訊息
        
        Args:
            text: 要顯示的文字（支持格式化）
            duration: 自動隱藏時間（毫秒），0 表示不自動隱藏
        """
        self.text = text
        # 大小固定，不再依內容改變；過長內容由內部 QTextEdit 滾動
        self.setFixedSize(self.fixed_width, self.fixed_height)

        formatted = self._format_text(text)
        # 根據內容型態切換字體
        is_code = formatted.strip().startswith('{') or formatted.strip().startswith('[')
        self.text_edit.setFont(self.code_font if is_code else self.font)
        self.text_edit.setPlainText(formatted)
        self.text_edit.move(5, 5)
        self.text_edit.resize(self.width() - 10, self.height() - 10)
        
        # 顯示並淡入
        self.show()
        self.fade_in_animation.start()
        
        # 設置自動隱藏
        if duration > 0:
            self.auto_hide_timer.start(duration)

    def set_text_live(self, text: str):
        """
        在不重置滾動位置與淡入動畫的情況下，更新當前顯示文字。
        適用於 LLM 串流過程中持續追加內容。
        """
        self.text = text
        formatted = self._format_text(text)
        # 這裡不切換字體，以免在使用者滾動時突然跳動；僅更新內容
        # 保留 QTextEdit 目前的滾動位置
        scroll_bar = self.text_edit.verticalScrollBar()
        value = scroll_bar.value()
        self.text_edit.setPlainText(formatted)
        scroll_bar.setValue(value)
        self.update()
    
    def _format_text(self, text: str) -> str:
        """
        格式化文本，保留換行和結構
        
        Args:
            text: 原始文本
            
        Returns:
            格式化後的文本
        """
        # 保留換行
        formatted = text
        
        # 檢測 JSON 格式（簡單檢測）
        if text.strip().startswith('{') or text.strip().startswith('['):
            # 嘗試美化 JSON（簡單版本）
            try:
                import json
                parsed = json.loads(text)
                formatted = json.dumps(parsed, indent=2, ensure_ascii=False)
            except:
                pass  # 如果不是有效 JSON，保持原樣
        
        return formatted
    
    def fade_out(self):
        """淡出並隱藏"""
        self.fade_out_animation.start()
    
    def paintEvent(self, event):
        """繪製泡泡框"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 設置透明度
        painter.setOpacity(self._opacity)
        
        # 繪製圓角矩形背景
        rect = self.rect().adjusted(5, 5, -5, -5)
        painter.setBrush(QColor(255, 255, 255, 240))
        painter.setPen(QPen(QColor(200, 200, 200, 200), 2))
        painter.drawRoundedRect(rect, 15, 15)
        # 文字由內部 QTextEdit 負責繪製與滾動
