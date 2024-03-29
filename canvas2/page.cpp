#include "page.h"

#include <QDateTime>
#include <QPainter>
#include <QBrush>
#include <QImage>


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
    highlightY(0),
    historyPosition(1)
{
    history.append(new PageChanges());

    eraserPen.setCapStyle(Qt::PenCapStyle::RoundCap);
    eraserPen.setStyle(Qt::PenStyle::SolidLine);
    eraserPen.setJoinStyle(Qt::PenJoinStyle::RoundJoin);

    inkPen.setCapStyle(Qt::PenCapStyle::RoundCap);
    inkPen.setStyle(Qt::PenStyle::SolidLine);
    inkPen.setCapStyle(Qt::PenCapStyle::RoundCap);

    highlightBrush.setStyle(Qt::BrushStyle::SolidPattern);
    highlightBrush.setColor(QColor(0, 0, 255, 128));

    eraserBrush.setStyle(Qt::BrushStyle::SolidPattern);
    eraserBrush.setColor(QColor(0, 0, 0));
}

void Page::move(MovePageCommand & cmd)
{
    std::lock_guard<std::mutex> lock(drawing);

    viewX += cmd.point.x();
    viewY += cmd.point.y();
}

void Page::highlightPosition(ChangePenSizeCommand & cmd)
{
    std::lock_guard<std::mutex> lock(drawing);

    highlightSize  = cmd.size;
    highlightStart = QDateTime::currentMSecsSinceEpoch();
    highlightEnd   = highlightStart + 2000;
    highlightX     = cmd.x;
    highlightY     = cmd.y;
}

void Page::draw(DrawCommand & cmd, int size, QColor * color)
{
    std::lock_guard<std::mutex> lock(drawing);

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

    int size_2 = size % 2 ? size / 2 + 1 : size / 2;

    int i1 = floor((min_y - size_2) / double(CELL_SIZE));
    int i2 = ceil ((max_y + size_2) / double(CELL_SIZE));

    int j1 = floor((min_x - size_2) / double(CELL_SIZE));
    int j2 = ceil ((max_x + size_2) / double(CELL_SIZE));

    // Create the pen we will use to draw

    inkPen.setWidth(size);
    inkPen.setColor(*color);

    // Paint all cells in the indexes selected

    for (int i=i1;i<i2;++i) {
        for (int j=j1;j<j2;++j) {
            QPair<int, int> key(i,j);
            destroyFuture();
            CellChanges * chp = history[historyPosition-1]->get(key, cells);
            Cell * cell = getCell(key, true);

            // Calculate the position relative to the cell coordinates

            for (QPoint & p : cmd.points) {
                p.setX(p.x() - cell->x());
                p.setY(p.y() - cell->y());
            }

            // Draw the line

            QPainter painter(cell->image());
            painter.setRenderHint(QPainter::Antialiasing, true);
            painter.setPen(inkPen);
            painter.drawPolyline(cmd.points);

            // Update the history point cache

            chp->setAfter(cell->image());

            // Move p to its previous value, the next cell will move it correctly

            for (QPoint & p : cmd.points) {
                p.setX(p.x() + cell->x());
                p.setY(p.y() + cell->y());
            }
        }
    }

    // Notify book that this page has changed

    book->onPageEdited(this);
}

void Page::erase(EraseCommand & cmd)
{
    std::lock_guard<std::mutex> lock(drawing);

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

    int i1 = floor((min_y - CELL_SIZE) / double(CELL_SIZE));
    int i2 = ceil ((max_y + CELL_SIZE) / double(CELL_SIZE));

    int j1 = floor((min_x - CELL_SIZE) / double(CELL_SIZE));
    int j2 = ceil ((max_x + CELL_SIZE) / double(CELL_SIZE));

    // Paint all cells in the indexes selected

    for (int i=i1;i<i2;++i) {
        for (int j=j1;j<j2;++j) {
            QPair<int, int> key(i,j);
            destroyFuture();
            CellChanges * chp = history[historyPosition-1]->get(key, cells);
            Cell * cell = getCell(key, true);

            // Calculate the position relative to the cell coordinates

            for (QPoint &p : cmd.points) {
                p.setX(p.x() - cell->x());
                p.setY(p.y() - cell->y());
            }

            // Erase the polygon area

            QPainter painter(cell->image());
            painter.setRenderHint(QPainter::Antialiasing, true);
            painter.setCompositionMode(QPainter::CompositionMode_Clear);
            painter.setBrush(eraserBrush);
            painter.drawPolygon(cmd.points.data(), cmd.points.size());

            // Update the history point cache

            chp->setAfter(cell->image());

            // Move p to its previous value, the next cell will move it correctly

            for (QPoint &p : cmd.points) {
                p.setX(p.x() + cell->x());
                p.setY(p.y() + cell->y());
            }
        }
    }

    // Notify book that this page has changed

    book->onPageEdited(this);
}

bool Page::onPaint(QPainter & painter, QRect & rect, QColor * backgroundColor)
{
    std::lock_guard<std::mutex> lock(drawing);

    if (backgroundColor != nullptr)
        painter.fillRect(0, 0, rect.width(), rect.height(), * backgroundColor);

    // Convert from multidisplay coordinates to world coordinates

    int x = rect.left() - viewXSmooth;
    int y = rect.top()  - viewYSmooth;

    // Obtain indexes that may intersect the area

    int i1 = floor((y - CELL_SIZE)     / double(CELL_SIZE));
    int i2 = ceil ((y + rect.height()) / double(CELL_SIZE));

    int j1 = floor((x - CELL_SIZE)    / double(CELL_SIZE));
    int j2 = ceil ((x + rect.width()) / double(CELL_SIZE));

    for (int i=i1;i<i2;++i) {
        for (int j=j1;j<j2;++j) {
            QPair<int, int> key(i,j);
            Cell * cell = getCell(key, false);

            if (cell != nullptr)
                painter.drawImage(cell->x() - x, cell->y() - y, *cell->image());
        }
    }

    auto now = QDateTime::currentMSecsSinceEpoch();

    bool result = false;

    // Smooth animate and draw highlighted brush size

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

        painter.drawEllipse(
                    highlightX - size_2 - rect.left(), highlightY - size_2 - rect.top() - 20,
                    highlightSizeSmooth, highlightSizeSmooth);
    }

    // Smooth animation when the page is moved

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

Cell * Page::getCell(QPair<int,int> & key, bool createOnMiss)
{
    // Debug mode

    if (false) {

        auto it = cells.find(key);

        if (it != cells.end())
            return *it;

        Cell *cell = new Cell(key, false);
        cells[key] = cell;
        return cell;
    }

    else {
        auto it = cells.find(key);

        if (it != cells.end())
            return *it;

        if (!createOnMiss)
            return nullptr;

        Cell *cell = new Cell(key, true);
        cells[key] = cell;
        return cell;
    }
}

void Page::undo(UndoCommand & cmd)
{
    if (cmd.offset == 0)
        return;

    std::lock_guard<std::mutex> lock(drawing);

    if (cmd.offset > 0 ) {
        for (int i=0;i!= cmd.offset;++i)
            nextHistoryPoint();
    } else {
        for (int i=0;i!=cmd.offset;--i)
            previousHistoryPoint();
    }
}

void Page::savePresent()
{
    std::lock_guard<std::mutex> lock(drawing);

    destroyFuture();

    if (history[historyPosition-1]->hasChanges()) {
        history.append(new PageChanges());
        historyPosition += 1;
        qDebug("Saving present, historyPosition is now at %d/%lld", historyPosition, history.size());
    } else {
        qDebug("Skiping save present, nothing to save");
    }
}

void Page::destroyFuture()
{
    if (historyPosition==history.size())
        return;

    qDebug("Destroying %lld future changes", history.size() - historyPosition);

    for (int i=historyPosition;i!=history.size();++i)
        delete history[i];

    history.resize(historyPosition);
    history.append(new PageChanges());
    historyPosition += 1;
}

void Page::previousHistoryPoint()
{
    if (historyPosition == 0)
        return;

    if (history[historyPosition-1]->hasChanges())
    {
        history[historyPosition-1]->undo(cells);
        historyPosition -= 1;
    }
    else
    {
        history[historyPosition-2]->undo(cells);
        historyPosition -= 2;
    }

    qDebug("Moving backward in time: %d/%lld", historyPosition, history.size());
}

void Page::nextHistoryPoint()
{
    if (historyPosition == history.size())
        return;

    history[historyPosition]->redo(cells);
    historyPosition += 1;

    if (historyPosition == history.size()-1)
        historyPosition += 1;

    qDebug("Moving forward in time: %d/%lld", historyPosition, history.size());
}
