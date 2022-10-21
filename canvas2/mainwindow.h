#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include "canvaswidget.h"

#include <QMainWindow>
#include <page.h>

QT_BEGIN_NAMESPACE
namespace Ui { class MainWindow; }
QT_END_NAMESPACE

class MainWindow : public QMainWindow, public CanvasWidgetListener
{
    Q_OBJECT

public:
    MainWindow(QScreen *screen);
    ~MainWindow();

    void setPage(Page * page);
    void draw(int x1, int y1, int x2, int y2, int size, QColor &color);
    void erase(int x1, int y1, int x2, int y2, int size);
    void onPaint(QPainter &painter);
    void update(QRect * rect);

private:
    void positionWindow(QScreen *screen);
    void configureWindowProperties();

private:
    Ui::MainWindow *ui;
    Page *page;
    QRect screenRect;

};

typedef MainWindow Viewport;

#endif // MAINWINDOW_H
