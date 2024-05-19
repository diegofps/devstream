#ifndef VIEWPORT_H
#define VIEWPORT_H

#include "book.h"
#include "canvaswidget.h"
#include "commands.h"
#include "notificationpool.h"

#include <QMainWindow>
#include <scalabledisplay.h>

QT_BEGIN_NAMESPACE
namespace Ui { class MainWindow; }
QT_END_NAMESPACE

class Viewport : public QMainWindow, public CanvasWidgetListener
{
    Q_OBJECT

public:
    Viewport(ScalableDisplay *display, NotificationPool * nPool);
    ~Viewport();

    void setBook(Book * book);
    void draw(DrawCommand cmd, int size, QColor * color);
    void erase(EraseCommand cmd);
    void onPaint(QPainter & painter);
    void highlightPosition(ChangePenSizeCommand cmd);
    void asyncUpdate();
    ScalableDisplay * getDisplay();
    void setDisplay(ScalableDisplay *display);

public Q_SLOTS:
    void animate();
    void positionWindow(const QRect & g);

private:
    void configureWindowProperties();

private:
    Ui::MainWindow *ui;
    Book *book;
    ScalableDisplay *display;
    NotificationPool * notificationPool;
    QTimer timer;
    bool mustRepaint;

};

#endif // VIEWPORT_H
