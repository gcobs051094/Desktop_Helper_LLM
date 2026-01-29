"""
LLM 客戶端模組 - 整合 Gemini API 進行對話處理
"""
from __future__ import annotations

import os
from typing import Optional, Iterable
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
        self.model = genai.GenerativeModel(
            'gemini-2.5-flash-lite',
            generation_config={
                "max_output_tokens": 2048,
            },
        )
        
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
        # 非串流模式：在內部透過 stream_message 聚合所有片段
        chunks = []
        for delta in self.stream_message(message):
            chunks.append(delta)
        return "".join(chunks)
    
    def clear_history(self):
        """清除對話歷史"""
        self.chat_history = []

    def stream_message(self, message: str) -> Iterable[str]:
        """
        以串流方式發送訊息並逐步取得回應片段。
        呼叫端可以一邊迭代、一邊更新 UI。
        """
        if not GEMINI_AVAILABLE:
            error_msg = "錯誤: Gemini API 未正確配置"
            print(error_msg)
            yield error_msg
            return

        full_text = ""
        try:
            response = self.model.generate_content(message, stream=True)
            for chunk in response:
                text = getattr(chunk, "text", None)
                if not text:
                    continue
                full_text += text
                yield text
        except Exception as e:
            error_msg = f"API 請求失敗: {str(e)}"
            print(error_msg)
            # 對呼叫端輸出錯誤片段，方便 UI 顯示
            yield error_msg
        finally:
            if full_text:
                self.chat_history.append({"role": "user", "content": message})
                self.chat_history.append({"role": "assistant", "content": full_text})
