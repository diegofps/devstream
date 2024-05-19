#ifndef CORE_H
#define CORE_H

#include "book.h"

#include <QObject>
#include <QScreen>
#include <QList>
#include <viewport.h>
#include <thread>
#include <page.h>
#include <QThread>

const int    MAX_PEN_INDEX = 17;
const int    MIN_PEN_INDEX = 2;
const double PEN_BASE      = 1.5;


class DrawCommand;
class Core;

class CommandThread : public QThread
{
    Q_OBJECT

public:
    CommandThread() { }
    virtual ~CommandThread() { }

private:

    void run() override;
};

class ReaderThread : public QThread
{
    Q_OBJECT

    Core * core;

public:
    ReaderThread(Core * c) : core(c) { }
    virtual ~ReaderThread() { }

private:

    void run() override;
};

class Core : public QObject, public BookListener
{
    Q_OBJECT

public:
    explicit Core(QApplication *a);
    virtual ~Core();
    void onPageChanged(Book *book, Page * page);

public slots:
    void changePenSize(ChangePenSizeCommand & cmd);
    void changePage(ChangePageCommand & cmd);
    void setPageMode(SetPageModeCommand & cmd);
    void movePage(MovePageCommand & cmd);
    void draw(DrawCommand & cmd);
    void erase(EraseCommand & cmd);
    void undo(UndoCommand & cmd);
    void savePresent(SavePresentCommand & cmd);
    void setWeakNotification(SetWeakNotificationCommand &cmd);
    void setStrongNotification(SetStrongNotificationCommand &cmd);
    void dropExpiredNotifications(DropExpiredNotifications & cmd);
    void refreshSpace();

private:
    QList<Viewport*> viewports;
    PageMode pageMode;
    Book transparentBook;
    Book opaqueBook;
    Book * activeBook;
    QThread * readerThread;
    QThread * commandThread;
    int size_pen_index;
    int size_pen;
    QColor brush_color;
    int width_space;
    int height_space;
    qint64 highlightPositionUntil;
    sched_param lowThreadPriority;
    QList<ScalableDisplay*> displays;
    NotificationPool notificationPool;

private:
    void requestDropExpiredNotifications();
};

#endif // CORE_H
