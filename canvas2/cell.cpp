#include "cell.h"

#include <QPainter>

Cell::Cell(QPair<int, int> & key, bool empty) :
    _i(key.first),
    _j(key.second),
    _x(_j * CELL_SIZE),
    _y(_i * CELL_SIZE),
    _img(nullptr)
{
    QImage * img = new QImage(QSize(CELL_SIZE, CELL_SIZE), QImage::Format_ARGB32_Premultiplied);

    if (empty)
    {
        img->fill(Qt::transparent);
    }
    else
    {
        img->fill(QColor((_i+_j) % 2 ? "#22ff0000" : "#220000ff"));
        QPainter painter(img);
        QString msg = QString::asprintf("(%d, %d)", _i, _j);
        painter.drawText(0, 11, msg);
    }

    this->_img = img;
}

Cell::~Cell()
{
    if (_img != nullptr)
        delete _img;
}
