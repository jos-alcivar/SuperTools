from __future__ import absolute_import

from .Node import PassManagerNode

def GetEditor():
    from .Editor import PassManagerEditor
    return PassManagerEditor