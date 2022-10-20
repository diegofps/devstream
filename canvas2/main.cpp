#include "mainwindow.h"

#include <QApplication>
#include <wup/wup.hpp>
#include <core.h>

using namespace wup;

WUP_STATICS;

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);
    Core core;

    return a.exec();
}
