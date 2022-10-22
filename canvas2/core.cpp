#include "core.h"

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
    std::string cmd;
    std::ifstream ifs(named_pipe);

    while (true)
    {
        if (!(ifs >> cmd)) {
            print("Error during cmd read");
            sleep(1);
            continue;
        }

        print("Got cmd: ", cmd);

        if (cmd == "draw") {
            int x1, y1, x2, y2;
            if (ifs >> x1 >> y1 >> x2 >> y2)
                c->draw(x1,y1,x2,y2);
        }

        else if (cmd == "erase") {
            int x1, y1, x2, y2;
            if (ifs >> x1 >> y1 >> x2 >> y2)
                 c->erase(x1,y1,x2,y2);
        }

        else if (cmd == "move_page") {
            int rx, ry;
            if (ifs >> rx >> ry)
                c->movePage(rx,ry);
        }

        else if (cmd == "change_brush_size") {
            int size;
            if (ifs >> size)
                c->changeBrushSize(size);
        }

        else if (cmd == "change_eraser_size") {
            int size;
            if (ifs >> size)
                c->changeEraserSize(size);
        }

        else if (cmd == "set_page_mode") {
            int pageMode;
            if (ifs >> pageMode)
                c->setPageMode(pageMode);
        }

        else if (cmd == "show_previous_page") {
            c->showPreviousPage();
        }

        else if (cmd == "show_next_page") {
            c->showNextPage();
        }

        else if (cmd == "") {
            sleep(1);
        }

        else {
            std::cout << "Unknown command:" << cmd << std::endl;
        }
    }

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
        viewport->setBook(activeBook);
        viewports.append(viewport);

        width_space = std::max(g.right(), width_space);
        height_space = std::max(g.bottom(), height_space);
//        break;
    }

    wup::print("space", width_space, height_space);
    wup::print("sizes", size_brush, size_eraser);
}

void Core::onPageChanged(Book *book, Page *)
{
    for (Viewport * viewport : viewports)
        viewport->setBook(book);
}

void Core::onRepaintPage(Book *, Page *, QRect *rect)
{
    for (Viewport * viewport : viewports)
        viewport->update(rect);
}

void Core::changeBrushSize(int size)
{
    size_brush_index += size;
    size_brush_index = std::min(size_brush_index, MAX_BRUSH_INDEX);
    size_brush_index = std::max(size_brush_index, MIN_BRUSH_INDEX);
    size_brush       = int(pow(BRUSH_BASE, size_brush_index));
}

void Core::changeEraserSize(int size)
{
    size_eraser_index += size;
    size_eraser_index = std::min(size_eraser_index, MAX_BRUSH_INDEX);
    size_eraser_index = std::max(size_eraser_index, MIN_BRUSH_INDEX);
    size_eraser       = int(pow(ERASER_BASE, size_eraser_index));
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
    // Convert from tablet abs coordinates to multidisplay coordinates
    x1 = (x1 * width_space) / 32767;
    x2 = (x2 * width_space) / 32767;

    y1 = (y1 * height_space) / 32767;
    y2 = (y2 * height_space) / 32767;

    for (Viewport * viewport : viewports)
        viewport->draw(x1, y1, x2, y2, size_brush, brush_color);
}

void Core::erase(int x1, int y1, int x2, int y2) {
    // Convert from tablet abs coordinates to multidisplay coordinates
    x1 = (x1 * width_space) / 32767;
    x2 = (x2 * width_space) / 32767;

    y1 = (y1 * height_space) / 32767;
    y2 = (y2 * height_space) / 32767;

    for (Viewport * viewport : viewports)
        viewport->erase(x1, y1, x2, y2, size_brush);
}

