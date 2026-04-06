#!/bin/zsh
CURRENT=$(openclaw --version 2>/dev/null | grep -oE '[0-9]{4}\.[0-9]+\.[0-9]+')
LATEST=$(npm show openclaw version 2>/dev/null)

if [ -z "$CURRENT" ] || [ -z "$LATEST" ]; then
  echo "버전 확인 실패"
  exit 1
fi

if [ "$CURRENT" != "$LATEST" ]; then
  echo "업데이트 발견: $CURRENT → $LATEST"
  npm install -g openclaw@latest 2>&1 | tail -3
  openclaw gateway restart
  echo "✅ OpenClaw $LATEST 업데이트 완료, 게이트웨이 재시작됨"
else
  echo "최신 버전 유지 중: $CURRENT"
fi
