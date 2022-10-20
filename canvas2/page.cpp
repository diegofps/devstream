#include "page.h"

#include <QImage>
#include <QPainter>
#include <wup/wup.hpp>

using namespace wup;

const int CELL_SIZE = 256;

Page::Page(PageListener *listener, bool opaque) :
    listener(listener),
    viewX(0),
    viewY(0),
    opaque(opaque),
    backgroundBrush()
{
    backgroundBrush.setColor(opaque? QColor("ffcccccc") : QColor("11ffffff"));
}

void Page::move(int rx, int ry) {
    print("Moving viewport", rx, ry, viewX, viewY);
    viewX += rx;
    viewY += ry;
    listener->onRepaintPage(this);
}

void Page::draw(int x1, int y1, int x2, int y2, int size, QColor &color) {

}

void Page::erase(int x1, int y1, int x2, int y2, int size) {

}

#include <QPaintEngine>

void Page::onPaint(QPaintEvent & event, QPainter & painter, QRect & rect) {
    wup::print("Page's onPaint called");

    painter.fillRect(0, 0, rect.width(), rect.height(), backgroundBrush);

    int x = rect.left() - viewX;
    int y = rect.top() - viewY;

//    wup::print(rect.left(), rect.top(), rect.right(), rect.bottom());
//    wup::print(viewX, viewY);
//    wup::print(x, y);

    int i1 = (y - CELL_SIZE) / CELL_SIZE;
    int i2 = ceil((y + rect.height()) / double(CELL_SIZE));

    int j1 = (x - CELL_SIZE) / CELL_SIZE;
    int j2 = ceil((x + rect.width()) / double(CELL_SIZE));

//    print("i:", i1, i2);
//    print("j:", j1, j2);
//    print();

    for (int i=i1;i<i2;++i) {
        for (int j=j1;j<j2;++j) {
            int xx = j * CELL_SIZE - x;
            int yy = i * CELL_SIZE - y;

            QImage * cell = getCell(i,j);
            painter.drawImage(xx, yy, *cell);
        }
    }
}

QImage * Page::getCell(int i, int j) {
//    print("Looking for cell", i, j);
    QPair<int, int> key(i,j);

    auto it = cells.find(key);

    if (it != cells.end())
        return *it;

    QImage *cell = new QImage(QSize(CELL_SIZE, CELL_SIZE), QImage::Format_ARGB32);
//    cell.fill(Qt::transparent);
    cells[key] = cell;

    if ((i+j) % 2)
        cell->fill(QColor("#22ff0000"));
    else
        cell->fill(QColor("#220000ff"));


    QString msg = QString::asprintf("(%d, %d)", i, j);

    QPainter painter(cell);
    painter.drawText(0, 11, msg);

    return cell;
}
