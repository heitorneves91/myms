#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
appimage="${MYMS_FREECAD_APPIMAGE:-/home/heits/tools/freecad}"
mount_log="$(mktemp)"
"$appimage" --appimage-mount >"$mount_log" 2>&1 &
mount_pid=$!
trap 'kill "$mount_pid" 2>/dev/null || true' EXIT
for attempt in {1..50}; do
    IFS= read -r appdir < "$mount_log" || true
    if [[ -n "${appdir:-}" && -d "$appdir/usr/lib" ]]; then break; fi
    sleep 0.1
done
export MYMS_FREECAD_LIB="$appdir/usr/lib"
"$appdir/AppRun" python -c 'import os,sys,runpy; sys.path.append(os.environ["MYMS_FREECAD_LIB"]); import FreeCADGui as G; G.setupWithoutGUI(); runpy.run_path("scripts/build_model.py",run_name="__main__")'
if [[ "${1:-}" == "--render" ]]; then
    "$appdir/AppRun" python -c 'import os,sys,runpy; sys.path.append(os.environ["MYMS_FREECAD_LIB"]); runpy.run_path("scripts/render_model.py",run_name="__main__"); runpy.run_path("scripts/render_sensor_demo.py",run_name="__main__")'
fi
