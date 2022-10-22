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
    void draw(int x1, int y1, int x2, int y2, int size, QColor &color);
    void erase(int x1, int y1, int x2, int y2, int size);
    void onPaint(QPainter &painter);
    void update(QRect * rect);

private:
    void positionWindow(QScreen *screen);
    void configureWindowProperties();

private:
    Ui::MainWindow *ui;
    Book *book;
    ScalableDisplay *display;

};

#endif // VIEWPORT_H
