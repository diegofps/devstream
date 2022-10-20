#include "mainwindow.h"
#include "ui_mainwindow.h"

#include <QRect>
#include <QScreen>
#include <QShortcut>
#include <wup/wup.hpp>


MainWindow::MainWindow(QScreen *screen)
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
    configureStylesheet(false);

    show();
}

MainWindow::~MainWindow()
{
    delete ui;
}

void MainWindow::setPage(Page *page)
{
    wup::print("Inside Viewport's setPage");
    this->page = page;
    this->update();
}


void MainWindow::positionWindow(QScreen *screen)
{
    QRect g = screen->geometry();

    const int x = g.left();
    const int y = g.top();

    this->move(x, y);
    this->resize(g.size());
}

void MainWindow::configureWindowProperties()
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

void MainWindow::configureStylesheet(bool opaque)
{
    if (opaque) {
        setStyleSheet(
            "border: 0px;"
            "background-color: #ffcccccc;"
        );
    }
    else {
        setStyleSheet(
            "border: 0px;"
            "background-color: #11ffffff;"
        );
    }

}

void MainWindow::draw(int x1, int y1, int x2, int y2, int size, QColor &color) {
    page->draw(x1, y1, x2, y2, size, color);
//    repaint(x1, y1, x2-x1, y2-y1);
}

void MainWindow::erase(int x1, int y1, int x2, int y2, int size) {
    page->erase(x1, y1, x2, y2, size);
//    repaint(x1, y1, x2-x1, y2-y1);
}

void MainWindow::onPaint(QPaintEvent & event, QPainter & painter) {
//    wup::print("MainWindow's onPaint called");
    if (page != nullptr)
        page->onPaint(event, painter, screenRect);
}
