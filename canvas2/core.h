#ifndef CORE_H
#define CORE_H

#include "book.h"

#include <QObject>
#include <QScreen>
#include <QList>
#include <viewport.h>
#include <thread>
#include <page.h>

const int    MAX_PEN_INDEX = 17;
const int    MIN_PEN_INDEX = 2;
const double PEN_BASE      = 1.5;


class DrawCommand;

class Core : public QObject, public BookListener
{
    Q_OBJECT

public:
    explicit Core(QApplication *a);
    void onPageChanged(Book *book, Page * page);

public slots:
    void changePenSize(ChangePenSizeCommand & cmd);
    void changePage(ChangePageCommand & cmd);
    void setPageMode(SetPageModeCommand & cmd);
    void movePage(MovePageCommand & cmd);
    void draw(DrawCommand & cmd);
    void erase(EraseCommand & cmd);
    void undo(UndoCommand &cmd);
    void savePresent(SavePresentCommand &cmd);
    void refreshSpace();

private:
    QList<Viewport*> viewports;
    PageMode pageMode;
    Book transparentBook;
    Book opaqueBook;
    Book * activeBook;
    std::thread reader;
    std::thread worker;
    int size_pen_index;
    int size_pen;
    QColor brush_color;
    int width_space;
    int height_space;
    qint64 highlightPositionUntil;
    sched_param lowThreadPriority;
    QList<ScalableDisplay*> displays;

};

#endif // CORE_H
