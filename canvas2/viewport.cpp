#include "viewport.h"
#include "ui_mainwindow.h"

#include <QRect>
#include <QScreen>
#include <QShortcut>
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
    wup::print("Inside Viewport's setBook");
    this->book = book;
    this->update(nullptr);
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

void Viewport::draw(int x1, int y1, int x2, int y2, int size, QColor &color) {

    auto x = this->display->internalGeometry.left();
    auto y = this->display->internalGeometry.top();

    x1 = x + (x1-x)*this->display->normX;
    x2 = x + (x2-x)*this->display->normX;
    y1 = y + (y1-y)*this->display->normY;
    y2 = y + (y2-y)*this->display->normY;

    book->currentPage()->draw(x1, y1, x2, y2, size, color);
}

void Viewport::erase(int x1, int y1, int x2, int y2, int size) {
    book->currentPage()->erase(x1, y1, x2, y2, size);
}

void Viewport::onPaint(QPainter & painter) {
//    wup::print("MainWindow's onPaint called");
    if (book != nullptr)
        book->onPaint(painter, this->display->internalGeometry);
}

void Viewport::update(QRect * rect) {
//    wup::print("repainting");
//    QMainWindow::update();
    QMetaObject::invokeMethod(ui->canvas, "update", Qt::AutoConnection);

//    ui->canvas->update();
//    ui->canvas->repaint(*rect);
}
