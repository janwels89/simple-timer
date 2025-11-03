import pytest
import platform

def is_arm():
    return 'arm' in platform.machine() or 'aarch64' in platform.machine()

@pytest.fixture
def display():
    # Import hardware or mock inside the fixture to avoid side effects at collection time
    if is_arm():
        from app.display import Display as Disp
    else:
        from features.steps.mocks.mock_sh1106 import SH1106 as Disp
    disp = Disp()
    disp.Init()
    return disp

def test_display_init_and_clear(display):
    display.clear()
    if hasattr(display, "is_cleared"):
        assert display.is_cleared is True
    if hasattr(display, "last_operation"):
        assert "clear" in display.last_operation

def test_display_show_image(display):
    dummy_buffer = [0] * ((display.width // 8) * display.height)
    display.ShowImage(dummy_buffer)
    if hasattr(display, "last_operation"):
        assert "ShowImage" in display.last_operation

def test_display_getbuffer(display):
    image = None
    buf = display.getbuffer(image)
    assert isinstance(buf, list)
    assert len(buf) == (display.width // 8) * display.height