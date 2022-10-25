#ifndef CORE_H
#define CORE_H

#include "book.h"

#include <QObject>
#include <QScreen>
#include <QList>
#include <viewport.h>
#include <thread>
#include <page.h>

const int    MAX_PEN_INDEX = 15;
const int    MIN_PEN_INDEX = 1;
const double PEN_BASE      = 1.5;


class DrawCommand;

class Core : public QObject, public BookListener
{
    Q_OBJECT
public:
    explicit Core(QObject *parent = nullptr);

    void onPageChanged(Book *book, Page * page);
//    void endHighlight();

signals:

public slots:
    void changePenSize(ChangePenSizeCommand & cmd);
    void changePage(ChangePageCommand & cmd);
//    void showPreviousPage();
//    void showNextPage();
    void setPageMode(SetPageModeCommand & cmd);
    void movePage(MovePageCommand & cmd);
    void draw(DrawCommand & cmd);
    void erase(EraseCommand & cmd);

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

    sched_param readerPriority;

};

#endif // CORE_H
