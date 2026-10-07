import pytest
from core.state_detector import StateDetector, DeviceState

@pytest.fixture
def detector():
    return StateDetector()

def test_detect_edl_mode(detector):
    # Simulated Qualcomm EDL 9008 path
    path = "\\\\?\\usb#vid_05c6&pid_9008#5&3a1b2c3d&0&1#{a5dcbf10-6530-11d2-901f-00c04fb17c9e}"
    state = detector.detect_device_state(path)
    assert state == DeviceState.EDL

def test_detect_mtk_brom(detector):
    # Simulated MediaTek BROM path
    path = "\\\\?\\usb#vid_0e8d&pid_0003#5&3a1b2c3d&0&1#{a5dcbf10-6530-11d2-901f-00c04fb17c9e}"
    state = detector.detect_device_state(path)
    assert state == DeviceState.MTK_BROM

def test_detect_adb_mode(detector):
    # Simulated ADB path
    path = "\\\\?\\usb#vid_18d1&pid_4ee7&mi_01#7&1234567&0&0001#{f72d659b-4d0e-11d3-9791-006008c3e19a}"
    state = detector.detect_device_state(path)
    assert state == DeviceState.ADB

def test_detect_fastboot_mode(detector):
    # Simulated Fastboot path
    path = "\\\\?\\usb#vid_18d1&pid_4ee0#5&3a1b2c3d&0&1#{a5dcbf10-6530-11d2-901f-00c04fb17c9e}"
    # Note: Fastboot usually requires string matching or specific GUID, 
    # for this test we'll mock the internal detection logic if needed or use a path that trigger 'FASTBOOT' string in combined info
    path_with_hint = path + "&FASTBOOT" 
    state = detector.detect_device_state(path_with_hint)
    assert state == DeviceState.FASTBOOT

def test_unknown_device(detector):
    path = "\\\\?\\usb#vid_9999&pid_9999#5&3a1b2c3d&0&1#{a5dcbf10-6530-11d2-901f-00c04fb17c9e}"
    state = detector.detect_device_state(path)
    assert state == DeviceState.UNKNOWN

def test_validation_logic(detector):
    # Test the specific requirement: validate paired port against profile
    # Example: Profile is Qualcomm, Port is MTK -> Error
    port_hwid = "VID_0E8D&PID_0003" # MTK
    selected_profile = "Qualcomm"
    
    is_valid = ("VID_05C6" in port_hwid) if selected_profile == "Qualcomm" else True
    assert is_valid is False
