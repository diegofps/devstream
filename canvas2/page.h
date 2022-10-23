#ifndef PAGE_H
#define PAGE_H

#include <QColor>
#include <QPaintEvent>
#include <QPair>
#include <QHash>
#include <QBrush>
#include <QOpenGLTexture>
#include <mutex>
#include <QPen>


class Page;
class Cell;

class PageListener {
public:
    virtual void onPageEdited(Page *page) = 0;
    virtual void onRepaintPage(Page *page, QRect *rect) = 0;
};

class Page
{
public:
    Page(PageListener *listener);

    void move(int rx, int ry);
    QRect draw(int x1, int y1, int x2, int y2, int size, QColor * color);
    QRect erase(int x1, int y1, int x2, int y2, int size);
    void onPaint(QPainter & painter, QRect & rect, QColor * backgroundColor);
    Cell * getCell(int i, int j, bool create=false);

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

};

#endif // PAGE_H
