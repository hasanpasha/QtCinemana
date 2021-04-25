#!/usr/bin/python

from cinemanaAPI import *

# Import PyQt5
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import * 
from PyQt5.uic import loadUiType

from os import path

from scripts import get_thumb_image, get_poster_image

MAIN_CLASS, _ = loadUiType(path.join(path.dirname(__file__), 'ui/main.ui'))

class MainWidnow(QMainWindow, MAIN_CLASS):
    def __init__(self, parent=None):
        super(MainWidnow, self).__init__(parent)
        QMainWindow.__init__(self)
        self.setupUi(self)

        # Initialize handlers
        self.handleButtons()

        # Items List 
        self.listWidget = QListWidget()
        self.movies_listwidget.itemClicked.connect(self.viewItem)
        self.series_listwidget.itemClicked.connect(self.viewItem)


    def handleButtons(self):
        self.btnsearch.clicked.connect(self.search)
        self.btnhome.clicked.connect(
            lambda: self.stackedWidget.setCurrentIndex(0))


    def search(self):
        if search_kword := self.elsearch.text():
            print("Searching ...")

            current_tab = self.home_tabs.currentIndex()

            types = ['movie', 'series']

            search_resuslt, _ = search(videoTitle=search_kword, type=types[current_tab])

            if search_resuslt:
                self.lstResult(search_resuslt, search=True)
            else:
                print(_)

    def lstResult(self, json_info, search=None):
        current_tab = self.home_tabs.currentIndex()

        if current_tab == 0:
            self.listWidget = self.movies_listwidget
        elif current_tab == 1:
            self.listWidget = self.series_listwidget
        else:
            return

        if search != None:
            self.listWidget.clear()

        self.listWidget.setIconSize(250 * QSize(2, 2))

        # print(json_info[0])

        for i in json_info:
            name = i['en_title']

            name += f"\n({i['year']})"

            # Name
            it = QListWidgetItem(name)

            # Set id number
            it.setData(Qt.UserRole, (i['nb'], i['kind']))

            # Set on hover
            it.setToolTip(i['stars'])

            # Poster
            data = get_thumb_image(i['imgThumbObjUrl'])
            pixmap = QPixmap()
            pixmap.loadFromData(data)

            it.setIcon(QIcon(pixmap))

            # Set Item not selectable
            it.setFlags(it.flags() | ~Qt.ItemIsSelectable)

            self.listWidget.addItem(it)
    
    def viewItem(self, item):
        # print(item.data(Qt.UserRole))
        nb, kind = item.data(Qt.UserRole)
        
        # get info
        info, _ = getInfos(nb)
        if info:
            # print(info)

            # if item is movie
            if kind == '1':
                # Hide episodes list
                self.twepisodes.hide()

            else:
                self.twepisodes.show()

                eps = {}
                seasons = []

                # Add episodes
                episodes_info, _ = getEpisodes(nb)
                if episodes_info:
                    # print(episodes_info)
                    for i in episodes_info:
                        if i[season] not in seasons:
                            eps[f'{i[season]}'] = []
                    for i in episodes_info:
                        eps[f'{i[season]}'].append(i)

                    for s in sorted(seasons):
                        qq = QTreeWidget()
                        qq.add
                        # for i in 
                        
                else:
                    print(_)
                    return


            # Add available Subs
            self.cosubs.clear()
            for i in info['translations']:
                if i['extention'] != 'vtt':
                    self.cosubs.addItem(i['name'])

            # Add available video qualities
            # Get videos data
            videos_data, _ = getVideos(nb)
            if videos_data:
                self.coqual.clear()
                for i in videos_data:
                    self.coqual.addItem(i['resolution'])
            else:
                print(_)
                return


            # Set Poster image
            if data := get_poster_image(info['imgObjUrl']):
                pixmap = QPixmap()
                pixmap.loadFromData(data)
                self.lposter.setPixmap(pixmap.scaled(300, 400, Qt.KeepAspectRatio))

            # Set en Name
            self.lenname.setText(info['en_title'])

            # Set ar name
            if info['ar_title'] != info['en_title']:
                self.larname.show()
                self.larname.setText(info['ar_title'])
            else:
                self.larname.hide()

            # Set year
            self.lyear.setText(f"({info['year']})")

            # Set stars
            self.lstars.setText(info['stars'])

            # Set story
            self.lstory.setText(info['en_content'])

            # set online info link
            self.linfo.setText("<a href='{}'>info</a>" .format(info['imdbUrlRef']))

            # Set categories
            cate = info['categories']
            categories = []
            for i in cate:
                categories.append(i['en_title'])
            self.lcate.setText(' • '.join(categories))
                
            self.stackedWidget.setCurrentIndex(1)

        else:
            print(_)
            return


if __name__ == '__main__':
    app = QApplication([])
    window = MainWidnow()
    window.show()
    app.exec_()
