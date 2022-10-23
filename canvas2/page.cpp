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


Page::Page(PageListener *listener) :
    book(listener),
    viewX(0),
    viewY(0),
    lastX(0),
    lastY(0)
{
    eraserPen.setCapStyle(Qt::PenCapStyle::RoundCap);
    eraserPen.setStyle(Qt::PenStyle::SolidLine);
    eraserPen.setJoinStyle(Qt::PenJoinStyle::RoundJoin);
//    eraserPen.setColor(QColor(255,255,255,255));

    inkPen.setCapStyle(Qt::PenCapStyle::RoundCap);
    inkPen.setStyle(Qt::PenStyle::SolidLine);
}

void Page::move(int rx, int ry) {
//    print("Moving viewport", rx, ry, viewX, viewY);

    std::lock_guard<std::mutex> lock(drawing);
    viewX += rx;
    viewY += ry;
    book->onRepaintPage(this, nullptr);
}

QRect Page::draw(int x1, int y1, int x2, int y2, int size, QColor * color) {
//    print("Drawing in page ");
    std::lock_guard<std::mutex> lock(drawing);

    // Convert from multidisplay coordinates to world coordinates
    x1 -= viewX;
    y1 -= viewY;

    x2 -= viewX;
    y2 -= viewY;

    // Obtain indexes that may intersect the area
    int i1 = (std::min(y1,y2) - CELL_SIZE) / CELL_SIZE;
    int i2 = ceil((std::max(y1,y2) + CELL_SIZE) / double(CELL_SIZE));

    int j1 = (std::min(x1,x2) - CELL_SIZE) / CELL_SIZE;
    int j2 = ceil((std::max(x1,x2) + CELL_SIZE) / double(CELL_SIZE));

    // Create the pen we will use to draw
    // TODO: Precalculate it in the class?

    if (color == nullptr) {
        eraserPen.setWidth(size);
    }
    else {
        inkPen.setWidth(size);
        inkPen.setColor(*color);
    }
//        pen.setColor(*color);
//    else
//        pen.setColor(QColor(0,0,0,0));

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
//            painter.setBrush(Qt::NoBrush);

            if (color == nullptr) {
                painter.setCompositionMode(QPainter::CompositionMode_Clear);
                painter.setPen(eraserPen);
            } else {
                painter.setPen(inkPen);
            }

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
    top  += viewY;

    QRect rect(left, top, width, height);

    // Request an update to the widget
    book->onRepaintPage(this, &rect);

    // Notify book that this page has changed
    book->onPageEdited(this);

    return rect;
}

QRect Page::erase(int x1, int y1, int x2, int y2, int size) {
    print("Page::eraser", x1, y1, x2, y2, size);
    return this->draw(x1, y1, x2, y2, size, nullptr);
}

void Page::onPaint(QPainter & painter, QRect & rect, QColor * backgroundColor) {
    // wup::print("Page's onPaint called");
    std::lock_guard<std::mutex> lock(drawing);

    if (backgroundColor != nullptr)
        painter.fillRect(0, 0, rect.width(), rect.height(), *backgroundColor);

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
            Cell * cell = getCell(i, j, false);
            if (cell != nullptr)
                painter.drawImage(cell->x - x, cell->y - y, *cell->img);
        }
    }
}

Cell * Page::getCell(int i, int j, bool createOnMiss) {
    //    print("Looking for cell", i, j);

    // Debug mode
    if (false) {
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

        if (!createOnMiss)
            return nullptr;

        Cell *cell = new Cell(i, j, true);
        cells[key] = cell;
        return cell;
    }
}
