"""
角色互動模組 - 處理角色部位點擊和對應的動作、回應
"""
from __future__ import annotations

import random
import re
from typing import Dict, Optional, Tuple, List
from pathlib import Path


class CharacterInteraction:
    """角色互動管理器"""
    
    # 部位對應的動作和回應
    # 注意：根據實際模型配置，目前只有 HitAreaHead 和 HitAreaBody
    # 其他部位可以通過點擊位置判斷或後續擴展
    INTERACTION_MAP: Dict[str, Dict[str, str]] = {
        "HitAreaHead": {
            "motion": "mtn_02",  # 動作索引 0
            "response": "謝謝主人 <3 ~"
        },
        "HitAreaBody": {
            "motion": "mtn_03",  # 動作索引 1
            "response": "主人！你要幹嘛？！"
        },
        # 以下為擴展部位（如果模型支持或通過位置判斷）
        "HitAreaHand": {
            "motion": "mtn_04",  # 動作索引 2
            "response": "牽手手~"
        },
        "HitAreaFoot": {
            "motion": "special_01",  # 動作索引 3
            "response": "不要碰我的腳啦~"
        },
        "HitAreaBelly": {
            "motion": "special_02",  # 動作索引 4
            "response": "好癢喔~"
        },
        "HitAreaChest": {
            "motion": "special_03",  # 動作索引 5
            "response": "變態！不要亂摸！"
        },
    }
    
    # 預設動作（如果部位未定義）
    DEFAULT_MOTION = "mtn_02"
    DEFAULT_RESPONSE = "嗯？怎麼了？"

    # 由「部件 PartId」推斷互動區域（因為 HitPart 回傳的是 Part* 而非 HitArea*）
    # 這是啟發式映射：不同模型可能需要調整
    PART_PATTERNS: List[Tuple[re.Pattern, str]] = [
        # 軀幹 / 披風
        (re.compile(r"^PartCore$|Robe|Body", re.IGNORECASE), "HitAreaBody"),
        # 腿 / 腳
        (re.compile(r"^PartLeg", re.IGNORECASE), "HitAreaFoot"),
        # 手 / 手臂 / 魔杖
        (re.compile(r"^PartArm|Hand|Wand", re.IGNORECASE), "HitAreaHand"),
        # 頭部：包含帽子、臉、嘴、眼睛等
        (re.compile(r"Head|Face|Hair|Eye|Brow|Hat|Mouth", re.IGNORECASE), "HitAreaHead"),
        # 胸部
        (re.compile(r"Chest|Bust", re.IGNORECASE), "HitAreaChest"),
        # 肚子
        (re.compile(r"Belly|Stomach", re.IGNORECASE), "HitAreaBelly"),
    ]

    # 讓回覆更自然：同一部位可隨機挑一句
    RESPONSES: Dict[str, List[str]] = {
        "HitAreaHead": [
            "謝謝主人 <3 ~",
            "嘿嘿～摸摸頭最舒服了！",
            "呀～別弄亂我的頭髮啦！",
        ],
        "HitAreaBody": [
            "主人！你要幹嘛？！",
            "嗯？怎麼啦？",
            "我在這裡喔～",
        ],
        "HitAreaHand": [
            "牽手手～",
            "握緊緊，不准放開！",
            "要一起去散步嗎？",
        ],
        "HitAreaFoot": [
            "不要碰我的腳啦～",
            "癢癢的！",
            "哼哼～想偷襲嗎？",
        ],
        "HitAreaBelly": [
            "好癢喔～",
            "咕嚕咕嚕…肚子在叫了",
            "別戳啦～我會笑出來！",
        ],
        "HitAreaChest": [
            "變態！不要亂摸！",
            "住手！那裡不行！",
            "你、你在看哪裡啦！",
        ],
    }
    
    def __init__(self, model_config_path: Optional[Path] = None):
        """
        初始化互動管理器
        
        Args:
            model_config_path: Live2D 模型配置文件路徑
        """
        self.model_config_path = model_config_path
        self.hit_areas: Dict[str, str] = {}
        
        if model_config_path:
            self._load_hit_areas()
    
    def _load_hit_areas(self):
        """從模型配置載入 Hit Areas"""
        if not self.model_config_path or not self.model_config_path.exists():
            return
        
        try:
            import json
            with open(self.model_config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # 載入 Hit Areas
            hit_areas = config.get("HitAreas", [])
            for area in hit_areas:
                area_id = area.get("Id", "")
                area_name = area.get("Name", "")
                if area_id:
                    self.hit_areas[area_id] = area_name
        except Exception as e:
            print(f"載入 Hit Areas 失敗: {e}")
    
    def get_interaction(self, hit_area_id: str) -> Tuple[str, str]:
        """
        獲取點擊部位的互動信息
        
        Args:
            hit_area_id: Hit Area ID（如 "HitAreaHead"）
            
        Returns:
            (動作名稱, 回應文本) 的元組
        """
        # 查找對應的互動
        interaction = self.INTERACTION_MAP.get(hit_area_id)
        
        if interaction:
            # 允許同一區域隨機回覆
            responses = self.RESPONSES.get(hit_area_id)
            if responses:
                return interaction["motion"], random.choice(responses)
            return interaction["motion"], interaction["response"]
        
        # 如果未找到，使用預設
        return self.DEFAULT_MOTION, self.DEFAULT_RESPONSE

    def get_interaction_for_part(self, part_id: str) -> Tuple[str, str, str]:
        """
        由 HitPart 回傳的 PartId 推斷互動並回傳「推斷後的互動區域 + 動作名稱 + 回覆」。
        """
        hit_area_id = self._infer_hit_area_from_part(part_id)
        motion, response = self.get_interaction(hit_area_id)
        return hit_area_id, motion, response

    def _infer_hit_area_from_part(self, part_id: str) -> str:
        part_id = (part_id or "").strip()
        for pattern, area in self.PART_PATTERNS:
            if pattern.search(part_id):
                return area
        return "HitAreaBody"
    
    def get_all_hit_areas(self) -> Dict[str, str]:
        """獲取所有 Hit Areas"""
        return self.hit_areas.copy()
