#include "cellchanges.h"

CellChanges::CellChanges(QPair<int, int> &key) :
    key(key),
    before(nullptr),
    after(nullptr)
{ }

CellChanges::~CellChanges() {
    if (before != nullptr)
        delete before;

    if (after != nullptr)
        delete after;
}

void CellChanges::setBefore(QImage *img) {
    if (before == nullptr)
        before = new QImage(QSize(CELL_SIZE, CELL_SIZE), QImage::Format_ARGB32_Premultiplied);

    before->fill(QColor(0,0,0,0));
    QPainter painter(before);
    painter.drawImage(0,0,*img);
}

void CellChanges::setAfter(QImage *img) {
    if (after == nullptr)
        after = new QImage(QSize(CELL_SIZE, CELL_SIZE), QImage::Format_ARGB32_Premultiplied);

    after->fill(QColor(0,0,0,0));
    QPainter painter(after);
    painter.drawImage(0,0,*img);
}

void CellChanges::undo(QHash<QPair<int, int>, Cell *> &cells) {
    apply(before, cells);
}

void CellChanges::redo(QHash<QPair<int, int>, Cell *> &cells) {
    apply(after, cells);
}

void CellChanges::apply(QImage *reference, QHash<QPair<int, int>, Cell *> &cells) {
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
            QPainter painter(cell->image());
            painter.drawImage(0,0,*reference);
            cells[key] = cell;
        }
        else
        {
            Cell *cell = *it;
            cell->image()->fill(QColor(0,0,0,0));
            QPainter painter(cell->image());
            painter.drawImage(0,0,*reference);
        }
    }
}
