QT       += core gui openglwidgets

greaterThan(QT_MAJOR_VERSION, 4): QT += widgets

CONFIG += c++17

INCLUDEPATH += ../../wup/cpp/include
DEFINES += WUP_NO_OPENCV WUP_NO_MPICH

# You can make your code fail to compile if it uses deprecated APIs.
# In order to do so, uncomment the following line.
#DEFINES += QT_DISABLE_DEPRECATED_BEFORE=0x060000    # disables all the APIs deprecated before Qt 6.0.0

SOURCES += \
    book.cpp \
    canvaswidget.cpp \
    core.cpp \
    main.cpp \
    page.cpp \
    viewport.cpp

HEADERS += \
    book.h \
    canvaswidget.h \
    core.h \
    page.h \
    viewport.h

FORMS += \
    viewport.ui

# Default rules for deployment.
qnx: target.path = /tmp/$${TARGET}/bin
else: unix:!android: target.path = /opt/$${TARGET}/bin
!isEmpty(target.path): INSTALLS += target
