#include "book.h"
#include <wup/wup.hpp>

Book::Book(BookListener * listener, bool opaque) :
    core(listener),
    pageIndex(0),
    extraPage(nullptr),
    opaque(opaque),
    visible(true),
    backgroundColor("#ffdddddd")
{
    extraPage = new Page(this);
}

Page * Book::currentPage() {
    auto page = pageIndex == pages.size() ? extraPage : pages[pageIndex];
    return page;
}

void Book::onPageEdited(Page *page) {
    if (page == extraPage) {
        wup::print("extra page added");
        pages.append(extraPage);
        extraPage = new Page(this);
    }
}

void Book::showPreviousPage() {
    if (pageIndex != 0) {
        --pageIndex;
        core->onPageChanged(this, currentPage());
    }
}

void Book::showNextPage() {
    if (pageIndex != pages.size()) {
        ++pageIndex;
        core->onPageChanged(this, currentPage());
    }
}

void Book::setVisible(bool visible) {
    this->visible = visible;
    core->onPageChanged(this, currentPage());
}

void Book::movePage(int rx, int ry) {
    currentPage()->move(rx, ry);
}

void Book::onRepaintPage(Page *page, QRect *rect) {
    core->onRepaintPage(this, page, rect);
}

void Book::onPaint(QPainter & painter, QRect & screenRect) {
    if (!visible)
        return;

    if (opaque)
        currentPage()->onPaint(painter, screenRect, &backgroundColor);
    else
        currentPage()->onPaint(painter, screenRect, nullptr);
}
