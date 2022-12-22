# This Python file uses the following encoding: utf-8

from ctypes import CDLL, c_char_p, c_void_p, c_size_t, py_object, c_int


flib = CDLL("./shadows/libeye/libeye.so")

_native_create = flib.Eye_create
_native_create.argtypes = [c_char_p]
_native_create.restype = c_void_p

_native_destroy = flib.Eye_destroy
_native_destroy.argtypes = [c_void_p]
_native_destroy.restype = None

_native_captureScreen = flib.Eye_captureScreen
_native_captureScreen.argtypes = [c_void_p]
_native_captureScreen.restype = None

_native_requestRegion = flib.Eye_requestRegion
_native_requestRegion.argtypes = [c_void_p, c_char_p]
_native_requestRegion.restype = py_object

_native_requestPoint = flib.Eye_requestPoint
_native_requestPoint.argtypes = [c_void_p, c_char_p]
_native_requestPoint.restype = py_object

_native_learn = flib.Eye_learn
_native_learn.argtypes = [c_void_p, c_int, c_int, c_int, c_int]
_native_learn.restype = c_size_t

_native_find = flib.Eye_find
_native_find.argtypes = [c_void_p, c_size_t]
_native_find.restype = py_object

_native_importFromBase64 = flib.Eye_importFromBase64
_native_importFromBase64.argtypes = [c_char_p, c_size_t]
_native_importFromBase64.restype = c_void_p

_native_exportAsBase64 = flib.Eye_exportAsBase64
_native_exportAsBase64.argtypes = [c_void_p]
_native_exportAsBase64.restype = py_object

_native_screenSize = flib.Eye_screenSize
_native_screenSize.argtypes = [c_void_p]
_native_screenSize.restype = py_object


class EyeException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Eye:


    def __init__(self, configFilepath=None, base64data=None):
        if configFilepath is not None:
            encodedFilepath = configFilepath.encode("utf-8")
            self.ptr = _native_create(encodedFilepath)

        elif base64data is not None:
            eBase64data = base64data.encode("utf-8")
            self.ptr = _native_importFromBase64(eBase64data, len(eBase64data))

    def capture_screen(self):
        self.assert_not_closed()
        _native_captureScreen(self.ptr)

    def screen_size(self):
        self.assert_not_closed()
        return _native_screenSize(self.ptr)

    def request_region(self, title):
        self.assert_not_closed()
        eTitle = title.encode("utf-8")
        target = _native_requestRegion(self.ptr, eTitle)

        if target is None:
            raise EyeException("User did not select a region")

        return target

    def request_point(self, title):
        self.assert_not_closed()
        eTitle = title.encode("utf-8")
        point = _native_requestPoint(self.ptr, eTitle)

        if point is None:
            raise EyeException("User did not select a point")

        return point

    def learn(self, region):
        self.assert_not_closed()
        return _native_learn(self.ptr, region[0], region[1], region[2], region[3])

    def find(self, id):
        self.assert_not_closed()
        return _native_find(self.ptr, id)

    @staticmethod
    def importFromBase64(base64data):
        return Eye(base64data=base64data)

    def exportAsBase64(self):
        self.assert_not_closed()
        return _native_exportAsBase64(self.ptr)

    def close(self):
        if self.ptr is not None:
            _native_destroy(self.ptr)
            self.ptr = None

    def assert_not_closed(self):
        if self.ptr is None:
            raise RuntimeError("This object is already closed")
