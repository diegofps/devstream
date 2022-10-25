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
      display(display),
      timer(this),
      mustRepaint(true)
{
    ui->setupUi(this);
    ui->canvas->setListener(this);

    configureWindowProperties();
    positionWindow(display->screen);

    show();

    connect(&timer, &QTimer::timeout, this, &Viewport::animate);
    timer.start(20);
}

Viewport::~Viewport()
{
    delete ui;
}

void Viewport::animate() {
    if (mustRepaint) {
        mustRepaint = false;
        ui->canvas->update();
    }
}

void Viewport::setBook(Book *book)
{
    this->book = book;
    mustRepaint = true;
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

void Viewport::highlightPosition(ChangePenSizeCommand cmd) {

    QRect & g = this->display->internalGeometry;

    if (!g.contains(cmd.x, cmd.y))
        return;

    auto x = g.left();
    auto y = g.top();

    cmd.x = x + (cmd.x - x) * this->display->normX;
    cmd.y = y + (cmd.y - y) * this->display->normY;

    book->currentPage()->highlightPosition(cmd);
    asyncUpdate();
}

void Viewport::draw(DrawCommand cmd, int size, QColor *color) {

    // Check if this drawing is out of viewport

    QRect & g = this->display->internalGeometry;
    bool skip = true;

//    wup::print("geometry is", g.left(), g.top(), g.width(), g.height());

    for (QPoint &p : cmd.points) {
//        wup::print("checking", p.x(), p.y());

        if (g.contains(p.x(), p.y())) {            
//            wup::print("contained!");

            skip = false;
            break;
        }
    }

    if (skip)
        return;

    // Normalize to global coordinates
//    wup::print("Didn't skip");

    auto x = g.left();
    auto y = g.top();

    for (QPoint &p : cmd.points) {
        p.setX(x + (p.x() - x) * this->display->normX);
        p.setY(y + (p.y() - y) * this->display->normY);
    }

    // Ask the book to draw it

    book->currentPage()->draw(cmd, size, color);

    // Update canvas

    asyncUpdate();
}

void Viewport::erase(EraseCommand cmd) {
//    QRect updateArea = this->draw(x1, y1, x2, y2, x3, y3, nullptr);

    // Check if this drawing is out of viewport

    QRect & g = this->display->internalGeometry;
    bool skip = true;

//    wup::print("geometry is", g.left(), g.top(), g.width(), g.height());

    for (QPoint &p : cmd.points) {
//        wup::print("checking", p.x(), p.y());

        if (g.contains(p.x(), p.y())) {
//            wup::print("contained!");

            skip = false;
            break;
        }
    }

    if (skip)
        return;

    // Normalize to global coordinates
//    wup::print("Didn't skip");

    auto x = g.left();
    auto y = g.top();

    for (QPoint &p : cmd.points) {
        p.setX(x + (p.x() - x) * this->display->normX);
        p.setY(y + (p.y() - y) * this->display->normY);
    }

    book->currentPage()->erase(cmd);
    asyncUpdate();
}

void Viewport::onPaint(QPainter & painter) {
//    mustRepaint = false;
    if (book != nullptr) {
//        wup::print("repainting");
        mustRepaint = book->onPaint(painter, this->display->internalGeometry);
    }
}


void Viewport::asyncUpdate() {
    mustRepaint = true;
}
