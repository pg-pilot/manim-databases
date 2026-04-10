#!/usr/bin/env bash
# Render every animated debug scene as a low-quality MP4 + extract frames.
#
# The MP4 lands in media/videos/btree_animated/480p15/.
# We also extract a few frames as PNGs so the animation can be inspected
# without playing the video.
#
# Usage: bash tests/visual/render_animated.sh

set -euo pipefail

cd "$(dirname "$0")/../.."

CONTAINER="${MANIM_CONTAINER:-ws-manim-databases}"
WORKDIR="/workspaces/manim-databases"
SCENE_FILE="tests/visual/btree_animated.py"

if ! docker ps --format '{{.Names}}' | grep -qx "$CONTAINER"; then
    echo "container '$CONTAINER' is not running" >&2
    exit 1
fi

scenes=$(grep -E '^class [A-Za-z0-9_]+\(Scene\):' "$SCENE_FILE" \
    | sed -E 's/^class ([A-Za-z0-9_]+).*/\1/')

mkdir -p tests/visual/frames

for scene in $scenes; do
    echo "→ rendering $scene"
    docker exec -w "$WORKDIR" "$CONTAINER" \
        .venv/bin/manim -ql "$SCENE_FILE" "$scene" 2>&1 \
        | grep -E "(File ready|ERROR|Traceback|Error)" || true

    mp4="media/videos/btree_animated/480p15/${scene}.mp4"
    if [ ! -f "$mp4" ]; then
        echo "  ✗ no mp4 produced"
        continue
    fi

    # Extract 5 evenly-spaced frames as PNGs for inspection.
    docker exec -w "$WORKDIR" "$CONTAINER" bash -c "
        ffmpeg -y -i '$mp4' \
            -vf 'select=not(mod(n\\,15))' -vsync vfr \
            'tests/visual/frames/${scene}_%03d.png' 2>/dev/null
    " || true
    echo "  ✓ frames in tests/visual/frames/${scene}_*.png"
done
