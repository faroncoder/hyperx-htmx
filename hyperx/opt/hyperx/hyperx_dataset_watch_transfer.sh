#!/usr/bin/env sh
#
# fs_inotifywatch_dataset_transfer.sh
# UNIX-style watcher for dataset auto-sync and AI model generation.
#
# Moves new CSV/JSON files from uploads → /dataset,
# then triggers HyperX AI Schema AutoGen service.
#

WATCH_SRC="/media/uploads/dataset"
WATCH_DEST="/dataset"
LOG_FILE="/var/log/fs_inotifywatch_dataset_transfer.log"
AUTOGEN_SCRIPT="/opt/hyperx/ai_schema_autogen.py"
PYTHON_BIN="/usr/bin/python3"

log() {
  printf "%s %s\n" "$(date '+%F %T')" "$1" >> "$LOG_FILE"
}

log "🚀 Dataset watcher started (sh version)"

inotifywait -m -e create,move "$WATCH_SRC" --format '%w%f' | while read -r FILE
do
  [ ! -f "$FILE" ] && continue

  BASENAME=$(basename "$FILE")
  EXT="${BASENAME##*.}"
  DEST_FILE="$WATCH_DEST/$BASENAME"

  case "$EXT" in
    csv|json)
      if mv "$FILE" "$DEST_FILE" 2>/dev/null; then
        log "✅ Moved: $BASENAME → $WATCH_DEST"

        # 🔥 Trigger AI Schema Autogen asynchronously
        nohup "$PYTHON_BIN" "$AUTOGEN_SCRIPT" "$DEST_FILE" >> "$LOG_FILE" 2>&1 &

      else
        log "❌ Failed to move: $BASENAME"
      fi
      ;;
    *)
      log "⚠️ Ignored non-dataset file: $BASENAME"
      ;;
  esac
done
