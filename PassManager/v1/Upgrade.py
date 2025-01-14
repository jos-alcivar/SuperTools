from __future__ import absolute_import

import logging

import Utils


__all__ = ['Upgrade']

log = logging.getLogger("PassManager.Upgrade")


def Upgrade(node):
    Utils.UndoStack.DisableCapture()
    try:
        pass
        # This is where you would detect an out-of-date version:
        #    node.getParameter('version')
        # and upgrade the internal network.
    except Exception as exception:
        log.exception('Error upgrading PassManager node "%s": %s'
                      % (node.getName(), str(exception)))
    finally:
        Utils.UndoStack.EnableCapture()