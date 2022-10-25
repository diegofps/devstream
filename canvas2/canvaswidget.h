#ifndef CANVASWIDGET_H
#define CANVASWIDGET_H

#include <QWidget>
#include <QOpenGLWidget>
#include <QTimer>

#include <thread>

class CanvasWidgetListener {
public:
    virtual void onPaint(QPainter & painter) = 0;
};

class CanvasWidget : public QOpenGLWidget
{
public:
    CanvasWidget(QWidget * parent = nullptr);
    void setListener(CanvasWidgetListener *listener);
    void paintEvent(QPaintEvent *event);
    void animate();
//    void asyncUpdate();

private:
    CanvasWidgetListener * listener;
//    bool mustRefresh;
//    QTimer timer;
    std::thread mythread;

};

#endif // CANVASWIDGET_H
