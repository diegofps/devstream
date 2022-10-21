#include "page.h"

#include <QImage>
#include <QBrush>
#include <QPainter>
#include <wup/wup.hpp>

using namespace wup;

const int CELL_SIZE = 256;


class Cell {
public:
    Cell(int i, int j, bool empty=false) :
        i(i), 
        j(j), 
        x(j * CELL_SIZE),
        y(i * CELL_SIZE),
        img(nullptr)
    {
        QImage * cell = new QImage(QSize(CELL_SIZE, CELL_SIZE), QImage::Format_ARGB32);
        
        if (empty) 
        {
            cell->fill(Qt::transparent);
        }
        else 
        {
            if ((i+j) % 2)
                cell->fill(QColor("#22ff0000"));
            else
                cell->fill(QColor("#220000ff"));

            QPainter painter(cell);
            QString msg = QString::asprintf("(%d, %d)", i, j);
            painter.drawText(0, 11, msg);
        }

        this->img = cell;
    }

    int i;
    int j;
    int x;
    int y;
    QImage *img;

};


Page::Page(PageListener *listener, bool opaque) :
    listener(listener),
    viewX(0),
    viewY(0),
    lastX(0),
    lastY(0),
    opaque(opaque),
    backgroundBrush()
{
    backgroundBrush.setColor(opaque? QColor("ffcccccc") : QColor("11ffffff"));
}

void Page::move(int rx, int ry) {
//    print("Moving viewport", rx, ry, viewX, viewY);

    std::lock_guard<std::mutex> lock(drawing);
    viewX += rx;
    viewY += ry;
    listener->onRepaintPage(this, nullptr);
}

void Page::draw(int x1, int y1, int x2, int y2, int size, QColor &color) {
    std::lock_guard<std::mutex> lock(drawing);

    // Convert from multidisplay coordinates to world coordinates
    x1 -= viewX;
    y1 -= viewY;

    x2 -= viewX;
    y2 -= viewY;

    // Obtain indexes that may intersect the area
    int i1 = (std::min(y1,y2) - CELL_SIZE) / CELL_SIZE;
    int i2 = ceil(std::max(y1,y2) / double(CELL_SIZE));

    int j1 = (std::min(x1,x2) - CELL_SIZE) / CELL_SIZE;
    int j2 = ceil(std::max(x1,x2) / double(CELL_SIZE));

    // Create the pen we will use to draw
    // TODO: Precalculate it in the class?
    QPen pen;
    pen.setColor(color);
    pen.setWidth(size);
    pen.setCapStyle(Qt::PenCapStyle::RoundCap);
    pen.setStyle(Qt::PenStyle::SolidLine);

    // Paint all cells in the indexes selected
    for (int i=i1;i<i2;++i) {
        for (int j=j1;j<j2;++j) {
            Cell * cell = getCell(i, j, true);

            // Calculate the position relative to the cell coordinates
            int xx1 = x1 - cell->x;
            int yy1 = y1 - cell->y;

            int xx2 = x2 - cell->x;
            int yy2 = y2 - cell->y;

            // Draw the line
            QPainter painter(cell->img);
            painter.setRenderHint(QPainter::Antialiasing, true);
            painter.setPen(pen);
            painter.drawLine(xx1,yy1,xx2,yy2);
        }
    }

    // Calculate the region in the widget that must be updated
    int left = std::min(x1,x2) * CELL_SIZE;
    int top  = std::min(y1,y2) * CELL_SIZE;

    int width  = std::max(x1,x2) * CELL_SIZE - std::min(x1,x2) * CELL_SIZE;
    int height = std::max(y1,y2) * CELL_SIZE - std::min(y1,y2) * CELL_SIZE;
    
    // Convert from world coordinates to multiviewport coordinates
    left += viewX;
    top += viewY;

    QRect rect(left, top, width, height);

    // Request an update to the widget
    listener->onRepaintPage(this, &rect);
}

void Page::erase(int x1, int y1, int x2, int y2, int size) {

}

void Page::onPaint(QPainter & painter, QRect & rect) {
//    wup::print("Page's onPaint called");

    int viewX, viewY;
    {
        std::lock_guard<std::mutex> lock(drawing);
        viewX = this->viewX;
        viewY = this->viewY;
    }

    painter.fillRect(0, 0, rect.width(), rect.height(), backgroundBrush);

    // Convert from multidisplay coordinates to world coordinates
    int x = rect.left() - viewX;
    int y = rect.top() - viewY;

    // Obtain indexes that may intersect the area
    int i1 = (y - CELL_SIZE) / CELL_SIZE;
    int i2 = ceil((y + rect.height()) / double(CELL_SIZE));

    int j1 = (x - CELL_SIZE) / CELL_SIZE;
    int j2 = ceil((x + rect.width()) / double(CELL_SIZE));

    for (int i=i1;i<i2;++i) {
        for (int j=j1;j<j2;++j) {
            Cell * cell = getCell(i, j, true);
            if (cell != nullptr)
                painter.drawImage(cell->x - x, cell->y - y, *cell->img);
        }
    }
}

Cell * Page::getCell(int i, int j, bool create) {
    //    print("Looking for cell", i, j);

    // Debug mode
    if (true) {
        QPair<int, int> key(i,j);

        auto it = cells.find(key);

        if (it != cells.end())
            return *it;

        Cell *cell = new Cell(i, j, false);
        cells[key] = cell;
        return cell;
    }

    else {
        QPair<int, int> key(i,j);
        auto it = cells.find(key);

        if (it != cells.end())
            return *it;

        if (!create)
            return nullptr;

        Cell *cell = new Cell(i, j, true);
        cells[key] = cell;
        return cell;
    }
}
