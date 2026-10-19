import subprocess
import sys

WITHOUT_MSS = """
import sys
sys.modules["mss"] = None
import tapper.helper.img
"""


def test_import_without_img_extras_tells_what_to_install() -> None:
    result = subprocess.run(
        [sys.executable, "-c", WITHOUT_MSS], capture_output=True, text=True
    )
    assert result.returncode != 0
    assert "pip install tapper[img]" in result.stderr
