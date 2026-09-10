#!/bin/bash
# Отправляет репозиторий по частям.
#
# Канал отдаёт 0.7 Мбит/с: 130 МБ одним куском не доходят — обрывается и
# загрузка образа в Railway, и обычный git push. Куски по 20–25 МБ уезжают
# за несколько минут каждый, а обрыв стоит одного куска, а не всей отправки.
set -u
cd "$HOME/Downloads/works-site" || exit 1

push() {
  local msg="$1"
  git commit -q -m "$msg

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>" 2>/dev/null || {
    echo "  нечего коммитить: $msg"; return 0; }
  local try
  for try in 1 2 3; do
    if git push -q origin main 2>/dev/null; then
      echo "  отправлено: $msg"
      return 0
    fi
    echo "  обрыв (попытка $try): $msg"
    sleep 10
  done
  echo "  НЕ ОТПРАВЛЕНО: $msg"
  return 1
}

echo "=== 1. код и страницы ==="
git add -A ':!assets' ':!w'
push "Код сайта, генератор страниц и бэкенд"

echo "=== 2. страницы работ ==="
git add w
push "Страница на каждую работу"

echo "=== 3. лёгкие ассеты ==="
git add assets/css assets/js assets/og assets/poster
push "Стили, скрипт, превью ссылок, постеры"

echo "=== 4. видео ==="
git add assets/vid
push "Видеоработы"

echo "=== 5. миниатюры ==="
git add assets/thumb
push "Миниатюры"

echo "=== 6. работы, частями ==="
i=0
part=1
batch=()
for f in assets/img/*.jpg; do
  batch+=("$f")
  i=$((i + 1))
  if [ ${#batch[@]} -ge 85 ]; then
    git add "${batch[@]}"
    push "Работы, часть $part"
    batch=()
    part=$((part + 1))
  fi
done
if [ ${#batch[@]} -gt 0 ]; then
  git add "${batch[@]}"
  push "Работы, часть $part"
fi

echo "=== итог ==="
git status --porcelain | wc -l | tr -d ' ' | sed 's/^/  неотправленных файлов: /'
git log --oneline | wc -l | tr -d ' ' | sed 's/^/  коммитов: /'
