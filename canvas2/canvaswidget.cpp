#include "canvaswidget.h"

#include <QPainter>
#include <wup/wup.hpp>

CanvasWidget::CanvasWidget(QWidget * parent) :
    QWidget(parent),
    listener(nullptr)
{

}

void CanvasWidget::setListener(CanvasWidgetListener * listener) {
    this->listener = listener;
}

void CanvasWidget::paintEvent(QPaintEvent *event)
{
    wup::print("paintEvent called");
    QPainter painter(this);
    painter.setRenderHint(QPainter::Antialiasing, true);

    if (listener != nullptr)
        listener->onPaint(*event, painter);
}
