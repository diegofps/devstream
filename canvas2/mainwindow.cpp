#include "mainwindow.h"
#include "ui_mainwindow.h"

#include <QRect>
#include <QScreen>
#include <QShortcut>
#include <wup/wup.hpp>


Viewport::MainWindow(QScreen *screen)
    : QMainWindow(nullptr),

      ui(new Ui::MainWindow),
      page(nullptr),
      screenRect(screen->geometry().left(), screen->geometry().top(),
           screen->geometry().width(), screen->geometry().height())
{
    ui->setupUi(this);
    ui->canvas->setListener(this);

    configureWindowProperties();
    positionWindow(screen);
//    configureStylesheet(false);

    show();
}

Viewport::~MainWindow()
{
    delete ui;
}

void Viewport::setPage(Page *page)
{
    wup::print("Inside Viewport's setPage");
    this->page = page;
    this->update();
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

void Viewport::configureStylesheet(bool opaque)
{
//    if (opaque) {
//        setStyleSheet(
//            "border: 0px;"
//            "background-color: #ffcccccc;"
//        );
//    }
//    else {
//        setStyleSheet(
//            "border: 0px;"
//            "background-color: #11ffffff;"
//        );
//    }

}

void Viewport::draw(int x1, int y1, int x2, int y2, int size, QColor &color) {
    page->draw(x1, y1, x2, y2, size, color);
//    repaint(x1, y1, x2-x1, y2-y1);
}

void Viewport::erase(int x1, int y1, int x2, int y2, int size) {
    page->erase(x1, y1, x2, y2, size);
//    repaint(x1, y1, x2-x1, y2-y1);
}

void Viewport::onPaint(QPainter & painter) {
//    wup::print("MainWindow's onPaint called");
    if (page != nullptr)
        page->onPaint(painter, screenRect);
}

void Viewport::update() {
    QMainWindow::update();
    ui->canvas->update();
}
