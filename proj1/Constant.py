class Const:
    class ConstError(TypeError):
        pass

    class ConstCaseError(ConstError):
        pass

    def __setattr__(self, name, value):
        if name in self.__dict__:
            raise self.ConstError("Can't change const value!")
        if not name.isupper():
            raise self.ConstCaseError('const "%s" is not all letters are capitalized' % name)
        self.__dict__[name] = value


import sys

sys.modules[__name__] = Const()

import constant

# 裁剪图片偏移量
# 宽度控制

constant.DEVICE_X_THREE = 575
constant.WIDTH_PX = 350
constant.GAP = (constant.DEVICE_X_THREE-constant.WIDTH_PX)/2
constant.DEVICE_X_THREE-(2*constant.GAP)
constant.DEVICE_X_THREE-(2*constant.GAP)
constant.HEIGHT_PX = 950
constant.DX0 = 380
constant.DX1 = constant.DX0 + constant.DEVICE_X_THREE
constant.DX2 = constant.DX1 + constant.DEVICE_X_THREE
constant.DX3 = constant.DX2 + constant.DEVICE_X_THREE
constant.DY0 = 650
constant.DY1 = constant.DY0 + constant.HEIGHT_PX

# 路径
constant.ORIGINAL_SUCCESS_IMAGE_PATH = './original_images/success_images/'
constant.ORIGINAL_FAIL_IMAGE_PATH = './original_images/failure_images/'
constant.ORIGINAL_PREDICT_IMAGE_PATH = './original_images/check_images/'
constant.SYNTHESIS_IMAGE_PATH = './synthesis_images/'
constant.TRAIN_IMAGES_PATH_LIST = [constant.ORIGINAL_SUCCESS_IMAGE_PATH, constant.ORIGINAL_FAIL_IMAGE_PATH]
constant.PREDICT_IMAGES_PATH_LIST = [constant.ORIGINAL_PREDICT_IMAGE_PATH]

# 测试集
constant.BEST_MODEL_PATH = 'net_no_validation_acc1.0'
constant.LAST_MODEL_PATH = 'net_last.pkl'


