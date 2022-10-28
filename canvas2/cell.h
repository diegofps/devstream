#ifndef CELL_H
#define CELL_H

#include <QImage>

const int CELL_SIZE = 512;


class Cell {
public:
    Cell(QPair<int, int> & key, bool empty=false);

    ~Cell();

    int i() {
        return _i;
    }

    int j() {
        return _j;
    }

    int x() {
        return _x;
    }

    int y() {
        return _y;
    }

    QImage * image() {
        return _img;
    }

    void setI(int i) {
        _i = i;
        _x = i * CELL_SIZE;
    }

    void setJ(int j) {
        _j = j;
        _y = j * CELL_SIZE;
    }

    void setImage(QImage * img) {
        _img = img;
    }

private:
    int _i;
    int _j;
    int _x;
    int _y;
    QImage *_img;

};

#endif // CELL_H
