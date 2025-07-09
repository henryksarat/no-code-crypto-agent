#!/bin/bash

echo "🚀 准备优化的Vercel部署..."

# 清理不必要的文件
echo "🧹 清理临时文件..."
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
rm -rf .pytest_cache
rm -f app.log
rm -rf *.egg-info

# 检查项目大小
echo "📏 检查项目大小..."
total_size=$(du -sh . | cut -f1)
echo "当前项目大小: $total_size"

# 检查是否超过Vercel限制
size_bytes=$(du -s . | cut -f1)
size_mb=$((size_bytes / 1024))

if [ $size_mb -gt 200 ]; then
    echo "⚠️  警告: 项目大小 ${size_mb}MB 可能接近Vercel限制"
    echo "建议检查.vercelignore文件是否正确配置"
fi

# 检查是否已登录Vercel
if ! vercel whoami &>/dev/null; then
    echo "请先登录Vercel:"
    vercel login
fi

echo "📝 使用优化配置部署到Vercel..."
echo "✅ 使用.vercelignore忽略不必要文件"
echo "✅ 配置了50MB Lambda大小限制"

# 部署
vercel --prod

echo "✅ 部署完成！"
echo ""
echo "📋 请确保在Vercel Dashboard中设置了以下环境变量："
echo "   - AI_MODEL_PROVIDER=deepseek"
echo "   - DEEPSEEK_API_KEY=your_deepseek_api_key"
echo "   - FUNDING_WALLET_PRIVATE_KEY=your_private_key (可选)"
echo "   - FUNDING_WALLET_PUBLIC_KEY=your_public_key (可选)"
echo ""
echo "💡 提示: Phantom集成不需要私钥，推荐使用!"