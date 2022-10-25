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

void Book::changePage(ChangePageCommand & cmd) {
    int oldPageIndex = pageIndex;

    pageIndex += cmd.offset;

    if (pageIndex < 0)
        pageIndex = 0;

    if (pageIndex > pages.size())
        pageIndex = pages.size();

    if (pageIndex == oldPageIndex)
        return;

    core->onPageChanged(this, currentPage());
}

void Book::setVisible(bool visible) {
    this->visible = visible;
    core->onPageChanged(this, currentPage());
}

void Book::movePage(MovePageCommand & cmd) {
    currentPage()->move(cmd);
}

bool Book::onPaint(QPainter & painter, QRect & screenRect) {
    if (!visible)
        return false;

    if (opaque)
        return currentPage()->onPaint(painter, screenRect, &backgroundColor);
    else
        return currentPage()->onPaint(painter, screenRect, nullptr);
}
