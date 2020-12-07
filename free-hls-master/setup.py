from distutils.core import setup
from Cython.Build import cythonize

# 我们看到构建扩展模块通过distutils.core下的setup
# 但是我们说distutils只能完成第二步，第一步要由Cython完成
# 所以使用cythonize("LSBSteg.pyx")
setup(ext_modules=cythonize("LSBSteg.pyx"))

# cythonize("LSBSteg.pyx")负责将Cython代码转成C代码
# 然后根据C代码生成扩展模块，我们可以传入单个文件，也可以是多个文件组成的列表
# 或者一个glob模式，会匹配满足模式的所有Cython文件