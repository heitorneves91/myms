#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
test_binary=$(mktemp /tmp/myms-controller-test.XXXXXX)
trap 'rm -f "$test_binary"' EXIT
g++ -std=c++17 -Wall -Wextra -Werror -fsanitize=address,undefined -I firmware/include firmware/test/controller_test.cpp -o "$test_binary"
"$test_binary"
python3 -m unittest discover -s scripts/tests -p 'test_*.py'
python3 - <<'PY'
from pathlib import Path
import subprocess
import tempfile
ui = Path('firmware/include/web_ui.h').read_text()
js = ui.split('<script>', 1)[1].split('</script>', 1)[0]
with tempfile.NamedTemporaryFile(suffix='.js', mode='w') as file:
    file.write(js)
    file.flush()
    subprocess.run(['node', '--check', file.name], check=True)
print('Embedded admin JavaScript syntax passed')
PY
