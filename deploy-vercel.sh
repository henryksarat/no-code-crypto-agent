#!/bin/bash

echo "🚀 开始部署到Vercel..."

# 检查是否已登录Vercel
if ! vercel whoami &>/dev/null; then
    echo "请先登录Vercel:"
    vercel login
fi

echo "📝 部署项目到Vercel..."
vercel --prod

echo "✅ 部署完成！"
echo "📋 记住在Vercel Dashboard中设置以下环境变量："
echo "   - DEEPSEEK_API_KEY: 你的DeepSeek API密钥"
echo "   - AI_MODEL_PROVIDER: deepseek"
echo "   - FUNDING_WALLET_PRIVATE_KEY: 你的私钥"
echo "   - FUNDING_WALLET_PUBLIC_KEY: 你的公钥"