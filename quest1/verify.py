"""Відтворювана перевірка: еталон не створюється і не оновлюється."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def main():
    manifest = json.loads((ROOT / 'evidence/baseline_sha256.json').read_text(encoding='utf-8'))
    for name, expected in manifest.items():
        actual = hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
        if actual != expected:
            raise SystemExit(f'CHANGED: {name}')
    print('Original, CSV, golden master and golden test SHA256: unchanged')
    if importlib.util.find_spec('pytest') is None:
        print('pytest is not installed. Run: python -m pip install -r requirements-dev.txt')
        return 2
    env = dict(os.environ, PYTHONPATH=str(ROOT), PYTHONIOENCODING='utf-8', PYTHONDONTWRITEBYTECODE='1')
    results = []
    targets = ['original/blocknot.py', 'stages/01_item.py',
               'stages/02_inventory.py', 'blocknot.py']
    # Спочатку незмінний історичний тест на всіх чотирьох версіях.
    # Потім pytest-еквівалент на всіх версіях та нові тести на фінальній.
    checks = []
    for target in targets:
        checks.append((target, 'historical', [sys.executable, '-m', 'unittest',
                       'discover', '-s', 'tests', '-p', 'test_golden.py', '-v']))
    for target in targets:
        selection = 'tests' if target == 'blocknot.py' else 'tests/test_golden_pytest.py'
        checks.append((target, 'pytest', [sys.executable, '-m', 'pytest', selection, '-v']))
    for index, (target, runner, command) in enumerate(checks):
        env['BLOCKNOT_TARGET'] = target
        result = subprocess.run(command,
                                cwd=ROOT, env=env, capture_output=True, encoding='utf-8')
        log = result.stdout + result.stderr
        (ROOT / f'evidence/pytest_verify_{index}.txt').write_text(log, encoding='utf-8')
        results.append({'target': target, 'runner': runner, 'exit_code': result.returncode})
        print(f'{runner} / {target}: {"PASS" if result.returncode == 0 else "FAIL"}')
        if result.returncode:
            print(log)
            return result.returncode
    (ROOT / 'evidence/pytest_verification.json').write_text(
        json.dumps({'python': sys.version, 'hashes_unchanged': True, 'runs': results}, indent=2),
        encoding='utf-8')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
