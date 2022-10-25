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
    viewXSmooth(0),
    viewYSmooth(0),
    highlightSize(5),
    highlightSizeSmooth(highlightSize),
    highlightStart(0),
    highlightEnd(0),
    highlightX(0),
    highlightY(0)
{
    eraserPen.setCapStyle(Qt::PenCapStyle::RoundCap);
    eraserPen.setStyle(Qt::PenStyle::SolidLine);
    eraserPen.setJoinStyle(Qt::PenJoinStyle::RoundJoin);

    inkPen.setCapStyle(Qt::PenCapStyle::RoundCap);
    inkPen.setStyle(Qt::PenStyle::SolidLine);
    inkPen.setCapStyle(Qt::PenCapStyle::RoundCap);

    highlightBrush.setStyle(Qt::BrushStyle::SolidPattern);
    highlightBrush.setColor(QColor(0,0,255, 128));

    eraserBrush.setStyle(Qt::BrushStyle::SolidPattern);
    eraserBrush.setColor(QColor(0,0,0));

}

void Page::move(MovePageCommand & cmd) {
//    print("Moving viewport", rx, ry, viewX, viewY);

    std::lock_guard<std::mutex> lock(drawing);
    viewX += cmd.point.x();
    viewY += cmd.point.y();
}

void Page::highlightPosition(ChangePenSizeCommand & cmd) {
//    print("setting highlight", cmd.size, cmd.x, cmd.y);

    highlightSize  = cmd.size;
    highlightStart = QDateTime::currentMSecsSinceEpoch();
    highlightEnd   = highlightStart + 2000;
    highlightX     = cmd.x;
    highlightY     = cmd.y;
}

void Page::draw(DrawCommand & cmd, int size, QColor * color) {

    std::lock_guard<std::mutex> lock(drawing);
    Clock c;

    // Convert from multidisplay coordinates to world coordinates

    for (QPoint &p : cmd.points) {
        p.setX(p.x() - viewX);
        p.setY(p.y() - viewY);
    }

    int min_x=cmd.points[0].x(), min_y=cmd.points[0].y();
    int max_x=min_x, max_y=min_y;

    for (QPoint &p : cmd.points) {
        if (p.x() < min_x)
            min_x = p.x();
        if (p.x() > max_x)
            max_x = p.x();

        if (p.y() < min_y)
            min_y = p.y();
        if (p.y() > max_y)
            max_y = p.y();
    }

    // Obtain indexes that may intersect the area
    int size_2 = size % 2 ? size / 2 + 1 : size;

    int i1 = (min_y - CELL_SIZE - size_2) / CELL_SIZE;
    int i2 = ceil((max_y + CELL_SIZE + size_2) / double(CELL_SIZE));

    int j1 = (min_x - CELL_SIZE - size_2) / CELL_SIZE;
    int j2 = ceil((max_x + CELL_SIZE + size_2) / double(CELL_SIZE));

    // Create the pen we will use to draw

    inkPen.setWidth(size);
    inkPen.setColor(*color);

    // Paint all cells in the indexes selected

    for (int i=i1;i<i2;++i) {
        for (int j=j1;j<j2;++j) {
            Cell * cell = getCell(i, j, true);

            // Calculate the position relative to the cell coordinates

            for (QPoint &p : cmd.points) {
                p.setX(p.x() - cell->x);
                p.setY(p.y() - cell->y);
            }

            // Draw the line

            QPainter painter(cell->img);
            painter.setRenderHint(QPainter::Antialiasing, true);
            painter.setPen(inkPen);
            painter.drawLines(cmd.points);

            for (QPoint &p : cmd.points) {
                p.setX(p.x() + cell->x);
                p.setY(p.y() + cell->y);
            }
        }
    }

    // Notify book that this page has changed

    book->onPageEdited(this);

//    c.stop();
//    auto time = c.ellapsed_milli();
//    print("time to draw:", time);

}

void Page::erase(EraseCommand & cmd) {
//    print("Page::eraser", x1, y1, x2, y2, x3, y3);

    std::lock_guard<std::mutex> lock(drawing);

    Clock c;

    // Convert from multidisplay coordinates to world coordinates

    for (QPoint &p : cmd.points) {
        p.setX(p.x() - viewX);
        p.setY(p.y() - viewY);
    }

    int min_x=cmd.points[0].x(), min_y=cmd.points[0].y();
    int max_x=min_x, max_y=min_y;

    for (QPoint &p : cmd.points) {
        if (p.x() < min_x)
            min_x = p.x();
        if (p.x() > max_x)
            max_x = p.x();

        if (p.y() < min_y)
            min_y = p.y();
        if (p.y() > max_y)
            max_y = p.y();
    }

    // Obtain indexes that may intersect the area

    int i1 = (min_y - CELL_SIZE) / CELL_SIZE;
    int i2 = ceil((max_y + CELL_SIZE) / double(CELL_SIZE));

    int j1 = (min_x - CELL_SIZE) / CELL_SIZE;
    int j2 = ceil((max_x + CELL_SIZE) / double(CELL_SIZE));

    // Paint all cells in the indexes selected

    for (int i=i1;i<i2;++i) {
        for (int j=j1;j<j2;++j) {
            Cell * cell = getCell(i, j, true);

            // Calculate the position relative to the cell coordinates

            for (QPoint &p : cmd.points) {
                p.setX(p.x() - cell->x);
                p.setY(p.y() - cell->y);
            }

            // Erase the polygon area

            QPainter painter(cell->img);
            painter.setRenderHint(QPainter::Antialiasing, true);
            painter.setCompositionMode(QPainter::CompositionMode_Clear);
            painter.setBrush(eraserBrush);
//            painter.drawPolygon(&erasePolygon[0], 3);

            painter.drawPolygon(cmd.points.data(), cmd.points.size());

            for (QPoint &p : cmd.points) {
                p.setX(p.x() + cell->x);
                p.setY(p.y() + cell->y);
            }
        }
    }

    // Notify book that this page has changed

    book->onPageEdited(this);

//    c.stop();
//    auto time = c.ellapsed_milli();
//    print("time to erase:", time);
}

bool Page::onPaint(QPainter & painter, QRect & rect, QColor * backgroundColor) {

    std::lock_guard<std::mutex> lock(drawing);

    if (backgroundColor != nullptr)
        painter.fillRect(0, 0, rect.width(), rect.height(), *backgroundColor);

    // Convert from multidisplay coordinates to world coordinates

    int x = rect.left() - viewXSmooth;
    int y = rect.top() - viewYSmooth;

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

    auto now = QDateTime::currentMSecsSinceEpoch();

    bool result = false;

    if (now < highlightEnd)
    {
        // Step
        result = true;
        highlightSizeSmooth = highlightSizeSmooth + (highlightSize - highlightSizeSmooth) / 4;

        // Paint
        highlightBrush.setColor(inkPen.color());
        painter.setBrush(highlightBrush);
        painter.setPen(Qt::NoPen);

        int size_2 = highlightSizeSmooth / 2;

//        print("drawing ellipse", highlightX, highlightY, highlightSize, highlightSizeSmooth);

        painter.drawEllipse(
                    highlightX - size_2 - rect.left(), highlightY - size_2 - rect.top() - 20,
                    highlightSizeSmooth, highlightSizeSmooth);
    }

    if (viewX != viewXSmooth || viewY != viewYSmooth)
    {
        result = true;

        viewXSmooth = viewXSmooth + (viewX - viewXSmooth) / 3;
        viewYSmooth = viewYSmooth + (viewY - viewYSmooth) / 3;

        if (abs(viewX - viewXSmooth) < 2)
            viewXSmooth = viewX;

        if (abs(viewY - viewYSmooth) < 2)
            viewYSmooth = viewY;
    }

    return result;
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
