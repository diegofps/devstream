#include "cell.h"

#include <QPainter>

Cell::Cell(int i, int j, bool empty) :
    i(i),
    j(j),
    x(j * CELL_SIZE),
    y(i * CELL_SIZE),
    img(nullptr)
{
    QImage * cell = new QImage(QSize(CELL_SIZE, CELL_SIZE), QImage::Format_ARGB32_Premultiplied);

    if (empty)
    {
        cell->fill(Qt::transparent);
    }
    else
    {
        cell->fill(QColor((i+j) % 2 ? "#22ff0000" : "#220000ff"));
        QPainter painter(cell);
        QString msg = QString::asprintf("(%d, %d)", i, j);
        painter.drawText(0, 11, msg);
    }

    this->img = cell;
}
