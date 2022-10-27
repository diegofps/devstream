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
#include <QPainter>


class CellChanges {
public:
    CellChanges(QPair<int, int> & key) :
        key(key),
        before(nullptr),
        after(nullptr)
    { }

    ~CellChanges() {
        if (before != nullptr)
            delete before;

        if (after != nullptr)
            delete after;
    }

    void setBefore(QImage * img) {
        if (before == nullptr)
            before = new QImage(QSize(CELL_SIZE, CELL_SIZE), QImage::Format_ARGB32_Premultiplied);

        before->fill(QColor(0,0,0,0));
        QPainter painter(before);
        painter.drawImage(0,0,*img);
    }

    void setAfter(QImage * img) {
        if (after == nullptr)
            after = new QImage(QSize(CELL_SIZE, CELL_SIZE), QImage::Format_ARGB32_Premultiplied);

        after->fill(QColor(0,0,0,0));
        QPainter painter(after);
        painter.drawImage(0,0,*img);
    }

    void undo(QHash<QPair<int,int>, Cell*> & cells) {
        apply(before, cells);
    }

    void redo(QHash<QPair<int,int>, Cell*> & cells) {
        apply(after, cells);
    }

    void apply(QImage * reference, QHash<QPair<int,int>, Cell*> & cells) {
        if (reference == nullptr)
        {
            auto it = cells.find(key);
            if (it != cells.end()) {
                delete *it;
                cells.remove(key);
            }
        }
        else
        {
            auto it = cells.find(key);
            if (it == cells.end())
            {
                Cell * cell = new Cell(key, true);
                QPainter painter(cell->img);
                painter.drawImage(0,0,*reference);
                cells[key] = cell;
            }
            else
            {
                Cell *cell = *it;
                cell->img->fill(QColor(0,0,0,0));
                QPainter painter(cell->img);
                painter.drawImage(0,0,*reference);
            }
        }
    }

    QPair<int, int> key;
    QImage * before;
    QImage * after;

};

class PageChanges {
public:

    PageChanges() {

    }

    void undo(QHash<QPair<int,int>, Cell*> & cells) {
        for (auto it : qAsConst(changes))
            it->undo(cells);
    }

    void redo(QHash<QPair<int,int>, Cell*> & cells) {
        for (auto it : qAsConst(changes))
            it->redo(cells);
    }

    bool hasChanges() {
        return !changes.isEmpty();
    }

    CellChanges * get(QPair<int,int> & key, QHash<QPair<int,int>, Cell*> & cells) {
        if (changes.contains(key))
            return changes[key];

        CellChanges * chp = new CellChanges(key);
        auto it = cells.find(key);

        if (it != cells.end())
            chp->setBefore((*it)->img);

        changes[key] = chp;

        return chp;
    }

    QHash<QPair<int,int>, CellChanges*> changes;
};


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
    void highlightPosition(ChangePenSizeCommand & cmd);
    void undo(UndoCommand &cmd);
    void savePresent();

protected:
    Cell * getCell(QPair<int, int> & key, bool create=false);
    void previousHistoryPoint();
    void nextHistoryPoint();
    void destroyFuture();

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
    QList<PageChanges*> history;
    int historyPosition;

};

#endif // PAGE_H
