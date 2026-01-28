# GitHub 倉庫連接指南

## 連接步驟

### 1. 初始化 Git 倉庫（如果尚未初始化）

```bash
cd d:\Work_File\Project\Desktop_helper
git init
```

### 2. 添加遠端倉庫

```bash
git remote add origin https://github.com/gcobs051094/Desktop_Helper_LLM.git
```

### 3. 配置 Git 用戶信息（如果尚未配置）

```bash
git config user.name "您的名稱"
git config user.email "您的郵箱"
```

### 4. 添加文件並提交

```bash
# 添加所有文件
git add .

# 提交更改
git commit -m "Initial commit: 桌面角色顯示和 LLM 對話功能"

# 推送到遠端倉庫
git push -u origin main
```

如果遇到分支名稱問題，可以使用：

```bash
# 重命名分支為 main（如果需要）
git branch -M main

# 推送到遠端
git push -u origin main
```

## 注意事項

- `.env` 文件已加入 `.gitignore`，不會被提交（保護 API Key）
- 請確保在提交前設置好 `.env` 文件（參考 `.env.example`）
- 如果遇到權限問題，請檢查 OneDrive 同步設置

## 後續操作

### 日常提交和推送

```bash
# 查看狀態
git status

# 添加更改
git add .

# 提交
git commit -m "描述您的更改"

# 推送
git push
```

### 拉取遠端更改

```bash
git pull origin main
```
