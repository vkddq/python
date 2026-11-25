"""Той самий еталон, перевірка звичайним assert у pytest."""
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def test_report_matches_unchanged_golden():
    target = os.environ.get('BLOCKNOT_TARGET', 'blocknot.py')
    # Окремий процес дає старому коду свіжий глобальний список.
    result = subprocess.run(
        [sys.executable, str(ROOT / target)], cwd=ROOT,
        env=dict(os.environ, PYTHONIOENCODING='utf-8'),
        capture_output=True, text=True, encoding='utf-8', check=True,
    )
    expected = (ROOT / 'golden/report.txt').read_text(encoding='utf-8')
    assert result.stdout == expected
