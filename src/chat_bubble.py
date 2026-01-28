"""
對話泡泡框組件 - 顯示 LLM 回應的對話泡泡
"""
from __future__ import annotations

from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QPainter, QColor, QFont, QPen
from PyQt6.QtWidgets import QWidget, QLabel


class ChatBubble(QWidget):
    """對話泡泡框組件"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.text = ""
        self._opacity = 0.0
        self.auto_hide_timer = QTimer(self)
        self.auto_hide_timer.timeout.connect(self.fade_out)
        self.auto_hide_timer.setSingleShot(True)
        
        # 設置視窗標誌（無邊框、透明背景）
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # 設置字體
        self.font = QFont("Microsoft YaHei", 10)
        
        # 設置初始大小
        self.setFixedSize(300, 100)
        
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
            text: 要顯示的文字
            duration: 自動隱藏時間（毫秒），0 表示不自動隱藏
        """
        self.text = text
        
        # 計算所需大小
        font_metrics = self.fontMetrics()
        text_rect = font_metrics.boundingRect(
            0, 0, 280, 0,
            Qt.AlignmentFlag.AlignLeft | Qt.TextFlag.TextWordWrap,
            text
        )
        
        # 設置大小（留邊距）
        width = min(text_rect.width() + 40, 400)
        height = max(text_rect.height() + 30, 60)
        self.setFixedSize(width, height)
        
        # 顯示並淡入
        self.show()
        self.fade_in_animation.start()
        
        # 設置自動隱藏
        if duration > 0:
            self.auto_hide_timer.start(duration)
    
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
        
        # 繪製文字
        painter.setPen(QColor(50, 50, 50))
        painter.setFont(self.font)
        painter.drawText(
            rect.adjusted(10, 10, -10, -10),
            Qt.AlignmentFlag.AlignLeft | Qt.TextFlag.TextWordWrap,
            self.text
        )
