#include "core.h"

#include <mainwindow.h>
#include <viewport.h>

#include <sys/stat.h>
#include <unistd.h>
#include <iostream>
#include <fstream>
#include <wup/wup.hpp>

#include <QApplication>

const char * named_pipe = "/tmp/shadow_xppen_deco_pro";

using wup::print;

void
readCommands(Core * c)
{
    mkfifo(named_pipe, 0666);

    std::string cmd;

    while (true)
    {
        print("Opening pipe at", named_pipe);
        std::ifstream ifs(named_pipe);
        print("Pipe opened", named_pipe);
        ifs >> cmd;
        print("Got cmd: ", cmd);

        if (cmd == "draw") {
            int x1, y1, x2, y2;
            ifs >> x1 >> y1 >> x2 >> y2;
            QMetaObject::invokeMethod(c, "draw", Qt::AutoConnection, Q_ARG(int, x1), Q_ARG(int, y1), Q_ARG(int, x2), Q_ARG(int, y2));
        }

        else if (cmd == "erase") {
            int x1, y1, x2, y2;
            ifs >> x1 >> y1 >> x2 >> y2;
            QMetaObject::invokeMethod(c, "erase", Qt::AutoConnection, Q_ARG(int, x1), Q_ARG(int, y1), Q_ARG(int, x2), Q_ARG(int, y2));
        }

        else if (cmd == "move_page") {
            int rx, ry;
            ifs >> rx >> ry;
            QMetaObject::invokeMethod(c, "movePage", Qt::AutoConnection, Q_ARG(int, rx), Q_ARG(int, ry));
        }

        else if (cmd == "change_brush_size") {
            int size;
            ifs >> size;
            QMetaObject::invokeMethod(c, "changeBrushSize", Qt::AutoConnection, Q_ARG(int, size));
        }

        else if (cmd == "change_eraser_size") {
            int size;
            ifs >> size;
            QMetaObject::invokeMethod(c, "changeEraserSize", Qt::AutoConnection, Q_ARG(int, size));
        }

        else if (cmd == "set_page_mode") {
            int pageMode;
            ifs >> pageMode;
            QMetaObject::invokeMethod(c, "setPageMode", Qt::AutoConnection, Q_ARG(int, pageMode));
        }

        else if (cmd == "show_previous_page")
            QMetaObject::invokeMethod(c, "showPreviousPage", Qt::AutoConnection);

        else if (cmd == "show_next_page")
            QMetaObject::invokeMethod(c, "showNextPage", Qt::AutoConnection);

        else
            std::cout << "Unknown command:" << cmd << std::endl;
    }

    unlink(named_pipe);
}


Core::Core(QObject *parent)
    : QObject{parent},
      pageMode(PageMode::MODE_TRANSPARENT),
      transparentBook(this, false),
      opaqueBook(this, true),
      activeBook(&transparentBook),
      reader(readCommands, this),
      size_brush_index(5),
      size_eraser_index(5),
      size_brush(pow(BRUSH_BASE, size_brush_index)),
      size_eraser(pow(ERASER_BASE, size_eraser_index)),
      brush_color(QColor("#0000ff")),
      width_space(0),
      height_space(0)
{

    QList<QScreen*> screens = QGuiApplication::screens();

    for (int i=0;i!=screens.size();++i) {
        auto screen = screens[i];
        auto g = screen->geometry();

        Viewport * viewport = new Viewport(screen);
        viewport->setPage(activeBook->currentPage());
        viewports.append(viewport);

        width_space = std::max(g.right(), width_space);
        height_space = std::max(g.bottom(), height_space);
//        break;
    }

    wup::print("space", width_space, height_space);
    wup::print("sizes", size_brush, size_eraser);
}

void Core::onPageChanged(Book *, Page *page)
{
    for (Viewport * viewport : viewports)
        viewport->setPage(page);
}

void Core::onRepaintPage(Book *, Page *)
{
    for (Viewport * viewport : viewports)
        viewport->update();
}

void Core::changeBrushSize(int size)
{
    size_brush_index += size;
    size_brush_index = std::min(size_brush_index, MAX_BRUSH_INDEX);
    size_brush_index = std::max(size_brush_index, MIN_BRUSH_INDEX);
    size_brush = int(pow(BRUSH_BASE, size_brush_index));
}

void Core::changeEraserSize(int size)
{
    size_eraser_index += size;
    size_eraser_index = std::min(size_eraser_index, MAX_BRUSH_INDEX);
    size_eraser_index = std::max(size_eraser_index, MIN_BRUSH_INDEX);
    size_eraser = int(pow(ERASER_BASE, size_eraser_index));
}

void Core::showPreviousPage()
{
    activeBook->showPreviousPage();
}

void Core::showNextPage()
{
    activeBook->showNextPage();
}

void Core::setPageMode(int iPageMode)
{
    PageMode pageMode = PageMode(iPageMode);

    if (this->pageMode == pageMode)
        return;

    this->pageMode = pageMode;

    switch (pageMode) {
    case MODE_TRANSPARENT:
        print("transparent");
        activeBook = &transparentBook;
        activeBook->setVisible(true);
        break;
    case MODE_OPAQUE:
        print("opaque");
        activeBook = &opaqueBook;
        activeBook->setVisible(true);
        break;
    case MODE_PASSTHROUGH:
        print("through");
        activeBook = &transparentBook;
        activeBook->setVisible(true);
        break;
    case MODE_DISABLED:
        print("disabled");
        activeBook = &transparentBook;
        activeBook->setVisible(false);
        break;
    }

}

void Core::movePage(int rx, int ry) {
    activeBook->movePage(rx, ry);
}

void Core::draw(int x1, int y1, int x2, int y2) {
    x1 = (x1 * width_space) / 32767;
    x2 = (x2 * width_space) / 32767;

    y1 = (y1 * height_space) / 32767;
    y2 = (y2 * height_space) / 32767;

    for (Viewport * viewport : viewports)
        viewport->draw(x1, y1, x2, y2, size_brush, brush_color);
}

void Core::erase(int x1, int y1, int x2, int y2) {
    x1 = (x1 * width_space) / 32767;
    x2 = (x2 * width_space) / 32767;

    y1 = (y1 * height_space) / 32767;
    y2 = (y2 * height_space) / 32767;

    for (Viewport * viewport : viewports)
        viewport->erase(x1, y1, x2, y2, size_brush);
}

