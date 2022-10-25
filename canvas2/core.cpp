#include "core.h"
#include "scalabledisplay.h"

#include <viewport.h>

#include <sys/stat.h>
#include <unistd.h>
#include <iostream>
#include <fstream>
#include <wup/wup.hpp>

#include <QApplication>
#include <QDateTime>
#include <QRegularExpression>

const char * named_pipe = "/tmp/shadow_xppen_deco_pro";

using wup::print;


void
readCommands(Core * c)
{
    std::string cmd;
    bool restart = false;

    while (true) {

        std::ifstream ifs(named_pipe);

        while (!restart)
        {
            if (!(ifs >> cmd)) {
                print("Error during cmd read");
                restart = true;
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
                int x1, y1, x2, y2, x3, y3;
                if (ifs >> x1 >> y1 >> x2 >> y2 >> x3 >> y3)
                     c->erase(x1,y1,x2,y2,x3,y3);
            }

            else if (cmd == "move_page") {
                int rx, ry;
                if (ifs >> rx >> ry)
                    c->movePage(rx,ry);
            }

            else if (cmd == "change_brush_size") {
                int size, x, y;
                if (ifs >> size >> x >> y)
                    c->changeBrushSize(size, x, y);
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

        restart = false;
    }
}

Core::Core(QObject *parent)
    : QObject{parent},
      pageMode(PageMode::MODE_TRANSPARENT),
      transparentBook(this, false),
      opaqueBook(this, true),
      activeBook(&transparentBook),
      reader(readCommands, this),
      size_pen_index(2), // 3
      size_pen(pow(PEN_BASE, size_pen_index)),
      brush_color(QColor("#0000ff")),
      width_space(0),
      height_space(0)
{
    QList<ScalableDisplay*> displays = ScalableDisplay::parseDisplays();

    for (int i=0;i!=displays.size();++i) {
        auto display = displays[i];
        auto g = display->internalGeometry;

        Viewport * viewport = new Viewport(display);
        viewport->setBook(activeBook);
        viewports.append(viewport);

        width_space  = std::max(g.right(), width_space);
        height_space = std::max(g.bottom(), height_space);
    }
}

void Core::onPageChanged(Book *book, Page *)
{
    for (Viewport * viewport : viewports)
        viewport->setBook(book);
}

void Core::changeBrushSize(int size, int x, int y)
{
    size_pen_index += size;
    size_pen_index = std::min(size_pen_index, MAX_PEN_INDEX);
    size_pen_index = std::max(size_pen_index, MIN_PEN_INDEX);
    size_pen       = int(pow(PEN_BASE, size_pen_index));

    x = (x * width_space) / 32767;
    y = (y * height_space) / 32767;

    for (Viewport * viewport : viewports)
        viewport->setHighlightPosition(size_pen, x, y);

    highlightPositionUntil = QDateTime::currentMSecsSinceEpoch() + 3000;
    QTimer::singleShot(3000, this, &Core::endHighlight);
}

void Core::endHighlight()
{
    auto now = QDateTime::currentMSecsSinceEpoch();
    wup::print("Ending highlight", now, highlightPositionUntil);

    if (now >= highlightPositionUntil) {
        for (Viewport * viewport : viewports)
            viewport->setHighlightPosition(0,0,0);
    }
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
        print("passthrough");
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
        viewport->draw(x1, y1, x2, y2, size_pen, &brush_color);
}

void Core::erase(int x1, int y1, int x2, int y2, int x3, int y3) {

    // Convert from tablet abs coordinates to multidisplay coordinates

    x1 = (x1 * width_space) / 32767;
    x2 = (x2 * width_space) / 32767;
    x3 = (x3 * width_space) / 32767;

    y1 = (y1 * height_space) / 32767;
    y2 = (y2 * height_space) / 32767;
    y3 = (y3 * height_space) / 32767;

    for (Viewport * viewport : viewports)
        viewport->erase(x1, y1, x2, y2, x3, y3);
}
