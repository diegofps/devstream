#include "viewport.h"
#include "ui_viewport.h"

#include <QDateTime>
#include <QRect>
#include <QShortcut>
#include <QThread>


struct Region {
    int _left, _top, _right, _bottom;
    int left() const { return _left; }
    int top() const { return _top; }
    int right() const { return _right; }
    int bottom() const { return _bottom; }
};


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

    notificationPen.setColor(qRgba(255,255,255,64));
    notificationBrush.setColor(qRgba(128,0,0,255));
    notificationBrush.setStyle(Qt::SolidPattern);

    configureWindowProperties();
    positionWindow(display->internalGeometry);
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

    if (notification == "")
        return;

    Region const padding {40,100,50,40};
    Region const margin {20,10,20,10};
    qreal const round = 10.0;

    QFont const & font = painter.font();
    QFontMetrics fm(font);
    QRect messageSize = fm.boundingRect(notification);

    QRect rect(geometry.width() - margin.left() - margin.right() - messageSize.width() - padding.right(),
               padding.top(),
               messageSize.width() + margin.left() + margin.right(),
               messageSize.height() + margin.top() + margin.bottom());

    painter.setPen(Qt::NoPen);
    painter.setBrush(notificationBrush);
    painter.drawRoundedRect(rect, round, round);

    QPoint point(geometry.width() - messageSize.width() - padding.right() - margin.right(),
                 padding.top() + margin.top() + messageSize.height() - fm.underlinePos());

    painter.setPen(notificationPen);
    painter.setBrush(Qt::NoBrush);
    painter.drawText(point, notification);
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

void Viewport::setNotification(QString notification)
{
    this->notification = notification;
    asyncUpdate();
}
