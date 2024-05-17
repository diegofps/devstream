#ifndef COMMANDS_H
#define COMMANDS_H

#include <QList>
#include <QPoint>
#include <QDebug>


enum PageMode {
    MODE_TRANSPARENT = 1,
    MODE_OPAQUE      = 2,
    MODE_PASSTHROUGH = 3,
    MODE_DISABLED    = 4,
};


class Command {
public:

    Command(const char * const name) :
        name(name), next(nullptr) {}

    QString name;
    Command * next;
    std::function<void(void)> callback;

};

class DrawCommand : public Command {
public:

    DrawCommand() :
        Command("draw") { }

    void add(int x1, int y1, int x2, int y2) {
        if (points.size() == 0)
            points.append(QPoint(x1, y1));
        points.append(QPoint(x2, y2));
    }

    QList<QPoint> points;
};

class EraseCommand : public Command {
public:

    EraseCommand() :
        Command("erase") { }

    void add(int x1, int y1, int x2, int y2, int x3, int y3) {
        if (points.size() == 0) {
            points.append(QPoint(x1, y1));
            points.append(QPoint(x2, y2));
        }
        points.append(QPoint(x3, y3));
    }

    QList<QPoint> points;
};

class MovePageCommand : public Command {
public:

    MovePageCommand() :
        Command("move_page"), point(0,0) { }

    void add(int x1, int y1) {
        point.setX(point.x() + x1);
        point.setY(point.y() + y1);
    }

    QPoint point;
};

class ChangePageCommand : public Command {
public:

    ChangePageCommand() :
        Command("change_page"), offset(0) { }

    void add(int offset) {
        this->offset += offset;
    }

    int offset;
};

class SetPageModeCommand : public Command {
public:

    SetPageModeCommand() :
        Command("set_page_mode"), pageMode(PageMode::MODE_TRANSPARENT) { }

    void add(int pageMode) {
        this->pageMode = PageMode(pageMode);
    }

    PageMode pageMode;
};

class ChangePenSizeCommand : public Command {
public:

    ChangePenSizeCommand() :
        Command("change_pen_size"),
        size(0),
        x(0),
        y(0) { }

    void add(int size, int x, int y) {
        this->size = size;
        this->x = x;
        this->y = y;
    }

    int size;
    int x;
    int y;
};

class UndoCommand : public Command {
public:

    UndoCommand() :
        Command("undo"),
        offset(0) { }

    void add(int offset) {
        this->offset += offset;
    }

    int offset;
};

class SavePresentCommand : public Command {
public:
    SavePresentCommand() : Command("save_present") { }
    void add() { }
};

class SetNotificationCommand : public Command {
public:

    SetNotificationCommand() :
        Command("set_notification") { }

    void add(std::string & notificationBase64) {
        QByteArray ba(notificationBase64.data()+1, notificationBase64.size()-1);
        this->notification = ba.fromBase64(ba);
        qDebug() << "Encoded notification message is: " << notificationBase64.c_str();
        qDebug() << "Decoded notification message is: " << this->notification;
    }

    QString notification;
};

#endif // COMMANDS_H
