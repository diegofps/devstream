#include "viewport.h"
#include "ui_mainwindow.h"

#include <QDateTime>
#include <QRect>
#include <QScreen>
#include <QShortcut>
#include <QThread>
#include <wup/wup.hpp>


Viewport::Viewport(ScalableDisplay *display)
    : QMainWindow(nullptr),

      ui(new Ui::MainWindow),
      book(nullptr),
      display(display)
{
    ui->setupUi(this);
    ui->canvas->setListener(this);

    configureWindowProperties();
    positionWindow(display->screen);

    show();
}

Viewport::~Viewport()
{
    delete ui;
}

void Viewport::setBook(Book *book)
{
    this->book = book;
    update();
}


void Viewport::positionWindow(QScreen *screen)
{
    QRect g = screen->geometry();

    const int x = g.left();
    const int y = g.top();

    this->move(x, y);
    this->resize(g.size());
}

void Viewport::configureWindowProperties()
{
    setAttribute(Qt::WA_NoSystemBackground, true);
    setAttribute(Qt::WA_TranslucentBackground, true);

    setWindowFlags(Qt::Dialog
                   | Qt::MSWindowsFixedSizeDialogHint
                   | Qt::FramelessWindowHint
                   | Qt::WindowStaysOnTopHint
    );

    setWindowFlags(windowFlags()
                   | Qt::WindowDoesNotAcceptFocus
                   | Qt::WindowTransparentForInput
                   | Qt::X11BypassWindowManagerHint
    );

}

QRect Viewport::setHighlightPosition(int size, int x1, int y1) {

    QRect & g = this->display->internalGeometry;

    if (!g.contains(x1, y1))
        return QRect();

    QRect updateArea(
                x1 - size / 2,
                y1 - size / 2,
                x1 + size / 2,
                y1 + size / 2);

    auto x = g.left();
    auto y = g.top();

    x1 = x + (x1 - x) * this->display->normX;
    y1 = y + (y1 - y) * this->display->normY;

    book->currentPage()->setHighlightPosition(size, x1, y1);

    QMetaObject::invokeMethod(this, "redraw", Qt::AutoConnection,
                              Q_ARG(int, updateArea.left()),
                              Q_ARG(int, updateArea.top()),
                              Q_ARG(int, updateArea.width()),
                              Q_ARG(int, updateArea.height()));

    return updateArea;
}

QRect Viewport::draw(int x1, int y1, int x2, int y2, int size, QColor *color) {

    QRect & g = this->display->internalGeometry;

    if (!g.contains(x1, y1) && !g.contains(x2,y2))
        return QRect();

    QRect updateArea(
                std::min(x1,x2),
                std::min(y1,y2),
                std::max(x1,x2)-std::min(x1,x2),
                std::max(y1,y2)-std::min(y1,y2));

    auto x = g.left();
    auto y = g.top();

    x1 = x + (x1 - x) * this->display->normX;
    x2 = x + (x2 - x) * this->display->normX;
    y1 = y + (y1 - y) * this->display->normY;
    y2 = y + (y2 - y) * this->display->normY;

    book->currentPage()->draw(x1, y1, x2, y2, size, color);

    wup::print("updateArea:", updateArea.left(), updateArea.top(), updateArea.width(), updateArea.height());
    QMetaObject::invokeMethod(this, "redraw", Qt::AutoConnection,
                              Q_ARG(int, updateArea.left()),
                              Q_ARG(int, updateArea.top()),
                              Q_ARG(int, updateArea.width()),
                              Q_ARG(int, updateArea.height()));

    return updateArea;
}

QRect Viewport::erase(int x1, int y1, int x2, int y2, int size) {
    QRect updateArea = this->draw(x1, y1, x2, y2, size, nullptr);
    return updateArea;
}

void Viewport::onPaint(QPainter & painter) {
    if (book != nullptr)
        book->onPaint(painter, this->display->internalGeometry);
}

void Viewport::redraw(int left, int top, int width, int height)
{
    ui->canvas->update();
//    ui->canvas->repaint(left, top, width, height);
//    QThread::msleep(10);
}
