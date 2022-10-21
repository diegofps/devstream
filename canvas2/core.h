#ifndef CORE_H
#define CORE_H

#include "book.h"

#include <QObject>
#include <QScreen>
#include <QList>
#include <mainwindow.h>
#include <thread>
#include <page.h>

const int MAX_BRUSH_INDEX = 10;
const int MIN_BRUSH_INDEX = 2;
const double BRUSH_BASE = 1.5;

const int MAX_ERASER_INDEX = 10;
const int MIN_ERASER_INDEX = 2;
const double ERASER_BASE = 1.5;


enum PageMode {
    MODE_TRANSPARENT = 1,
    MODE_OPAQUE      = 2,
    MODE_PASSTHROUGH = 3,
    MODE_DISABLED    = 4,
};


class Core : public QObject, public BookListener
{
    Q_OBJECT
public:
    explicit Core(QObject *parent = nullptr);

    void onPageChanged(Book *book, Page * page);
    void onRepaintPage(Book *book, Page * page, QRect * rect);

signals:

public slots:
    void changeBrushSize(int size);
    void changeEraserSize(int size);
    void showPreviousPage();
    void showNextPage();
    void setPageMode(int pageMode);
    void movePage(int rx, int ry);
    void draw(int x1, int y1, int x2, int y2);
    void erase(int x1, int y1, int x2, int y2);

private:

    QList<MainWindow*> viewports;

    PageMode pageMode;
    Book transparentBook;
    Book opaqueBook;
    Book * activeBook;
    std::thread reader;

    int size_brush_index;
    int size_eraser_index;

    int size_brush;
    int size_eraser;

    QColor brush_color;

    int width_space;
    int height_space;

    QList<std::function<void(void)>> callbacksCopy;

};

#endif // CORE_H
