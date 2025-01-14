from __future__ import absolute_import

import logging
from collections import OrderedDict

import Utils
from Katana import NodegraphAPI

from .Upgrade import Upgrade
from . import ScriptActions as SA

log = logging.getLogger("PassManagerNode.Node")

class PassManagerNode(NodegraphAPI.SuperTool):
    def __init__(self):
        # Hide group node controls
        self.hideNodegraphGroupControls()
        # Add ports
        self.addInputPort('in')
        self.addOutputPort('out')

        rootParameter = self.getParameters()
        # Hidden version parameter to detect out-of-date
        # internal networks and upgrade it.
        rootParameter.createChildNumber('version', 1)
        rootParameter.createChildString("info", "Press 'Create Network' to build the setup.")
        self.__buildDefaultNetwork()
    
    def __buildDefaultNetwork(self):
        print(self)
        # Create the child nodes
        merge_node = NodegraphAPI.CreateNode('Merge', self)
        location_create_node = NodegraphAPI.CreateNode('LocationCreate', self)
        opscript_node = NodegraphAPI.CreateNode('OpScript', self)
        # Add Parameters to OpScript npde
        root_attr = opscript_node.getParameters()
        user_attr = root_attr.createChildGroup("user")
        render_quality = user_attr.createChildNumber("renderQuality", 0)
        denoise = user_attr.createChildNumber("denoise", 0)
        camera = user_attr.createChildString("camera", '/root/world/cam/camera')
        vis_on = user_attr.createChildString("VisibilityON", '')
        vis_off = user_attr.createChildString("VisibilityOFF", '')
        holdout = user_attr.createChildString("Holdout", '')
        prune = user_attr.createChildString("Prune", '')
        # Set widget hints
        denoise.setHintString("{'widget': 'checkBox', 'constant': True}")
        render_quality.setHintString("{'widget': 'mapper', 'options': {'Low': 0, 'Medium': 1, 'High': 2}, 'constant': True}")
        camera.setHintString("{'widget': 'scenegraphLocation'}")
        vis_on.setHintString("{'widget': 'cel'}")
        vis_off.setHintString("{'widget': 'cel'}")
        holdout.setHintString("{'widget': 'cel'}")
        prune.setHintString("{'widget': 'cel'}")
        
        location_create_node.getParameter('locations.i0').setExpression('="/root/world/passes/" + ~/type')
        location_create_name = location_create_node.getName()
        opscript_node.getParameter('CEL').setExpression(f'={location_create_name}/locations.i0')



        # Connect the nodes
        NodegraphAPI.SetNodePosition(merge_node, (0, -100))
        NodegraphAPI.SetNodePosition(location_create_node, (200,-50))
        NodegraphAPI.SetNodePosition(opscript_node, (0, -150))
        
        # Add input ports to the merge_node
        merge_i0 = merge_node.addInputPort("i0")
        merge_i1 = merge_node.addInputPort("i1")
        
        # Connect parent input to merge_node i0
        self.getSendPort(self.getInputPortByIndex(0).getName()).connect(merge_i0)        
        # Connect location_create_node output to merge_node i1
        location_create_node.getOutputPort('out').connect(merge_i1)
        
        # Connect merge_node output to opscript_node input
        merge_node.getOutputPort('out').connect(opscript_node.getInputPortByIndex(0))
        
        # Connect opscript_node output to parent output port
        self.getReturnPort(self.getOutputPortByIndex(0).getName()).connect(opscript_node.getOutputPortByIndex(0))
    
    def upgrade(self):
        if not self.isLocked():
            Upgrade(self)
        else:
            log.warning('Cannot upgrade locked AttributeWedge node "%s".'
                        % self.getName())