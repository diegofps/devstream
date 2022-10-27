#include "pagechanges.h"

PageChanges::PageChanges() {

}

void PageChanges::undo(QHash<QPair<int, int>, Cell *> &cells) {
    for (auto it : qAsConst(changes))
        it->undo(cells);
}

void PageChanges::redo(QHash<QPair<int, int>, Cell *> &cells) {
    for (auto it : qAsConst(changes))
        it->redo(cells);
}

bool PageChanges::hasChanges() {
    return !changes.isEmpty();
}

CellChanges * PageChanges::get(QPair<int, int> &key, QHash<QPair<int, int>, Cell *> & cells) {
    if (changes.contains(key))
        return changes[key];

    CellChanges * chp = new CellChanges(key);
    auto it = cells.find(key);

    if (it != cells.end())
        chp->setBefore((*it)->image());

    changes[key] = chp;

    return chp;
}
