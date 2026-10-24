#!/usr/bin/env python
"""
Compatibility shim: the report generator is now requirements_traceability_report.py
(it writes docs/requirements/Requirements Traceability Report.md). This file keeps the old command working:

    python behave_logic_report.py run          # same as: python requirements_traceability_report.py run
"""
import runpy
import sys
from pathlib import Path

if __name__ == '__main__':
    target = Path(__file__).resolve().with_name('requirements_traceability_report.py')
    sys.argv[0] = str(target)
    runpy.run_path(str(target), run_name='__main__')
