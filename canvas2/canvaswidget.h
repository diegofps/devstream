#ifndef CANVASWIDGET_H
#define CANVASWIDGET_H

#include <QWidget>

class CanvasWidgetListener {
public:
    virtual void onPaint(QPaintEvent & event, QPainter & painter) = 0;
};

class CanvasWidget : public QWidget
{
public:
    CanvasWidget(QWidget * parent = nullptr);
    void paintEvent(QPaintEvent *);
    void setListener(CanvasWidgetListener *listener);

private:
    CanvasWidgetListener * listener;

};

#endif // CANVASWIDGET_H
