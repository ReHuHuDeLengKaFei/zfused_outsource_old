# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import sys
import logging

from qtpy import QtGui, QtCore

import zfused_api

__all__ = ["ListFilterProxyModel", "ListModel"]

_logger = logging.getLogger(__name__)


class ListFilterProxyModel(QtCore.QSortFilterProxyModel):
    def __init__(self, parent=None):
        super(ListFilterProxyModel, self).__init__(parent)

        # 状态删选列表
        self._search_text = ""
        self._filter_type_list = []
        self._filter_status_list = []
        self._filter_tag_list = []
        self._filter_object_list = []

    def search(self, text):
        self._search_text = text
        self.invalidateFilter()

    def filter_type(self, type_list=[]):
        self._filter_type_list = type_list
        self.invalidateFilter()

    def filter_status(self, status_list=[]):
        self._filter_status_list = status_list
        self.invalidateFilter()

    def filter_tag(self, tag_list):
        self._filter_tag_list = tag_list
        self.invalidateFilter()

    def filter_object(self, object_list):
        self._filter_object_list = object_list
        self.invalidateFilter()

    def filterAcceptsRow(self, sourceRow, sourceParent):
        assignedTo_index = self.sourceModel().index(sourceRow, 0, sourceParent)
        _data = self.sourceModel().data(assignedTo_index)
        return ( self._search(_data) and \
                 self._filter_status(_data) and \
                 self._filter_type(_data) and \
                 self._filter_tag(_data) and \
                 self._filter_object(_data)
                )

    def filterAcceptsColumn(self, sourceColumn, sourceParent):
        # print self.headerData(0)

        index0 = self.sourceModel().index(0, sourceColumn, sourceParent)
        return True

    def _search(self, data):
        if not self._search_text:
            return True
        # _link_handle = zfused_api.objects.Objects(data["Object"], data["LinkId"])
        # if self._search_text.lower() in data["Name"].lower() or self._search_text.lower() in _link_handle.full_name_code().lower():
        if self._search_text.lower() in data.lower():
            return True
        return False

    def _filter_type(self, data):
        if not self._filter_type_list:
            return True
        # if isinstance(data, zfused_api.task.Task):
        _link_handle = zfused_api.objects.Objects(data["Object"], data["LinkId"])
        if _link_handle.data["TypeId"] in self._filter_type_list:
            return True
        return False

    def _filter_status(self, data):
        if not self._filter_status_list:
            return True
        if data["StatusId"] in self._filter_status_list:
            return True
        return False

    def _filter_tag(self, data):
        if not self._filter_tag_list:
            return True
        _link_handle = zfused_api.objects.Objects(data["Object"], data["LinkId"])
        _tag_ids = _link_handle.tag_ids()
        for _tag_id in _tag_ids:
            if _tag_id in self._filter_tag_list:
                return True
        return False

    def _filter_object(self, data):
        if not self._filter_object_list:
            return True
        # if isinstance(data, zfused_api.task.Task):
        _link_handle = zfused_api.objects.Objects(data["Object"], data["LinkId"])
        if _link_handle.object() in self._filter_object_list:
            return True
        return False

class ListModel(QtCore.QAbstractListModel):
    """
    asset model

    """

    def __init__(self, data=[], parent=None):
        super(ListModel, self).__init__(parent)
        self._items = data

    def rowCount(self, parent = QtCore.QModelIndex()):
        """
        return len asset
        """
        if self._items:
            return len(self._items)
        return 0

    def data(self, index, role=0):
        if not index.isValid() or not 0 <= index.row() < len(self._items):
            return None

        if role == 0:
            return self._items[index.row()]
