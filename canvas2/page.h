#ifndef PAGE_H
#define PAGE_H

#include "cell.h"
#include "commands.h"

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

    void move(MovePageCommand & cmd);
    void draw(DrawCommand & cmd, int size, QColor * color);
    void erase(EraseCommand & cmd);
    bool onPaint(QPainter & painter, QRect & rect, QColor * backgroundColor);
    Cell * getCell(int i, int j, bool create=false);
    void highlightPosition(ChangePenSizeCommand & cmd);

private:
    PageListener *book;
    int viewX;
    int viewY;
    float viewXSmooth;
    float viewYSmooth;
    QHash<QPair<int,int>, Cell*> cells;
    bool opaque;
    QBrush backgroundBrush;
    std::mutex drawing;
    QPen eraserPen;
    QPen inkPen;
    int highlightSize;
    float highlightSizeSmooth;
    qint64 highlightStart;
    qint64 highlightEnd;
    QBrush highlightBrush;
    int highlightX;
    int highlightY;
    QPointF erasePolygon[3];
    QBrush eraserBrush;

};

#endif // PAGE_H
