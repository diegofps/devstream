#ifndef PAGE_H
#define PAGE_H

#include "cell.h"

#include <QColor>
#include <QPaintEvent>
#include <QPair>
#include <QHash>
#include <QBrush>
#include <QOpenGLTexture>
#include <mutex>
#include <QPen>



class Page;

class PageListener {
public:
    virtual void onPageEdited(Page *page) = 0;
};

class Page
{
public:
    Page(PageListener *listener);

    void move(int rx, int ry);
    void draw(int x1, int y1, int x2, int y2, int size, QColor * color);
    void erase(int x1, int y1, int x2, int y2, int x3, int y3);
    void onPaint(QPainter & painter, QRect & rect, QColor * backgroundColor);
    Cell * getCell(int i, int j, bool create=false);
    QRect setHighlightPosition(int size, int x, int y);

private:
    PageListener *book;
    int viewX;
    int viewY;
    int lastX;
    int lastY;
    QHash<QPair<int,int>, Cell*> cells;
    bool opaque;
    QBrush backgroundBrush;
    std::mutex drawing;
    QPen eraserPen;
    QPen inkPen;
    int highlightSize;
    QBrush highlightBrush;
    QPointF erasePolygon[3];
    QBrush eraserBrush;

};

#endif // PAGE_H
