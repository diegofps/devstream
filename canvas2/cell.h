#ifndef CELL_H
#define CELL_H

#include <QImage>

const int CELL_SIZE = 64;


class Cell {
public:
    Cell(QPair<int, int> & key, bool empty=false);

    ~Cell();

    int i;
    int j;
    int x;
    int y;
    QImage *img;

};

#endif // CELL_H
