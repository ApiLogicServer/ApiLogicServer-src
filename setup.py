"""
Project metadata and package discovery live in pyproject.toml.  This file exists only for one build hook:

    prototypes/manager/samples  ->  prototypes/manager/samples.zip   (in the built wheel only)

Why: the unzipped sample paths (up to ~170 chars) plus the install prefix
(<venv>\\Lib\\site-packages\\api_logic_server_cli\\prototypes\\manager\\) exceed the Windows 260-char
MAX_PATH for users without LongPathsEnabled, so `pip install` fails.  A zip is one short path.
`genai-logic start` expands it into the Manager (see create_from_model/api_logic_server_utils.py:
copy_manager_prototype), where the prefix is much shorter.

Source tree and editable installs (pip -e) are unchanged: samples/ stays unzipped in gold, no zip exists.
The zip is built from the files build_py actually copied, so MANIFEST.in excludes (*.pyc, *.zip, ...) still
apply; file modes (run.sh exec bit) are taken from the source files.  Nothing to do in BLT: it runs
`python -m build` and this hook runs inside it.
"""
import os
import shutil
import zipfile
from pathlib import Path

from setuptools import setup
from setuptools.command.build_py import build_py

PKG_MANAGER = Path('api_logic_server_cli') / 'prototypes' / 'manager'
SAMPLES = 'samples'
SAMPLES_ZIP = 'samples.zip'     # keep in sync with api_logic_server_utils.SAMPLES_ZIP


class BuildPyZipSamples(build_py):

    def run(self):
        super().run()
        build_manager = Path(self.build_lib) / PKG_MANAGER
        built_samples = build_manager / SAMPLES
        if not built_samples.is_dir():
            return          # nothing was packaged (e.g. samples excluded) - nothing to zip
        src_samples = Path(__file__).parent / PKG_MANAGER / SAMPLES
        zip_path = build_manager / SAMPLES_ZIP
        if zip_path.exists():
            zip_path.unlink()
        count = 0
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
            for root, dirs, files in os.walk(built_samples):
                dirs.sort()
                for name in sorted(files):
                    built_file = Path(root) / name
                    rel = built_file.relative_to(build_manager)         # samples/<...>
                    info = zipfile.ZipInfo.from_file(built_file, arcname=rel.as_posix())
                    src_file = Path(__file__).parent / PKG_MANAGER / rel
                    mode = (src_file if src_file.exists() else built_file).stat().st_mode
                    info.external_attr = (mode & 0xFFFF) << 16          # preserves exec bits
                    info.compress_type = zipfile.ZIP_DEFLATED
                    with open(built_file, 'rb') as f, zf.open(info, 'w') as dest:
                        shutil.copyfileobj(f, dest)
                    count += 1
        shutil.rmtree(built_samples)        # the wheel carries the zip, not the long paths
        self.announce(f'zipped {count} files from {SAMPLES}/ into {SAMPLES_ZIP} '
                      f'({zip_path.stat().st_size / 1_000_000:.1f} MB)', level=2)


setup(cmdclass={'build_py': BuildPyZipSamples})
