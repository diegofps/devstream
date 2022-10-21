#include "book.h"
#include <wup/wup.hpp>

Book::Book(BookListener * listener, bool opaque) :
    listener(listener),
    pageIndex(0),
    extraPage(nullptr),
    opaque(opaque),
    visible(true)
{
    extraPage = new Page(this, opaque);
}

Page * Book::currentPage() {
    auto page = pageIndex == pages.size() ? extraPage : pages[pageIndex];
    return page;
}

void Book::onPageEdited(Page *page)
{
    if (page == extraPage) {
        pages.append(extraPage);
        extraPage = new Page(this, opaque);
    }
}

void Book::showPreviousPage()
{
    if (pageIndex != 0) {
        --pageIndex;
        listener->onRepaintPage(this, currentPage(), nullptr);
    }
}

void Book::showNextPage()
{
    if (pageIndex != pages.size()) {
        ++pageIndex;
        listener->onRepaintPage(this, currentPage(), nullptr);
    }
}

void Book::setVisible(bool visible) {
    this->visible = visible;
    listener->onRepaintPage(this, currentPage(), nullptr);
}

void Book::movePage(int rx, int ry) {
    currentPage()->move(rx, ry);
}

void Book::onRepaintPage(Page *page, QRect *rect)
{
    listener->onRepaintPage(this, page, rect);
}
