# coding:utf-8
# --author-- binglu.wang
from __future__ import print_function

import os
import json
import logging

import maya.cmds as cmds

import zfused_api
import zfused_maya.node.core.element as element
import zfused_maya.node.core.alembiccache as alembiccache

__all__ = ["import_cache"]
logger = logging.getLogger(__name__)

# load abc plugin
_is_load = cmds.pluginInfo("AbcImport", query=True, loaded = True)
if not _is_load:
    try:
        logger.info("try load AbcImport plugin")
        cmds.loadPlugin("AbcImport")
    except Exception as e:
        logger.error(e)
        sys.exit()

def get_cache_info(cache_file):
    '''load json info
    '''
    with open(cache_file, 'r') as info:
        dataInfo = json.load(info)
        info.close()
    return dataInfo

def load_asset(cacheinfo,step,_dict = {}):
    _interpath = "maya2017/file"
    def get_assets():
        import zfused_maya.core.record as record
        _assets = {}
        _project_id = record.current_project_id()
        _project_assets = zfused_api.asset.project_assets([_project_id])
        # print _project_assets
        for _asset in _project_assets:
            asset = zfused_api.asset.Asset(_asset["Id"])
            _assets[asset.code()] =asset.production_path()
        return _assets

    _assets = get_assets()
    for item in cacheinfo:
        _assetname = item[0]
        if _assetname in _assets:
            if _assetname in _dict:
                _dict[_assetname]["namespace"].append(item[1])
            else:
                _dict[_assetname] = {}
                _dict[_assetname]["namespace"] = [item[1]]
                _production_path = "/".join([_assets[_assetname],step,_interpath])
                _dict[_assetname]["path"] = "{}/{}.mb".format(_production_path,_assetname)
            cmds.file(_dict[_assetname]["path"],r = 1,iv = 1,mergeNamespacesOnClash = 1,ns = item[1])
    return _dict



def import_cache(output_link_object, output_link_id,  output_attr_id, input_link_object, input_link_id, input_attr_id):
    '''import alembic cache
    '''

    _file_title = "shader/redshift"

    _output_attr_handle = zfused_api.outputattr.OutputAttr(output_attr_id)
    _project_step_id = _output_attr_handle.data["ProjectStepId"]
    _project_step_handle = zfused_api.step.ProjectStep(_project_step_id)
    _step_code = _project_step_handle.code()
    _software_code = zfused_api.software.Software(_project_step_handle.data["SoftwareId"]).code()

    _output_link_handle = zfused_api.objects.Objects(output_link_object, output_link_id)
    _output_link_production_path = _output_link_handle.production_path()
    _output_link_publish_path = _output_link_handle.publish_path()
    _file_code = _output_link_handle.file_code()
    _suffix = _output_attr_handle.suffix()
    _attr_code = _output_attr_handle.code()
    _output_link_production_file = "{}/{}/{}/{}/{}{}".format( _output_link_production_path, _step_code, _software_code, _attr_code, _file_code, _suffix )

    print( _output_link_production_file )
    # # input task
    # _input_task_id = argv_task_id
    # _input_task_handle = zfused_api.task.Task(_input_task_id)
    # # get shot frame
    # _link_handle = zfused_api.objects.Objects(_input_task_handle.data["Object"], _input_task_handle.data["LinkId"])
    # _start_frame = _link_handle.start_frame()
    # _end_frame = _link_handle.end_frame()
    # cmds.playbackOptions(min = _start_frame, max = _end_frame)
    # # get shot version
    # _input_production_path = _input_task_handle.production_path()
    # _version_id = _input_task_handle.last_version_id()
    # if not _version_id:
    #     return
    # # get json path
    # _version_handle = zfused_api.version.Version(_version_id)
    # _outputattr_handle = zfused_api.outputattr.OutputAttr(argv_attr_id)
    # _attr_file = "{}/{}/{}{}".format(_input_production_path, argv_attr_code, _version_handle.data["Name"], _outputattr_handle.data["Suffix"])
    # if not os.path.exists(_attr_file):
    #     return False
    
    # get shot info
    # _elements = element.scene_elements()
    # _asset_dict = element.get_asset(_elements,_file_title)

    _info = get_cache_info( _output_link_production_file )
    if not _info:
        return
    _asset_dict = load_asset(_info,_file_title)
    if not _asset_dict:
        return

    # merge alembic cache
    for item in _info:
        _asset,_ns,_node,_path = item
        try:
            if _asset and _asset in _asset_dict and _asset_dict[_asset]["namespace"]:
                _tex_ns = _asset_dict[_asset]["namespace"][0]
                # ======================================================================================
                # 领取重复参考的模型,弃用
                # if _asset and _asset in _asset_dict and _ns not in _asset_dict[_asset]["namespace"]:
                #     _assetpath = _asset_dict[_asset]["path"]
                #     cmds.file(_assetpath,r = 1,iv = 1,mergeNamespacesOnClash = 1,ns = _ns)
                #     _asset_dict[_asset]["namespace"].append(_ns)
                # ======================================================================================
                logger.info("load asset:{}".format(_path))
                alembiccache.import_cache(_asset,_ns,_node,_path,"{}:{}".format(_tex_ns,_node))
                _asset_dict[_asset]["namespace"].pop(0)
            else:
                logger.info("load camera:{}".format(_path))
                _log = alembiccache.import_cache(_asset,_ns,_node,_path)
        except:
            logger.warning("wrong load cache:{}".format(_path))
    return True

if __name__ == '__main__':
    import_cache()
