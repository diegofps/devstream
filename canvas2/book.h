#ifndef BOOK_H
#define BOOK_H

#include <QList>
#include <QColor>
#include <page.h>

class Book;

class BookListener {
public:
    virtual void onPageChanged(Book * book, Page *page) = 0;
    virtual void onRepaintPage(Book * book, Page *page, QRect *rect) = 0;
};

class Book: public PageListener
{
public:
    Book(BookListener *listener, bool opaque);

    Page * currentPage();
    void onPageEdited(Page *page);
    void onRepaintPage(Page *page, QRect *rect);
    void showPreviousPage();
    void showNextPage();
    void setVisible(bool visible);
    void movePage(int rx, int ry);

private:
    BookListener *listener;
    QList<Page*> pages;
    int pageIndex;
    Page * extraPage;
    bool opaque;
    bool visible;
};

#endif // BOOK_H
