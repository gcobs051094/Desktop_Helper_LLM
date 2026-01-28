"""
LLM 客戶端模組 - 整合 Gemini API 進行對話處理
"""
from __future__ import annotations

import os
from typing import Optional
from dotenv import load_dotenv

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("警告: google-generativeai 未安裝")
    print("請執行: pip install google-generativeai")


class LLMClient:
    """Gemini API 客戶端"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化 LLM 客戶端
        
        Args:
            api_key: Gemini API Key，如果為 None 則從環境變數讀取
        """
        if not GEMINI_AVAILABLE:
            raise ImportError("google-generativeai 未安裝")
        
        # 載入環境變數
        load_dotenv()
        
        # 獲取 API Key
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "未找到 Gemini API Key。請設置環境變數 GEMINI_API_KEY 或在代碼中提供。"
            )
        
        # 配置 Gemini
        genai.configure(api_key=self.api_key)
        
        # 初始化模型（gemini-2.5-flash-lite）
        self.model = genai.GenerativeModel('gemini-2.5-flash-lite')
        
        # 對話歷史
        self.chat_history = []
    
    def send_message(self, message: str) -> str:
        """
        發送訊息並獲取回應
        
        Args:
            message: 使用者輸入的訊息
            
        Returns:
            LLM 的回應文字
        """
        if not GEMINI_AVAILABLE:
            return "錯誤: Gemini API 未正確配置"
        
        try:
            # 發送訊息
            response = self.model.generate_content(message)
            
            # 獲取回應文字
            reply = response.text if response.text else "未收到有效回應"
            
            # 記錄對話歷史（可選，用於上下文）
            self.chat_history.append({"role": "user", "content": message})
            self.chat_history.append({"role": "assistant", "content": reply})
            
            return reply
            
        except Exception as e:
            error_msg = f"API 請求失敗: {str(e)}"
            print(error_msg)
            return error_msg
    
    def clear_history(self):
        """清除對話歷史"""
        self.chat_history = []
