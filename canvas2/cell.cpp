#include "cell.h"

#include <QPainter>

Cell::Cell(QPair<int, int> & key, bool empty) :
    i(key.first),
    j(key.second),
    x(j * CELL_SIZE),
    y(i * CELL_SIZE),
    img(nullptr)
{
    QImage * img = new QImage(QSize(CELL_SIZE, CELL_SIZE), QImage::Format_ARGB32_Premultiplied);

    if (empty)
    {
        img->fill(Qt::transparent);
    }
    else
    {
        img->fill(QColor((i+j) % 2 ? "#22ff0000" : "#220000ff"));
        QPainter painter(img);
        QString msg = QString::asprintf("(%d, %d)", i, j);
        painter.drawText(0, 11, msg);
    }

    this->img = img;
}

Cell::~Cell()
{
    if (img != nullptr)
        delete img;
}
