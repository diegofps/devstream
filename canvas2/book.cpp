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
    wup::print("Getting current page", pages.size(), pageIndex);
    auto page = pageIndex == pages.size() ? extraPage : pages[pageIndex];
    wup::print("got current page");
    return page;
}

void Book::onPageEdited(Page *page)
{
    if (page == extraPage) {
        pages.append(extraPage);
        extraPage = new Page(this, opaque);
    }
}

void Book::onRepaintPage(Page *page)
{
    listener->onRepaintPage(this, page);
}

void Book::showPreviousPage()
{
    if (pageIndex != 0) {
        --pageIndex;
        listener->onRepaintPage(this, currentPage());
    }
}

void Book::showNextPage()
{
    if (pageIndex != pages.size()) {
        ++pageIndex;
        listener->onRepaintPage(this, currentPage());
    }
}

void Book::setVisible(bool visible) {
    this->visible = visible;
    listener->onRepaintPage(this, currentPage());
}

void Book::movePage(int rx, int ry) {
    currentPage()->move(rx, ry);
}
