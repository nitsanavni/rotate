import pytest
from approvaltests.reporters import PythonNativeReporter

@pytest.fixture(autouse=True)
def set_native_reporter(monkeypatch):
    # Patch the ApprovalTests default reporter to use the native CLI reporter
    from approvaltests import set_default_reporter
    set_default_reporter(PythonNativeReporter())
