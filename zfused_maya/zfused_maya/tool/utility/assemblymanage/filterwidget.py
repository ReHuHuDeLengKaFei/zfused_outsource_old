# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import sys
import os
import logging

from qtpy import QtWidgets, QtGui, QtCore

import zfused_api
import zfused_maya.core.record as record
import zfused_maya.core.resource as resource

__all__ = ["FilterWidget"]

logger = logging.getLogger(__name__)


class FilterWidget(QtWidgets.QFrame):
    asset_type_changed = QtCore.Signal(list)
    def __init__(self, parent=None):
        super(FilterWidget, self).__init__(parent)
        self._build()

        self._type_name_id_dict = {}
        self._type_checkboxs = []

        self._load()


    def load_project_id(self, project_id):
        """ 加载项目资产类型和任务步骤
        
        :rtype: None
        """
        pass

    def _asset_type_ids(self):
        _type_ids = []
        for _checkbox in self._type_checkboxs:
            if _checkbox.isChecked():
                _type_ids.append(self._type_name_id_dict[_checkbox.text()])
        self.asset_type_changed.emit(_type_ids)


    def _load(self):
        # clear asset type item
        self._clear()
        # get current project id
        _project_id = record.current_project_id()
        if not _project_id:
            return
        # asset type
        _project_handle = zfused_api.project.Project(_project_id)
        _asset_type_ids = _project_handle.asset_type_ids()
        if _asset_type_ids:
            for _asset_type_id in _asset_type_ids:
                _asset_type_handle = zfused_api.types.Types(_asset_type_id)
                _name = _asset_type_handle.name_code()
                self._type_name_id_dict[_name] = _asset_type_id
                _name_checkbox = QtWidgets.QCheckBox()
                _name_checkbox.setText(_name)
                self.filter_type_checkbox_layout.addWidget(_name_checkbox)
                self._type_checkboxs.append(_name_checkbox)
                _name_checkbox.stateChanged.connect(self._asset_type_ids)

    def _clear(self):
        """清除资产类型和任务步骤
        
        :rtype: None
        """
        # 清除资产类型
        self._type_name_id_dict = {}
        self._type_checkboxs = []
        _childrens = self.filter_type_widget.findChildren(QtWidgets.QCheckBox)
        if not _childrens:
            return
        for _child in _childrens:
            self.filter_type_checkbox_layout.removeWidget(_child)
            _child.deleteLater()

        # 清除任务步骤
        self._step_name_id_dict = {}
        self._step_checkboxs = []


    def _build(self):
        self.setMaximumWidth(200)
        _layout = QtWidgets.QVBoxLayout(self)
        _layout.setSpacing(0)
        _layout.setContentsMargins(0,0,0,0)

        # filter type widget
        self.filter_type_widget = QtWidgets.QFrame()
        self.filter_type_layout = QtWidgets.QVBoxLayout(self.filter_type_widget)
        self.filter_type_layout.setSpacing(0)
        self.filter_type_layout.setContentsMargins(0,0,0,0)
        #  title button
        self.filter_type_name_button = QtWidgets.QPushButton()
        self.filter_type_name_button.setMaximumHeight(25)
        self.filter_type_name_button.setText(u"资产类型检索")
        self.filter_type_name_button.setIcon(QtGui.QIcon(resource.get("icons","filter.png")))
        self.filter_type_layout.addWidget(self.filter_type_name_button)
        #  type widget
        self.filter_type_checkbox_widget = QtWidgets.QFrame()
        self.filter_type_layout.addWidget(self.filter_type_checkbox_widget)
        self.filter_type_checkbox_layout = QtWidgets.QVBoxLayout(self.filter_type_checkbox_widget)
        self.filter_type_checkbox_layout.setContentsMargins(20,0,0,0)

        _layout.addWidget(self.filter_type_widget)
        
        _layout.addStretch(True)

        _qss = resource.get("qss", "tool/assemblymanage/filter.qss")
        with open(_qss) as f:
            qss = f.read()
            self.setStyleSheet(qss)