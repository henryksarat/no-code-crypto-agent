# Vercel部署指南

## 环境变量配置

在Vercel控制台中，需要设置以下环境变量：

### 必需的环境变量：

1. **DEEPSEEK_API_KEY**
   - 你的DeepSeek API密钥
   - 从 https://platform.deepseek.com 获取

2. **AI_MODEL_PROVIDER** 
   - 设置为 `deepseek`
   - 使用免费的DeepSeek AI模型

### 可选的环境变量：

3. **OPENAI_API_KEY** (可选)
   - 如果想使用OpenAI而不是DeepSeek
   - 需要将AI_MODEL_PROVIDER设置为 `openai`

## 部署步骤

1. 将代码推送到GitHub仓库
2. 在Vercel中导入项目
3. 配置环境变量
4. 部署

## 访问应用

部署完成后，访问你的Vercel URL即可使用Phantom钱包集成的Solana代理。

## 功能特性

- 🔒 安全的Phantom钱包集成
- 🤖 中文/英文自然语言处理
- 💰 钱包余额查询
- 📊 交易历史查看  
- 🔄 代币操作
- 🆓 免费DeepSeek AI支持

## 技术栈

- Python Flask
- DeepSeek AI API
- Solana Web3.js
- Phantom Wallet SDK