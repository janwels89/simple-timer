import sys
import os
import platform
import pytest

# Add the repo root to sys.path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def is_arm():
    return 'arm' in platform.machine() or 'aarch64' in platform.machine()

@pytest.fixture
def Display():
    # Import as late as possible to avoid blocking/hardware initialisation on import
    if is_arm():
        from app.display import Display as RealDisplay
        return RealDisplay
    else:
        from features.steps.mocks.mock_sh1106 import SH1106 as MockDisplay
        return MockDisplay

def test_display_init_and_clear(Display):
    disp = Display()
    disp.Init()
    disp.clear()
    # Check mock: is_cleared or buffer log
    if hasattr(disp, "is_cleared"):
        assert disp.is_cleared is True
    if hasattr(disp, "last_operation"):
        assert "clear" in disp.last_operation

def test_display_show_image(Display):
    disp = Display()
    dummy_buffer = [0] * ((disp.width // 8) * disp.height)
    disp.ShowImage(dummy_buffer)
    if hasattr(disp, "last_operation"):
        assert "ShowImage" in disp.last_operation

def test_display_getbuffer(Display):
    disp = Display()
    # Simulate a PIL image with correct attributes if needed; here just None for mock
    image = None
    buf = disp.getbuffer(image)
    assert isinstance(buf, list)
    assert len(buf) == (disp.width // 8) * disp.height