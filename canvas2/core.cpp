#include "core.h"
#include "scalabledisplay.h"

#include <viewport.h>

#include <sys/stat.h>
#include <unistd.h>
#include <iostream>
#include <fstream>

#include <QApplication>
#include <QDateTime>
#include <QRegularExpression>
#include <QSemaphore>
#include <QFile>

const char * named_pipe = "/tmp/shadow_xppen_deco_pro";

#include "commands.h"

QSemaphore semCommands;
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


Core::Core(QApplication *a)
    : QObject{nullptr},

      pageMode(PageMode::MODE_TRANSPARENT),
      transparentBook(this, false),
      opaqueBook(this, true),
      activeBook(&transparentBook),
//      readerThread(runReader, this),
//      workerThread(runWorker),
      size_pen_index(6),
      size_pen(pow(PEN_BASE, size_pen_index)),
      brush_color(QColor("#0000ff")),
      width_space(0),
      height_space(0)
{
    // Configure reader thread

//    lowThreadPriority.sched_priority = 2;
//    pthread_setschedparam(reader.native_handle(), SCHED_OTHER, &lowThreadPriority);
//    pthread_setschedparam(worker.native_handle(), SCHED_OTHER, &lowThreadPriority);

    readerThread = new ReaderThread(this);
    readerThread->setPriority(QThread::LowPriority);
    readerThread->start();


    // Configure command executor thread
    commandThread = new CommandThread();
    commandThread->setPriority(QThread::LowPriority);
    commandThread->start();


    // Configure Viewports for each display

    refreshSpace();

    // Add listeners to react to display changes

    connect(a, &QGuiApplication::screenAdded, [this](QScreen *) {
        qDebug("Screen added");
        refreshSpace();
    });

    connect(a, &QGuiApplication::screenRemoved, [this](QScreen *) {
        qDebug("Screen removed");
        refreshSpace();
    });

    for (QScreen *screen : QGuiApplication::screens()) {
        connect(screen, &QScreen::geometryChanged, [this, screen](const QRect &) {
            qDebug("Screen changed: %s", qUtf8Printable(screen->serialNumber()));
            refreshSpace();
        });
    }
}

Core::~Core()
{
//    readerThread->finish();
//    commandThread->finish();

//    readerThread->wait();
//    commandThread->wait();
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

        Viewport * viewport = new Viewport(display, &notificationPool);
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

void Core::undo(UndoCommand & cmd)
{
    activeBook->undo(cmd);

    for (Viewport * viewport : viewports)
        viewport->asyncUpdate();
}

void Core::savePresent(SavePresentCommand & cmd)
{
    activeBook->savePresent(cmd);
}

void Core::setPageMode(SetPageModeCommand & cmd)
{
    if (pageMode == cmd.pageMode)
        return;

    this->pageMode = cmd.pageMode;

    switch (pageMode) {
    case MODE_TRANSPARENT:
        qDebug("Activating mode: transparent");
        activeBook = &transparentBook;
        activeBook->setVisible(true);
        break;
    case MODE_OPAQUE:
        qDebug("Activating mode: opaque");
        activeBook = &opaqueBook;
        activeBook->setVisible(true);
        break;
    case MODE_PASSTHROUGH:
        qDebug("Activating mode: passthrough");
        activeBook = &transparentBook;
        activeBook->setVisible(true);
        break;
    case MODE_DISABLED:
        qDebug("Activating mode: disabled");
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

void Core::setWeakNotification(SetWeakNotificationCommand & cmd)
{
    notificationPool.setWeakNotification(cmd.title, cmd.extra);
    requestDropExpiredNotifications();

    for (Viewport * viewport : viewports)
        viewport->asyncUpdate();
}

void Core::requestDropExpiredNotifications()
{
    Core * c = this;
    std::string cmd { "drop_expired_notifications" };
    PUSH_CMD(DropExpiredNotifications, dropExpiredNotifications);
}

void Core::setStrongNotification(SetStrongNotificationCommand & cmd)
{
    notificationPool.setStrongNotification(cmd.title, cmd.extra, cmd.visible);

    for (Viewport * viewport : viewports)
        viewport->asyncUpdate();
}

void Core::dropExpiredNotifications(DropExpiredNotifications &)
{
    long nextExpireTime = notificationPool.dropExpiredNotifications();

    for (Viewport * viewport : viewports)
        viewport->asyncUpdate();

    if (nextExpireTime >= 0)
        QTimer::singleShot(nextExpireTime * 1000, this, &Core::requestDropExpiredNotifications);
}

void CommandThread::run()
{
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

void ReaderThread::run()
{
    std::string cmd;
    bool reopenPipe;
    Core * c = core;

    while (true)
    {

        //        QFile ifs2(named_pipe);

        //        if (!ifs2.open(QFile::ReadOnly | QFile::Text))
        //        {
        //            qWarning("Failed to open named pipe");
        //            sleep(1);
        //            continue;
        //        }

        std::ifstream ifs(named_pipe);
        reopenPipe = false;

        while (!reopenPipe)
        {
            if (!(ifs >> cmd)) {
                qWarning("Error during cmd read");
                reopenPipe = true;
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

            else if (cmd == "undo") {
                int offset;
                if (ifs >> offset)
                    PUSH_CMD(UndoCommand, undo, offset);
            }

            else if (cmd == "save_present") {
                PUSH_CMD(SavePresentCommand, savePresent);
            }

            else if (cmd == "set_weak_notification") {
                std::string titleBase64;
                ifs >> titleBase64;

                std::string extraBase64;
                ifs >> extraBase64;

                PUSH_CMD(SetWeakNotificationCommand, setWeakNotification, titleBase64, extraBase64);
            }

            else if (cmd == "set_strong_notification") {
                std::string titleBase64;
                ifs >> titleBase64;

                std::string extraBase64;
                ifs >> extraBase64;

                int visible;
                ifs >> visible;

                PUSH_CMD(SetStrongNotificationCommand, setStrongNotification, titleBase64, extraBase64, visible);
            }

            else if (cmd == "") {
                sleep(1);
            }

            else {
                qWarning("Unknown command '%s'", cmd.c_str());
            }
        }
    }
}
