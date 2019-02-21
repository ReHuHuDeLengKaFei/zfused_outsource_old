# coding:utf-8
# --author-- lanhua.zhou
from __future__ import print_function

import sys
import os

from qtpy import QtWidgets, QtGui, QtCore

__all__ = ["LineEdit"]


class LineEdit(QtWidgets.QLineEdit):
    def __init__(self, parent=None):
        super(LineEdit, self).__init__(parent)
        self.setStyleSheet("QLineEdit{font-family:Microsoft YaHei UI;font: bold 12px;color:#66686A}"
                           "QLineEdit{border:0px solid; border-bottom:1px solid}")
        self._tip = "info"
        self._is_inputmethod = False

        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if QtCore.QEvent.KeyPress == event.type():
            self._is_inputmethod = False
        elif QtCore.QEvent.InputMethod == event.type():
            self._is_inputmethod = True
        return super(LineEdit, self).eventFilter(obj, event)

    def tip(self):
        return self._tip()

    def set_tip(self, tip):
        self._tip = tip

    def paintEvent(self, event):
        super(LineEdit, self).paintEvent(event)
        _rect = self.rect()
        _painter = QtGui.QPainter(self)
        _painter.save()
        _painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        if not self.text() and not self._is_inputmethod:
            _painter.drawText(QtCore.QRect(_rect.x() + 5, _rect.y(), _rect.width() - 5,
                                           _rect.height()), QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter, self._tip)
        _painter.restore()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ui = LineEdit()
    ui.show()
    ui.set_tip(u"用户名")
    sys.exit(app.exec_())
