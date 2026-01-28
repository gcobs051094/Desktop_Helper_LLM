"""
角色載入模組 - 負責載入和管理 Live2D 角色模型
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional, List


class CharacterLoader:
    """Live2D 角色載入器"""
    
    def __init__(self, model_path: Path):
        """
        初始化角色載入器
        
        Args:
            model_path: Live2D 模型文件的路徑（.model3.json 文件）
        """
        self.model_path = Path(model_path)
        self.runtime_path = self.model_path.parent / "runtime"
        self.model_config: Optional[Dict] = None
    
    def load_model_config(self) -> Dict:
        """
        載入模型配置文件
        
        Returns:
            模型配置字典
        """
        if not self.model_path.exists():
            raise FileNotFoundError(f"模型文件不存在: {self.model_path}")
        
        with open(self.model_path, 'r', encoding='utf-8') as f:
            self.model_config = json.load(f)
        
        return self.model_config
    
    def get_moc_path(self) -> Path:
        """獲取 .moc3 文件路徑"""
        if not self.model_config:
            self.load_model_config()
        
        moc_file = self.model_config.get("FileReferences", {}).get("Moc")
        if not moc_file:
            raise ValueError("模型配置中未找到 Moc 文件")
        
        return self.runtime_path / moc_file
    
    def get_texture_paths(self) -> List[Path]:
        """獲取紋理文件路徑列表"""
        if not self.model_config:
            self.load_model_config()
        
        textures = self.model_config.get("FileReferences", {}).get("Textures", [])
        return [self.runtime_path / tex for tex in textures]
    
    def get_motions_path(self) -> Dict[str, List[Path]]:
        """獲取動作文件路徑字典"""
        if not self.model_config:
            self.load_model_config()
        
        motions_config = self.model_config.get("FileReferences", {}).get("Motions", {})
        motions = {}
        
        for motion_group, motion_files in motions_config.items():
            motions[motion_group] = [
                self.runtime_path / motion["File"]
                for motion in motion_files
            ]
        
        return motions
    
    def get_expressions_path(self) -> Dict[str, Path]:
        """獲取表情文件路徑字典"""
        if not self.model_config:
            self.load_model_config()
        
        expressions_config = self.model_config.get("FileReferences", {}).get("Expressions", [])
        expressions = {}
        
        for expr in expressions_config:
            name = expr.get("Name")
            file_path = expr.get("File")
            if name and file_path:
                expressions[name] = self.runtime_path / file_path
        
        return expressions
