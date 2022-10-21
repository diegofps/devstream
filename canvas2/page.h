#ifndef PAGE_H
#define PAGE_H

#include <QColor>
#include <QPaintEvent>
#include <QPair>
#include <QHash>
#include <QBrush>
#include <QOpenGLTexture>

class Page;

class PageListener {
public:
    virtual void onPageEdited(Page *page) = 0;
    virtual void onRepaintPage(Page *page) = 0;
};

class Page
{
public:
    Page(PageListener *listener, bool opaque);

    void move(int rx, int ry);
    void draw(int x1, int y1, int x2, int y2, int size, QColor &color);
    void erase(int x1, int y1, int x2, int y2, int size);
    void onPaint(QPainter & painter, QRect & rect);
    QImage * getCell(int i, int j, bool create=false);

private:
    PageListener *listener;
    int viewX;
    int viewY;
    int lastX;
    int lastY;
    QHash<QPair<int,int>, QImage*> cells;
    bool opaque;
    QBrush backgroundBrush;

};

#endif // PAGE_H
