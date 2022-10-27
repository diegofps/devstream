#ifndef CELLCHANGES_H
#define CELLCHANGES_H

#include "cell.h"

#include <QHash>
#include <QImage>
#include <QPainter>


class CellChanges {
public:
    CellChanges(QPair<int, int> & key);
    ~CellChanges();
    void setBefore(QImage * img);
    void setAfter(QImage * img);
    void undo(QHash<QPair<int,int>, Cell*> & cells);
    void redo(QHash<QPair<int,int>, Cell*> & cells);
    void apply(QImage * reference, QHash<QPair<int,int>, Cell*> & cells);

private:
    QPair<int, int> key;
    QImage * before;
    QImage * after;

};

#endif // CELLCHANGES_H
