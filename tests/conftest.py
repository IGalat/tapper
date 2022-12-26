import sys

import pytest
from testutil_model import Dummy


@pytest.fixture
def dummy() -> Dummy:
    return Dummy()


@pytest.fixture
def is_debug() -> bool:
    return hasattr(sys, "gettrace") and (sys.gettrace() is not None)
