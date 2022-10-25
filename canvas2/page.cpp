#include "page.h"

#include <QDateTime>
#include <QPainter>
#include <QBrush>
#include <QImage>

#include <wup/wup.hpp>

using namespace wup;



Page::Page(PageListener *listener) :
    book(listener),
    viewX(0),
    viewY(0),
    lastX(0),
    lastY(0),
    highlightSize(5)
{
    eraserPen.setCapStyle(Qt::PenCapStyle::RoundCap);
    eraserPen.setStyle(Qt::PenStyle::SolidLine);
    eraserPen.setJoinStyle(Qt::PenJoinStyle::RoundJoin);

    inkPen.setCapStyle(Qt::PenCapStyle::RoundCap);
    inkPen.setStyle(Qt::PenStyle::SolidLine);
    inkPen.setCapStyle(Qt::PenCapStyle::RoundCap);

    highlightBrush.setStyle(Qt::BrushStyle::SolidPattern);
    highlightBrush.setColor(QColor(255,0,0));

    eraserBrush.setStyle(Qt::BrushStyle::SolidPattern);
    eraserBrush.setColor(QColor(0,0,0));

}

void Page::move(int rx, int ry) {
//    print("Moving viewport", rx, ry, viewX, viewY);

    std::lock_guard<std::mutex> lock(drawing);
    viewX += rx;
    viewY += ry;
}

QRect Page::setHighlightPosition(int size, int x, int y) {
    print("setting highlight", size);

    lastX = x;
    lastY = y;
    highlightSize = size;

    QRect area(x, y, size, size);

    return area;
}

void Page::draw(int x1, int y1, int x2, int y2, int size, QColor * color) {

    std::lock_guard<std::mutex> lock(drawing);

    // Convert from multidisplay coordinates to world coordinates

    x1 -= viewX;
    y1 -= viewY;

    x2 -= viewX;
    y2 -= viewY;

    // Obtain indexes that may intersect the area
    int size_2 = size % 2 ? size / 2 + 1 : size;

    int i1 = (std::min(y1,y2) - CELL_SIZE - size_2) / CELL_SIZE;
    int i2 = ceil((std::max(y1,y2) + CELL_SIZE + size_2) / double(CELL_SIZE));

    int j1 = (std::min(x1,x2) - CELL_SIZE - size_2) / CELL_SIZE;
    int j2 = ceil((std::max(x1,x2) + CELL_SIZE + size_2) / double(CELL_SIZE));

    // Create the pen we will use to draw

    inkPen.setWidth(size);
    inkPen.setColor(*color);

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
            painter.setPen(inkPen);
            painter.drawLine(xx1,yy1,xx2,yy2);
        }
    }

    // Notify book that this page has changed

    book->onPageEdited(this);

    lastX = x2;
    lastY = y2;
}

void Page::erase(int x1, int y1, int x2, int y2, int x3, int y3) {
//    print("Page::eraser", x1, y1, x2, y2, x3, y3);

    std::lock_guard<std::mutex> lock(drawing);

    Clock c;

    // Convert from multidisplay coordinates to world coordinates

    x1 -= viewX;
    y1 -= viewY;

    x2 -= viewX;
    y2 -= viewY;

    x3 -= viewX;
    y3 -= viewY;

    // Obtain indexes that may intersect the area

    int i1 = (std::min(y1,y2) - CELL_SIZE) / CELL_SIZE;
    int i2 = ceil((std::max(y1,y2) + CELL_SIZE) / double(CELL_SIZE));

    int j1 = (std::min(x1,x2) - CELL_SIZE) / CELL_SIZE;
    int j2 = ceil((std::max(x1,x2) + CELL_SIZE) / double(CELL_SIZE));

    // Paint all cells in the indexes selected

    for (int i=i1;i<i2;++i) {
        for (int j=j1;j<j2;++j) {
            Cell * cell = getCell(i, j, true);

            // Calculate the position relative to the cell coordinates

            erasePolygon[0].setX(x1 - cell->x);
            erasePolygon[1].setX(x2 - cell->x);
            erasePolygon[2].setX(x3 - cell->x);

            erasePolygon[0].setY(y1 - cell->y);
            erasePolygon[1].setY(y2 - cell->y);
            erasePolygon[2].setY(y3 - cell->y);

            // Erase the polygon area

            QPainter painter(cell->img);
            painter.setRenderHint(QPainter::Antialiasing, true);
            painter.setCompositionMode(QPainter::CompositionMode_Clear);
            painter.setBrush(eraserBrush);
            painter.drawPolygon(&erasePolygon[0], 3);

//            painter.drawRect(
//                        erasePolygon[0].x(),
//                        erasePolygon[0].y(),
//                        erasePolygon[2].x() - erasePolygon[0].x(),
//                        erasePolygon[2].y() - erasePolygon[0].y()
//                    );
        }
    }

    // Notify book that this page has changed

    book->onPageEdited(this);

    lastX = x2;
    lastY = y2;

    c.stop();
    auto time = c.ellapsed_milli();
    print("time to draw:", time);
}

void Page::onPaint(QPainter & painter, QRect & rect, QColor * backgroundColor) {

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

//    if (highlightSize != 0) {
//        print("drawing highlight", lastX, lastY, highlightSize, highlightSize);
//        painter.setBrush(highlightBrush);
//        painter.drawEllipse(lastX - highlightSize / 2, lastY - highlightSize / 2, highlightSize, highlightSize);
//    }
}

Cell * Page::getCell(int i, int j, bool createOnMiss) {

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
