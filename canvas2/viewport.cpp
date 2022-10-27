#include "viewport.h"
#include "ui_viewport.h"

#include <QDateTime>
#include <QRect>
#include <QScreen>
#include <QShortcut>
#include <QThread>


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
    positionWindow(display->screen->geometry());
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


void Viewport::positionWindow(const QRect & g)
{
    qDebug("Positioning viewport at %d %d %d %d", g.left(), g.top(), g.width(), g.height());

    const int x = g.left();
    const int y = g.top();

    this->move(x, y);
    this->resize(g.size());

    mustRepaint = true;
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

    for (QPoint &p : cmd.points) {
        if (g.contains(p.x(), p.y())) {
            skip = false;
            break;
        }
    }

    if (skip)
        return;

    // Normalize to global coordinates

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
    // Check if this drawing is out of viewport

    QRect & g = this->display->internalGeometry;
    bool skip = true;

    for (QPoint &p : cmd.points) {
        if (g.contains(p.x(), p.y())) {
            skip = false;
            break;
        }
    }

    if (skip)
        return;

    // Normalize to global coordinates

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
    if (book != nullptr)
        mustRepaint = book->onPaint(painter, this->display->internalGeometry);
}


void Viewport::asyncUpdate() {
    mustRepaint = true;
}

ScalableDisplay *Viewport::getDisplay()
{
    return display;
}

void Viewport::setDisplay(ScalableDisplay * display)
{
    this->display = display;
    positionWindow(display->screen->geometry());
}
