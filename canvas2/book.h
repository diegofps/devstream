#ifndef BOOK_H
#define BOOK_H

#include <QList>
#include <QColor>
#include <page.h>

class Book;

class BookListener {
public:
    virtual void onPageChanged(Book * book, Page *page) = 0;
};

class Book: public PageListener
{
public:
    Book(BookListener *listener, bool opaque);

    Page * currentPage();
    void onPageEdited(Page *page);
    void changePage(ChangePageCommand & cmd);
    void setVisible(bool visible);
    void movePage(MovePageCommand & cmd);
    bool onPaint(QPainter &painter, QRect &screenRect);

private:
    BookListener *core;
    QList<Page*> pages;
    int pageIndex;
    Page * extraPage;
    bool opaque;
    bool visible;
    QColor backgroundColor;
};

#endif // BOOK_H
