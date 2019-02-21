# coding:utf-8
# --author-- lanhua.zhou

""" zfused maya 清除机制 """

from __future__ import print_function

import maya.cmds as cmds

import logging

logger = logging.getLogger(__name__)

def unknown_plugins():
    """ clear unknown plugins

    """
    oldplugins = cmds.unknownPlugin(q=True, list=True)
    if not oldplugins:
        return
    for plugin in oldplugins:
        try:
            cmds.unknownPlugin(plugin, remove=True)
        except:
            pass

def animation_layer():
    """ clear animation layer

    """
    _lays = cmds.ls(type = "animLayer")
    if _lays:
        for _lay in _lays:
            cmds.delete(_lay)

def unknown_node():
    allNodes = cmds.ls(type = "unknown")
    if allNodes:
        for node in allNodes:
            try:
                cmds.lockNode(node, lock = False)
                cmds.delete(node)
            except Exception as e:
                logger.warning(e)

def camera():
    """ clear camera

    """
    allCameras = cmds.ls(type = "camera")
    initCameras = list(set(allCameras) - set(["frontShape","topShape","perspShape","sideShape"]))
    if initCameras:
        for camera in initCameras:
            cameraTrans = cmds.listRelatives(camera, parent = True)
            try:
                cmds.lockNode(cameraTrans, lock = False)
                cmds.delete(cameraTrans)
            except Exception as e:
                logger.warning(e)

def light():
    """ clear light

    """
    _lights = cmds.ls(type = cmds.listNodeTypes("light"))
    
    if _lights:
        for _light in _lights:
            try:
                #if cmds.objExists(_light):
                if cmds.referenceQuery(_light,isNodeReferenced = True) == False:
                    par = cmds.listRelatives(_light, p = True)
                    cmds.delete(par)
            except Exception as e:
                logger.warning(e)

def anim_curve():
    """ clear animation curve

    """
    NodeList = cmds.ls(type = 'animCurve')
    if NodeList:
        for NodeName in NodeList:
            if cmds.referenceQuery(NodeName,isNodeReferenced = True) == False:
                cmds.delete(NodeName)

def display_layer():
    """ clear diaplay layers

    """
    import pymel.core as core
    DisplayLayer = [Layer for Layer in core.ls(type = 'displayLayer') if not core.referenceQuery(Layer,isNodeReferenced = True) and Layer.name() != 'defaultLayer' and cmds.getAttr("%s.identification"%Layer) != 0]
    if DisplayLayer:
        for Layer in DisplayLayer:
            Layer.attr('drawInfo').disconnect()
            Layer.unlock()
            core.delete(Layer)

def render_layer():
    """ clear render layers

    """
    import pymel.core as core
    RenderLayer = [Layer for Layer in core.ls(type = 'renderLayer') if not core.referenceQuery(Layer,isNodeReferenced = True) and Layer.name() != 'defaultRenderLayer']
    if RenderLayer:
        for Layer in RenderLayer:
            #Layer.attr('drawInfo').disconnect()
            Layer.unlock()
            core.delete(Layer)

def namespace():
    """ clear namespace
    
    """
    NamespaceList = cmds.namespaceInfo(recurse = True,listOnlyNamespaces = True)
    if NamespaceList:
        NamespaceList.reverse()
        for NamespaceName in NamespaceList:
            if NamespaceName != 'shared' and NamespaceName != 'UI':
                cmds.namespace(setNamespace = NamespaceName)
                NamespaceList = cmds.namespaceInfo(recurse = True,listOnlyNamespaces = True)
                NodeList = cmds.namespaceInfo(listOnlyDependencyNodes = True,dagPath = True)
                ParentNamespace = cmds.namespaceInfo(parent = True)
                cmds.namespace(setNamespace = ':')
                if NamespaceList == None:
                    if NodeList == None:
                        try:
                            cmds.namespace(removeNamespace = NamespaceName)
                        except Exception as e:
                            logger.warning(e)
                    else:
                        IsNodeReferenced = False
                        for NodeName in NodeList:
                            if cmds.referenceQuery(NodeName,isNodeReferenced = True) == True:
                                IsNodeReferenced = True
                                break
                        if IsNodeReferenced == False:
                            try:
                                cmds.namespace(force = True,moveNamespace = (NamespaceName,ParentNamespace))
                                cmds.namespace(removeNamespace = NamespaceName)
                            except Exception as e:
                                logger.warning(e)

def reference():
    _refnode = cmds.ls(typ="reference")
    for _i in _refnode:
        _getlinknode = cmds.listConnections(_i)
        if _getlinknode == None:
            cmds.lockNode(_i,l=0)
            cmds.delete(_i)
            #print ("deleted referenceNode: "+_i)