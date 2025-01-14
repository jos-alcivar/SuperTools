from __future__ import absolute_import

from Katana import NodegraphAPI

def GetRefNode(gnode, key):
    p = gnode.getParameter('node_'+key)
    if not p:
        return None
    
    return NodegraphAPI.GetNode(p.getValue(0))


def AddNodeReferenceParam(destNode, paramName, node):
    param = destNode.getParameter(paramName)
    if not param:
        param = destNode.getParameters().createChildString(paramName, '')
    
    param.setExpression('getNode(%r).getNodeName()' % node.getName())