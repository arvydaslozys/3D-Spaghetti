import cv2
import numpy as np
import pytest

from camera.camera import KlipperMoonrakerCamera


@pytest.mark.parametrize("ret,frame,expected", [
(False, None, None),
(True, np.zeros((100, 100, 3), dtype=np.uint8), np.zeros((100, 100, 3), dtype=np.uint8))])
def test_get_frame_returns_image_on_success_and_none_on_read_failure(monkeypatch, ret, frame, expected):

    class FakeCapture:
        def read(self):
            return ret, frame

        def release(self):
            pass

    monkeypatch.setattr(cv2, "VideoCapture", lambda url: FakeCapture())

    camera = KlipperMoonrakerCamera("camera.local")

    result = camera.get_frame()
    
    if expected is None:
        assert result is None
    else:
        np.testing.assert_array_equal(result, expected)

def test_get_frame_returns_none_for_invalid_ip(monkeypatch):
    camera = KlipperMoonrakerCamera("111.111.111.111")
    result = camera.get_frame()
    assert result is None
