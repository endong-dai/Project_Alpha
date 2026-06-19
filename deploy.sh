#!/usr/bin/env bash
# 一键发布：提交源码 -> pygbag 打包 -> 覆盖 docs/ -> 提交 -> push (触发 GitHub Pages)
# 用法:  bash deploy.sh
set -e
cd "$(dirname "$0")"

echo "==> 0/6 检查 pygbag"
if ! python3 -c "import pygbag" >/dev/null 2>&1; then
  echo "!! pygbag 未安装。请先运行:  pip3 install pygbag"
  echo "!! 装好后重新执行 bash deploy.sh"
  exit 1
fi
echo "pygbag OK"

echo "==> 1/6 回归测试"
python3 run_tests.py | tail -1

echo "==> 2/6 提交源码改动"
git add -A
if git diff --cached --quiet; then
  echo "（无新的源码改动，跳过提交）"
else
  git commit -m "Add weapon triangle + class promotion systems, tests, balance sim

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
fi

echo "==> 3/6 pygbag 打包 web 版"
python3 -m pygbag --build --template default.tmpl main.py

echo "==> 4/6 覆盖进 docs/"
cp -r build/web/* docs/
touch docs/.nojekyll
echo "--- 产物大小 ---"
du -sh build/web 2>/dev/null || true
ls -la docs

echo "==> 5/6 提交 docs"
git add -A
if git diff --cached --quiet; then
  echo "（docs 无变化，跳过）"
else
  git commit -m "Update web deployment (weapon triangle + promotion)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
fi

echo "==> 6/6 push 到 GitHub"
git push origin main

echo ""
echo "✅ 完成。等 1-2 分钟 GitHub Pages 构建后访问:"
echo "   https://endong-dai.github.io/Project_Alpha/"
