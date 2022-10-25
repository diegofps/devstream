#ifndef VIEWPORT_H
#define VIEWPORT_H

#include "book.h"
#include "canvaswidget.h"

#include <QMainWindow>
#include <scalabledisplay.h>

QT_BEGIN_NAMESPACE
namespace Ui { class MainWindow; }
QT_END_NAMESPACE

class Viewport : public QMainWindow, public CanvasWidgetListener
{
    Q_OBJECT

public:
    Viewport(ScalableDisplay *display);
    ~Viewport();

    void setBook(Book * book);
    QRect draw(int x1, int y1, int x2, int y2, int size, QColor * color);
    QRect erase(int x1, int y1, int x2, int y2, int size);
    void onPaint(QPainter &painter);
    QRect setHighlightPosition(int size, int x, int y);

public Q_SLOTS:
    void redraw(int left, int top, int width, int height);

private:
    void positionWindow(QScreen *screen);
    void configureWindowProperties();

private:
    Ui::MainWindow *ui;
    Book *book;
    ScalableDisplay *display;

};

#endif // VIEWPORT_H
