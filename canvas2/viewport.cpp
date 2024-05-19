#include "viewport.h"
#include "ui_viewport.h"

#include <QDateTime>
#include <QFontDatabase>
#include <QRect>
#include <QShortcut>
#include <QThread>



Viewport::Viewport(ScalableDisplay *display, NotificationPool * notificationPool)
    : QMainWindow(nullptr),

      ui(new Ui::MainWindow),
      book(nullptr),
      display(display),
      notificationPool(notificationPool),
      timer(this),
      mustRepaint(true)
{
    ui->setupUi(this);
    ui->canvas->setListener(this);

    configureWindowProperties();
    positionWindow(display->internalGeometry);
    show();

    connect(&timer, &QTimer::timeout, this, &Viewport::animate);
    timer.start(20);

//    QFontDatabase db;
//    QStringList const families = db.families();
//    for (auto fam : families)
//        qDebug() << "Font family:" << fam;
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

    book->currentPage()->erase(cmd);
    asyncUpdate();
}

void Viewport::onPaint(QPainter & painter) {
    QRect & geometry = display->internalGeometry;

    if (book != nullptr)
        mustRepaint = book->onPaint(painter, geometry);

    notificationPool->onPaint(painter, geometry);
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
    positionWindow(display->internalGeometry);
}
