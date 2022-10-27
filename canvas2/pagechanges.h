#ifndef PAGECHANGES_H
#define PAGECHANGES_H

#include "cell.h"
#include "cellchanges.h"

#include <QHash>
#include <QPair>


class PageChanges {
public:
    PageChanges();
    void undo(QHash<QPair<int,int>, Cell*> & cells);
    void redo(QHash<QPair<int,int>, Cell*> & cells);
    bool hasChanges();
    CellChanges * get(QPair<int,int> & key, QHash<QPair<int,int>, Cell*> & cells);

private:
    QHash<QPair<int,int>, CellChanges*> changes;

};

#endif // PAGECHANGES_H
