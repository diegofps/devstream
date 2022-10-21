#include "canvaswidget.h"

#include <QOpenGLFunctions>
#include <QPainter>
#include <wup/wup.hpp>

CanvasWidget::CanvasWidget(QWidget * parent) :
    QOpenGLWidget(parent),
    listener(nullptr)
{

}

void CanvasWidget::setListener(CanvasWidgetListener * listener) {
    this->listener = listener;
}

void CanvasWidget::paintEvent(QPaintEvent *)
{
//    wup::print("paintEvent called");
    QPainter painter(this);

//    painter.setRenderHint(QPainter::Antialiasing, true);

    QOpenGLFunctions *f = context()->functions();
    f->glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT);
    f->glClearColor(0.0,0.0,0.0,0.0);

    if (listener != nullptr)
        listener->onPaint(painter);
}
