"""Один незмінний тест для старої та кожної нової версії."""
import contextlib
import importlib.util
import io
import os
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class GoldenMasterTest(unittest.TestCase):
    def test_report_matches_golden(self):
        source = ROOT / os.environ.get("BLOCKNOT_TARGET", "blocknot.py")
        spec = importlib.util.spec_from_file_location("tested_blocknot", source)
        module = importlib.util.module_from_spec(spec)
        import sys
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            module.zvit(ROOT / "barakhlo.csv")
        expected = (ROOT / "golden/report.txt").read_text(encoding="utf-8")
        self.assertEqual(expected, output.getvalue())


if __name__ == "__main__":
    unittest.main()
