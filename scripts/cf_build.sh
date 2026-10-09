#!/usr/bin/env bash
# Cloudflare Pages build: copy only the public site into dist/
# (keeps backups, previews, scripts, data, docs, templates out of the live site)
set -euo pipefail
rm -rf dist && mkdir dist
for f in *; do
  case "$f" in
    dist|backups|previews|scripts|functions|workers|data|docs|templates|tests|node_modules|README.md|REDESIGN-REVIEW.md|package.json|package-lock.json|_config.yml|CNAME|booking-handler.php) continue ;;
  esac
  cp -R "$f" dist/
done
echo "Built $(find dist -type f | wc -l) files into dist/"
