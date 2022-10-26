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

#include "commands.h"

wup::Semaphore semCommands;
std::mutex syncCommands;
Command * head = nullptr;
Command * tail = nullptr;

#define PUSH_CMD(COMMAND_TYPE, CORE_METHOD, ...) \
{\
    std::lock_guard<std::mutex> lock(syncCommands);\
\
    if (tail != nullptr && tail->name == cmd.c_str()) \
    { \
        ((COMMAND_TYPE*)tail)->add(__VA_ARGS__); \
    } \
    else \
    { \
        COMMAND_TYPE * newCmd = new COMMAND_TYPE(); \
        newCmd->add(__VA_ARGS__); \
        newCmd->callback = [c, newCmd]() \
        { \
            c->CORE_METHOD(*newCmd); \
        }; \
\
        if (head == nullptr) \
        { \
            head = newCmd; \
            tail = newCmd; \
        } \
        else \
        { \
            tail->next = newCmd; \
            tail = newCmd; \
        } \
\
        semCommands.release(); \
    } \
}

void
runReader(Core * c)
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

            if (cmd == "draw") {
                int x1, y1, x2, y2;
                if (ifs >> x1 >> y1 >> x2 >> y2)
                    PUSH_CMD(DrawCommand, draw, x1, y1, x2, y2);
            }

            else if (cmd == "erase") {
                int x1, y1, x2, y2, x3, y3;
                if (ifs >> x1 >> y1 >> x2 >> y2 >> x3 >> y3)
                    PUSH_CMD(EraseCommand, erase, x1, y1, x2, y2, x3, y3);
            }

            else if (cmd == "move_page") {
                int rx, ry;
                if (ifs >> rx >> ry)
                    PUSH_CMD(MovePageCommand, movePage, rx, ry);
            }

            else if (cmd == "change_brush_size") {
                int size, x, y;
                if (ifs >> size >> x >> y)
                    PUSH_CMD(ChangePenSizeCommand, changePenSize, size, x, y);
            }

            else if (cmd == "set_page_mode") {
                int pageMode;
                if (ifs >> pageMode)
                    PUSH_CMD(SetPageModeCommand, setPageMode, pageMode);
            }

            else if (cmd == "change_page") {
                int offset;
                if (ifs >> offset)
                    PUSH_CMD(ChangePageCommand, changePage, offset);
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

void runWorker() {
    Command * cmd;

    while (true) {
        semCommands.acquire();

        {
            std::lock_guard<std::mutex> lock(syncCommands);
            cmd = head;
            head = head->next;

            if (head == nullptr)
                tail = nullptr;
        }

        cmd->callback();
        delete cmd;
    }
}

Core::Core(QApplication *a)
    : QObject{nullptr},

      pageMode(PageMode::MODE_TRANSPARENT),
      transparentBook(this, false),
      opaqueBook(this, true),
      activeBook(&transparentBook),
      reader(runReader, this),
      worker(runWorker),
      size_pen_index(3), // 3
      size_pen(pow(PEN_BASE, size_pen_index)),
      brush_color(QColor("#0000ff")),
      width_space(0),
      height_space(0)
{
    // Configure thread priorities

    lowThreadPriority.sched_priority = 2;
    pthread_setschedparam(reader.native_handle(), SCHED_OTHER, &lowThreadPriority);
    pthread_setschedparam(worker.native_handle(), SCHED_OTHER, &lowThreadPriority);

    // Configure Viewports for each display

    refreshSpace();

    // Add listeners to react to display changes

    connect(a, &QGuiApplication::screenAdded, [this](QScreen *) {
        refreshSpace();
    });

    connect(a, &QGuiApplication::screenRemoved, [this](QScreen *) {
        refreshSpace();
    });

    for (QScreen *screen : QGuiApplication::screens()) {
        connect(screen, &QScreen::geometryChanged, [this](const QRect &) {
            refreshSpace();
        });
    }
}

void Core::refreshSpace() {

    qDebug("Refreshing displays and viewports");

    QList<ScalableDisplay*> displaysNow = ScalableDisplay::parseDisplays();
    QSet<QString> preservedSerialNumbers;

    QList<QPair<ScalableDisplay*,ScalableDisplay*>> displaysPreserved;
    QList<ScalableDisplay*> displaysRemoved;
    QList<ScalableDisplay*> displaysAdded;

    for (ScalableDisplay * newDisplay : displaysNow) {
        ScalableDisplay * oldDisplay = nullptr;

        for (ScalableDisplay * x : displays) {
            if (x->serialNumber == newDisplay->serialNumber) {
                oldDisplay = x;
                break;
            }
        }

        if (oldDisplay == nullptr) {
            displaysAdded.append(newDisplay);
        } else {
            displaysPreserved.append(QPair<ScalableDisplay*,ScalableDisplay*>(oldDisplay, newDisplay));
            preservedSerialNumbers.insert(newDisplay->serialNumber);
        }
    }

    for (ScalableDisplay * oldDisplay : displays)
        if (!preservedSerialNumbers.contains(oldDisplay->serialNumber))
            displaysRemoved.append(oldDisplay);

    qDebug("DisplaysRemoved=%lld, DisplaysAdded=%lld, DisplaysPreserved=%lld",
           displaysRemoved.size(),
           displaysAdded.size(),
           displaysPreserved.size());

    displays.clear();

    qDebug("Adding new displays");

    for (ScalableDisplay * display : displaysAdded) {
        displays.append(display);

        Viewport * viewport = new Viewport(display);
        viewport->setBook(activeBook);
        viewports.append(viewport);
    }

    qDebug("Refreshing preserved displays");

    for (auto & pair : displaysPreserved) {
        displays.append(pair.first);

        ScalableDisplay * oldDisplay = pair.first;
        ScalableDisplay * newDisplay = pair.second;

        oldDisplay->displaySerialNumber = newDisplay->displaySerialNumber;
        oldDisplay->displayProductName = newDisplay->displayProductName;
        oldDisplay->externalGeometry = newDisplay->externalGeometry;
        oldDisplay->internalGeometry = newDisplay->internalGeometry;
        oldDisplay->scaleX = newDisplay->scaleX;
        oldDisplay->scaleY = newDisplay->scaleY;
        oldDisplay->normX = newDisplay->normX;
        oldDisplay->normY = newDisplay->normY;
        oldDisplay->port = newDisplay->port;

        for (Viewport * viewport : viewports)
            if (viewport->getDisplay()->serialNumber == oldDisplay->serialNumber)
                viewport->setDisplay(oldDisplay);
    }

    qDebug("Deleting removed displays and viewports");

    for (ScalableDisplay * display : displaysRemoved) {
        for (Viewport * viewport : viewports) {
            if (viewport->getDisplay()->serialNumber == display->serialNumber) {
                viewport->close();
                viewports.removeOne(viewport);
                delete viewport;
                break;
            }
        }

        delete display;
    }

    qDebug("Updating width and height space");

    width_space  = 0;
    height_space = 0;

    for (ScalableDisplay * display : displays) {
        auto g = display->internalGeometry;
        width_space  = std::max(g.right(), width_space);
        height_space = std::max(g.bottom(), height_space);
    }

    qDebug("Displays and viewports refreshed");
}

void Core::onPageChanged(Book *book, Page *)
{
    for (Viewport * viewport : viewports)
        viewport->setBook(book);
}

void Core::changePenSize(ChangePenSizeCommand & cmd)
{
    size_pen_index += cmd.size;
    size_pen_index = std::min(size_pen_index, MAX_PEN_INDEX);
    size_pen_index = std::max(size_pen_index, MIN_PEN_INDEX);
    size_pen       = int(pow(PEN_BASE, size_pen_index));

    cmd.x    = (cmd.x * width_space) / 32767;
    cmd.y    = (cmd.y * height_space) / 32767;
    cmd.size = size_pen;

    for (Viewport * viewport : viewports)
        viewport->highlightPosition(cmd);
}

void Core::changePage(ChangePageCommand & cmd)
{
    activeBook->changePage(cmd);
}

void Core::setPageMode(SetPageModeCommand & cmd)
{
    if (pageMode == cmd.pageMode)
        return;

    this->pageMode = cmd.pageMode;

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

void Core::movePage(MovePageCommand & cmd) {

    activeBook->movePage(cmd);

    for (Viewport * viewport : viewports)
        viewport->asyncUpdate();
}

void Core::draw(DrawCommand & cmd) {

    // Convert from tablet abs coordinates to multidisplay coordinates

    for (QPoint & p : cmd.points)
    {
        p.setX((p.x() * width_space) / 32767);
        p.setY((p.y() * height_space) / 32767);
    }

    // Ask each viewport to draw, if necessary

    for (Viewport * viewport : viewports)
        viewport->draw(cmd, size_pen, &brush_color);
}

void Core::erase(EraseCommand & cmd) {

    // Convert from tablet abs coordinates to multidisplay coordinates

    for (QPoint & p : cmd.points)
    {
        p.setX((p.x() * width_space) / 32767);
        p.setY((p.y() * height_space) / 32767);
    }

    for (Viewport * viewport : viewports)
        viewport->erase(cmd);
}
