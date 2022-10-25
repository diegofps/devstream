#ifndef CORE_H
#define CORE_H

#include "book.h"

#include <QObject>
#include <QScreen>
#include <QList>
#include <viewport.h>
#include <thread>
#include <page.h>

const int    MAX_PEN_INDEX = 9;
const int    MIN_PEN_INDEX = 1;
const double PEN_BASE      = 2;


enum PageMode {
    MODE_TRANSPARENT = 1,
    MODE_OPAQUE      = 2,
    MODE_PASSTHROUGH = 3,
    MODE_DISABLED    = 4,
};


class Core : public QObject, public BookListener
{
    Q_OBJECT
public:
    explicit Core(QObject *parent = nullptr);

    void onPageChanged(Book *book, Page * page);
    void endHighlight();

signals:

public slots:
    void changeBrushSize(int size, int x, int y);
    void showPreviousPage();
    void showNextPage();
    void setPageMode(int pageMode);
    void movePage(int rx, int ry);
    void draw(int x1, int y1, int x2, int y2);
    void erase(int x1, int y1, int x2, int y2, int x3, int y3);

private:

    QList<Viewport*> viewports;

    PageMode pageMode;
    Book transparentBook;
    Book opaqueBook;
    Book * activeBook;
    std::thread reader;

    int size_pen_index;
    int size_pen;

    QColor brush_color;

    int width_space;
    int height_space;

    qint64 highlightPositionUntil;

    sched_param readerPriority;

};

#endif // CORE_H
