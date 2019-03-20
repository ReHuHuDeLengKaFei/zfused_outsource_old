#coding:utf-8

import os
import sys
import shutil
import time
import datetime
import json

from pymel.core import *
import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import maya.OpenMayaUI as OpenMayaUI

#import displayHUD
import zfused_api
import zfused_maya.core.record as record
import zfused_maya.tool.animation.playblast_hud as ph
import zfused_maya.core.video as video

def _get_project_path():
    _project_id = record.current_project_id()
    _project_handle = zfused_api.project.Project(_project_id)
    return _project_handle.production_path()

# 
# global path
SETUP_DIR = '{}/setup/'.format(_get_project_path())

def read_json_file(file_path):
    with open(os.path.abspath(file_path), "r") as json_file:
        json_dict = json.load(json_file)
    return json_dict if json_dict else {}
def write_json_file(json_dict, file_path):
    with open(file_path,"w") as json_file:
        json_file.write(json.dumps(json_dict,indent = 4,separators=(',',':')))
        json_file.close()



class PlaybastTool(object):
    def __init__(self):

        tmp_current_time = str(datetime.datetime.now())
        self.date = tmp_current_time.split(' ')[0]
        self.filename = cmds.file(q=True,expandName=True).split('/')[-1]
        self.movPath = ''
        self.originalFilePath = cmds.file(q=True,expandName=True)                  #~ 原始maya文件地址
        #self.LocalFilePath = LocalRootPath + "Backup/"                             #~ 本地拷贝的maya文件的路径，用于lsrunas上传类
        """遍历出服务器maya文件地址"""
        parts = self.originalFilePath.split('/')
        #for i in range(2,len(parts)-1):
        #    ServerRootPath += parts[i]
        #    ServerRootPath += '/'
        #self.ServerBackupPath = ServerRootPath+'Playblast/'+self.date+'/'            #~ 服务器maya文件路径，用于lsrunas上传类
        self.LocalPlayblastPath = self.movPath                                       #~ 本地拍屏文件路径，用于lsrunas上传类
        #self.ServerRootPath = ProjectConfig.ProjectConfig().get('PlayblastEditRoot', #~ 服务器剪辑目录路径，用于lsrunas上传类
        #                                                        default='//hnas01/Data/Edit/%s/AutoImport/'%Prj)
    
    def show(self):
        Window = 'SaveAsTool'
        if cmds.window(Window,exists = True) == True:
            cmds.deleteUI(Window,window = True)
        if cmds.windowPref(Window,exists = True) == True:
            cmds.windowPref(Window,remove = True)
        cmds.window(Window,sizeable = False,title = 'Playblast Tool')
        ColumnLayout = cmds.columnLayout(parent = Window,adjustableColumn = True)
        cmds.text(label='Playbast Tools',height=30, backgroundColor=[0.5, 0.5, 0.6])
        cmds.separator(style='out')
        cmds.frameLayout(label='Description :', collapsable=True, collapse=True,width=410)
        cmds.columnLayout(adjustableColumn=True)
        cmds.scrollField('descriptionScrollField',height=100,wordWrap=True)
        cmds.separator(style='in')
        cmds.setParent('..')
        cmds.setParent('..')
        cmds.rowColumnLayout( numberOfColumns=3, columnWidth=[(1, 50),(2,310),(3,50)])
        ShotT = cmds.text(height = 24,label = 'Mov Path:')
        ShotTF = cmds.textField(height = 24)
        browseB = cmds.button(height = 24,label = 'Browse',command = lambda *args: self.ChooseFolder())
        cmds.setParent('..')
        cmds.columnLayout(adjustableColumn=True)
        qualitySlider = cmds.intSliderGrp( field=True, label='Quality', value=50 )
        ScaleSlider = cmds.floatSliderGrp( label='Scale', field=True, minValue=0.10, maxValue=1.00, fieldMinValue=0.10, fieldMaxValue=1.00, value=0.50,precision=2 )
        
        cmds.columnLayout(adjustableColumn=True)
        cmds.rowColumnLayout( numberOfColumns = 2, columnWidth = [(1, 100),(2,300)])
        file_name_text = cmds.text(height = 24,label = u'屏显文件名:')
        file_name_textField = cmds.textField(height = 24)
        cmds.setParent('..')
        cmds.columnLayout(adjustableColumn=True)
        cmds.rowColumnLayout( numberOfColumns = 2, columnWidth = [(1, 20),(2,300)])
        cmds.text(height = 24,label = '  ')
        approved_checkBox = cmds.checkBox(height = 24,label = u'已经通过', changeCommand = self.showHUD)
        cmds.setParent('..')

        playB = cmds.button(height = 32,label = 'Playblast',command = lambda *args: self.Playblastfunction())
        #openB = cmds.button(height = 32,label = 'Open Mov',command = lambda *args: self.openMov())
        #uploadB = cmds.button(height = 32,label = 'Upload Mov',command = lambda *args: self.uploadTheFile())
        cmds.setParent('..')
        cmds.separator(style='in')
        cmds.text(label=' ')

        self.ShotTF = ShotTF
        self.qualitySlider = qualitySlider
        self.ScaleSlider = ScaleSlider
        self.file_name_textField = file_name_textField
        self.approved_checkBox = approved_checkBox

        self.playB = playB
        #self.uploadB = uploadB
        #self.openB = openB
        cmds.showWindow(Window)
        self.SetDefaultFolder()
        #self.setOpenB()
        #self.setUploadB(False)

        # print ph.HUD._get_namewithversion()
        _name = self._get_file_name()

        playblast_setup_path = SETUP_DIR + 'MAYA_PLAYBLAST.json'
        playblast_setup_dict = read_json_file(playblast_setup_path)
        qualitySlider_value = playblast_setup_dict['quality']
        ScaleSlider_value   = playblast_setup_dict['scale']
        cmds.intSliderGrp(self.qualitySlider, edit = True, value = qualitySlider_value)
        cmds.floatSliderGrp(self.ScaleSlider, edit = True, value = ScaleSlider_value)
        cmds.textField(self.file_name_textField, edit = True, text = _name, textChangedCommand = self.showHUD)

        self.showHUD()

    def _get_file_name(self):
        _file = cmds.file(q = True, sn = True)
        if _file:
            _name = os.path.basename(os.path.splitext(_file)[0])
            return _name
        return ""

    def SetDefaultFolder(self):
        ShotTF = self.ShotTF
        Folder = os.path.split(sceneName())[0]
        #Folder = cmds.workspace(query = True, directory = True)
        cmds.textField(ShotTF,edit = True,text = Folder)

    def ChooseFolder(self):
        ShotTF = self.ShotTF
        StartFolder = cmds.workspace(query = True, directory = True)
        Folder = cmds.fileDialog2( dialogStyle=2, startingDirectory = StartFolder,fileMode=3)
        if not Folder == None:
            cmds.textField(ShotTF,edit = True,text = Folder[0])

    def GetFolder(self):
        ShotTF = self.ShotTF
        Folder = cmds.textField(ShotTF,query = True,text = True)
        if Folder[-1] == '/':
            return Folder
        else:
            return (Folder+'/')

    def GetQuality(self):
        qualitySlider = self.qualitySlider
        quality = cmds.intSliderGrp(qualitySlider,q=1,value=1)
        return quality

    def GetScale(self):
        ScaleSlider = self.ScaleSlider
        scale = cmds.floatSliderGrp(ScaleSlider,q=1,value=1)
        return scale

    '''
    def setOpenB(self):
        openB = self.openB
        if self.movPath == '':
            cmds.button(openB,edit=1,enable=0)
        else:
            cmds.button(openB,edit=1,enable=1)
    def setUploadB(self,flag):
        uploadB = self.uploadB
        cmds.button(uploadB,enable=flag,edit=True)
    '''
    def GetCurrentCam(self):
        view = OpenMayaUI.M3dView.active3dView()
        camDag = OpenMaya.MDagPath()
        view.getCamera(camDag)
        return camDag.fullPathName()

    def openMov(self):
        movPath = self.movPath
        print movPath
        os.system(movPath)

    def Playblastfunction(self):
        self.showHUD()
        folder = self.GetFolder()
        qualityNum = self.GetQuality()
        scale = self.GetScale()
        camShape = self.GetCurrentCam().split('|')[-1]
        camTrans = cmds.listRelatives( camShape,parent=1)[0].replace(':','_')
        judgeArg = cmds.camera(camShape,q=1,overscan=1)

        #set camera overscan
        #import Mili.Module.utilties.ProjectConfig as ProjectConfig
        #reload(ProjectConfig)
        #config = ProjectConfig.ProjectConfig()

        #cameraSetting = {'overscan':1, 'displayResolution':0, 'displayFilmGate':1, 'displayGateMask':1}
        cam_setup_path = SETUP_DIR + 'MAYA_CAM.json'
        cam_setup_dict = read_json_file(cam_setup_path)
        cam_save_dict = {}
        for _attr, _value in cam_setup_dict.items():
            cam_save_dict[_attr] = getAttr(camShape + '.' + _attr)
            setAttr(camShape + '.' + _attr, _value)

        # cameraSetting = cam_setup_dict
        # #cameraSetting = eval(cameraSetting)
        # setAttr(camShape + '.filmFit', cameraSetting["filmFit"])
        # cmds.camera(camShape,edit=1,displayResolution=cameraSetting["displayResolution"])
        # cmds.camera(camShape,edit=1,displayGateMask=cameraSetting["displayGateMask"])
        # setAttr(camShape + '.displayGateMaskOpacity', cameraSetting["displayGateMaskOpacity"])
        # setAttr(camShape + '.displayGateMaskColor', cameraSetting["displayGateMaskColor"])
        # cmds.camera(camShape,edit=1,displaySafeAction=cameraSetting["displaySafeAction"])
        # cmds.camera(camShape,edit=1,overscan=cameraSetting["overscan"])
        
        #cmds.camera(camShape,edit=1,displayFilmGate=cameraSetting["displayFilmGate"])
        

        #mc.setAttr(activeCam()+'.displayResolution',cameraSetting["displayResolution"])
        #mc.setAttr(activeCam()+'.displayFilmGate',cameraSetting["displayFilmGate"])
        #mc.setAttr(activeCam()+'.displayGateMask',cameraSetting["displayGateMask"])
        playblast_setup_path = SETUP_DIR + 'MAYA_PLAYBLAST.json'
        playblast_setup_dict = read_json_file(playblast_setup_path)
        format = playblast_setup_dict['format']
        compression = playblast_setup_dict['compression']
        width = playblast_setup_dict['width']
        height = playblast_setup_dict['height']

        # get current file name
        _file_name = cmds.file(q = True, sn = True, shn = True)
        _file_name = os.path.splitext(_file_name)[0]

        # compression = u'IYUV 编码解码器'
        sound = None
        import maya.mel as mm
        aPlayBackSliderPython = mm.eval('$temVar=$gPlayBackSlider')
        if aPlayBackSliderPython:
            sound = cmds.timeControl(aPlayBackSliderPython, q = True, sound = True)
        if sound:
            movPath = cmds.playblast(format = format, filename = folder + _file_name + '.' + format, sound = sound, forceOverwrite = 1,sequenceTime=0,clearCache=1,viewer=0,showOrnaments=1,offScreen=1,fp=4,percent =scale*100, compression=compression,quality=qualityNum,w=width,h=height)
        else:
            movPath = cmds.playblast(format = format, filename = folder + _file_name + '.' + format,                forceOverwrite = 1,sequenceTime=0,clearCache=1,viewer=0,showOrnaments=1,offScreen=1,fp=4,percent =scale*100, compression=compression,quality=qualityNum,w=width,h=height)
        
        # cmds.playblast(format='avi',clearCache=1,viewer=0,showOrnaments=1,offScreen = 1,
        #                             startTime = timeline[0], 
        #                             endTime = timeline[1],
        #                             percent=100,
        #                             widthHeight=self.resolutionSize,
        #                             quality=100,
        #                             compression=codec,
        #                             filename = vidDir+'/playblast.avi',
        #     #                        compression='none',
        #     #                        compression='MS-CRAM',
        #                             )

        #self.setUploadB(True)
        if judgeArg == 1.3 :
            cmds.camera(camShape,edit=1,overscan=1.3)
        self.movPath = movPath
        #self.setOpenB()
        self.LocalPlayblastPath = folder      #~ 拍屏文件本地路径
        self.playblastFile = camTrans + '.avi'  #~ 拍屏文件名称
        # self.playblastFile = "{}.avi".format(_file_name)
        #self.openMov() #~ 播放截屏
        #self.uploadTheFile() #~ 上传文件
        convert_format = '.mov'
        convert_path = os.path.splitext(movPath)[0] + convert_format
        if video.convert_video(movPath, convert_path) == True:
            # os.remove(movPath)
            pass

        # 恢复状态
        self.hideHUD()
        for _attr, _value in cam_save_dict.items():
            setAttr(camShape + '.' + _attr, _value)

    def get_ui_filename(self):
        _name = cmds.textField(self.file_name_textField, query = True, text = True)
        return _name

    def showHUD(self,*args):
        # description = cmds.scrollField('descriptionScrollField',text=True,q=True)
        # try:
        #     key = self.filename.split('_')[2]
        # except IndexError:
        #     key = None
        # if key == 'lay':
        #     type = 'Layout'
        # elif key == 'blocking':
        #     type = 'Blocking'
        # elif key == 'ani':
        #     type = 'Animation'
        # else:
        #     type = 'None'
        # #import animHUD

        #屏显
        _name = cmds.textField(self.file_name_textField, query = True, text = True)
        _approved = cmds.checkBox(self.approved_checkBox, query = True,value = True)

        _v = ph.HUD(ph.get_maya_hud(), _name, _approved)
        _v._remove()
        _v._show()
        

        # pl = displayHUD.HUD()
        # #pl.setDescription(description)
        # #pl.setAniType("Animation")
        # pl.AnimationHUD()
        # #pl.RefreshInfo()

    def hideHUD(self,*args):
        _v = ph.HUD(ph.get_maya_hud())
        _v._remove()
        _v._restore_defalut()
