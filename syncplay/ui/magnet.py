from abc import ABC, abstractmethod
from syncplay.utils import find_magnet_from_website

from syncplay.vendor.Qt import QtWidgets
from syncplay.vendor.Qt.QtWidgets import QLineEdit, QLabel, QPlainTextEdit, QPushButton

class MagnetFromWebPage(ABC):
    def __init__(self, parent):
        self.parent = parent

    def openMagnetFromURLDialog(self):
        self.magnetFromURLDialog = QtWidgets.QDialog()
        self.magnetFromURLDialog.resize(800, 700)
        layout = QtWidgets.QGridLayout()
        box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Cancel)
        box.rejected.connect(self.magnetFromURLDialog.reject)
        box.accepted.connect(self.magnetFromURLDialog.accept)
        urlLabel = QLabel('Website URL:')
        self.urlEditor = QLineEdit(self.parent)
        encodingLabel = QLabel('Encodings to try:')
        self.encodingEditor = QLineEdit(self.parent)
        self.encodingEditor.setText('utf-8,windows-1252')
        self.fetchButton = QtWidgets.QPushButton('Fetch magnet from URL')
        self.fetchButton.clicked.connect(self.fetchMagnetClicked)
        self.magnetDisplay = QPlainTextEdit(self.parent)
        self.magnetDisplay.setReadOnly(True)
        magnetDisplayLabel = QLabel('Fetched magnet:')

        self.makeSaveButton()
        box.addButton(self.saveMagnetButton, QtWidgets.QDialogButtonBox.AcceptRole)

        layout.addWidget(urlLabel, 0, 0)
        layout.addWidget(self.urlEditor, 0, 1)
        layout.addWidget(encodingLabel, 1, 0)
        layout.addWidget(self.encodingEditor, 1, 1)
        layout.addWidget(self.fetchButton, 2, 1)
        layout.addWidget(magnetDisplayLabel, 3, 0)
        layout.addWidget(self.magnetDisplay, 3, 1)
        layout.addWidget(box, 4, 0, 1, 2)
        self.magnetFromURLDialog.setLayout(layout)

        self.magnetFromURLDialog.exec()

    def fetchMagnetClicked(self):
        url = self.urlEditor.text()
        encodings = self.encodingEditor.text().split(',')
        if url == '' or encodings == []:
            return
        (self.desc, self.x, self.e) = find_magnet_from_website(url, encodings)
        if self.e is not None:
            msgbox = QtWidgets.QMessageBox(self.parent)
            msgbox.resize(600, 600)
            msgbox.setText(str(self.e))
            msgbox.setIcon(QtWidgets.QMessageBox.Critical)

            if self.desc == 'url':
                msgbox.setInformativeText('\nProbably an error in opening the url')
                msgbox.setDetailedText('Got url: ' + self.x)
            elif self.desc == 'html_bytes':
                msgbox.setInformativeText("\nProbably couldn't parse with given encodings")
                msgbox.setDetailedText('Scraped html in bytes:\n' + str(self.x))
            elif self.desc == 'html':
                msgbox.setInformativeText("\nProbably couldn't find a magnet link in the page")
                msgbox.setDetailedText('Decoded html:\n' + self.x)
            else:
                msgbox.setInformativeText('\nSuper mysterious error')
                msgbox.setDetailedText(self.x)

            bugReportButton = QPushButton('Send a bug report')
            bugReportButton.clicked.connect(self.sendBugReport)
            msgbox.addButton(bugReportButton, QtWidgets.QMessageBox.ActionRole)
            msgbox.setStandardButtons(QtWidgets.QMessageBox.Cancel)

            return msgbox.exec()
        magnet = self.x
        self.magnetDisplay.setPlainText(magnet)
        self.saveMagnetButton.setEnabled(True)

    def sendBugReport(self):
        msgbox = QtWidgets.QDialog(self.parent)
        layout = QtWidgets.QGridLayout()
        label = QLabel(
            'Create a new issue in the issue tracker below and paste in the details'
        )
        link = QLabel(
            'Issue tracker: <a href="https://www.github.com/akazukin5151/syncplay/issues/new/">https://www.github.com/akazukin5151/syncplay/issues/new/</a>'
        )
        details = QPlainTextEdit()
        details.setReadOnly(True)
        details.setPlainText(f'{self.desc=}\n{self.x=}\n{self.e=}')
        layout.addWidget(label)
        layout.addWidget(link)
        layout.addWidget(details)
        msgbox.setLayout(layout)
        box = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok)
        box.accepted.connect(msgbox.accept)
        msgbox.exec()

    @abstractmethod
    def makeSaveButton(self):
        raise NotImplementedError


class MagnetFromWebPageInConfig(MagnetFromWebPage):
    def __init__(self, parent, target_field):
        self.parent = parent
        self.target_field = target_field

    def makeSaveButton(self):
        self.saveMagnetButton = QtWidgets.QPushButton('Use magnet as path to video')
        self.saveMagnetButton.setEnabled(False)
        self.saveMagnetButton.clicked.connect(self.pasteMagnetToField)

    def pasteMagnetToField(self):
        magnet = self.magnetDisplay.toPlainText()
        self.target_field.setText(magnet)


class MagnetFromWebPageInFilesMenu(MagnetFromWebPage):
    def makeSaveButton(self):
        self.saveMagnetButton = QtWidgets.QPushButton('Stream this magnet')
        self.saveMagnetButton.clicked.connect(self.openMagnet)

    def openMagnet(self):
        magnet = self.magnetDisplay.toPlainText()
        # TODO: Freezes for a few seconds, need threads
        if magnet != '':
            self.parent._syncplayClient.openMagnet(magnet, resetPosition=False, fromUser=True)

