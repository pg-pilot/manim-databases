#!/usr/bin/env bash
# Render every static debug scene as a single PNG (last frame only).
# Usage: bash tests/visual/render.sh [scene_file]
#
# Default scene file is tests/visual/btree_states.py. Pass another file
# to render its scenes instead.
#
# Manim runs inside the devcontainer (ws-manim-databases) where the venv
# is set up. The host invokes it via `docker exec`.

set -euo pipefail
scene_file="${1:-tests/visual/btree_states.py}"

cd "$(dirname "$0")/../.."

CONTAINER="${MANIM_CONTAINER:-ws-manim-databases}"
WORKDIR="/workspaces/manim-databases"

# Discover scene class names by grepping for `class FOO(Scene):`
scenes=$(grep -E '^class [A-Za-z0-9_]+\(Scene\):' "$scene_file" \
    | sed -E 's/^class ([A-Za-z0-9_]+).*/\1/')

if [ -z "$scenes" ]; then
    echo "no Scene classes found in $scene_file" >&2
    exit 1
fi

if ! docker ps --format '{{.Names}}' | grep -qx "$CONTAINER"; then
    echo "container '$CONTAINER' is not running" >&2
    echo "open the project in VS Code (or set MANIM_CONTAINER=...)" >&2
    exit 1
fi

for scene in $scenes; do
    echo "→ rendering $scene"
    docker exec -w "$WORKDIR" "$CONTAINER" \
        .venv/bin/manim -ql -s "$scene_file" "$scene" 2>&1 \
        | grep -E "(File ready|ERROR|Traceback|Error)" || true
done

echo
out_dir="media/images/$(basename "$scene_file" .py)"
echo "PNGs in: ${out_dir}/"
ls -1 "$out_dir/" 2>/dev/null || echo "  (none yet)"
