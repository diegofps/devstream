#include "core.h"

#include <viewport.h>

#include <sys/stat.h>
#include <unistd.h>
#include <iostream>
#include <fstream>
#include <wup/wup.hpp>

#include <QApplication>
#include <QRegularExpression>

const char * named_pipe = "/tmp/shadow_xppen_deco_pro";

using wup::print;


QString exec(QString cmd) {
    QByteArray ba = cmd.toLocal8Bit();
    FILE * process = popen(ba.data(), "r");
    std::unique_ptr<FILE, decltype(&pclose)> pipe(process, pclose);
    std::array<char, 512> buffer;
    QString result;

    if (!pipe)
        throw std::runtime_error("popen() failed!");

    while (fgets(buffer.data(), buffer.size(), pipe.get()) != nullptr)
        result += buffer.data();

    return result;
}


class ScalableDisplay {
public:

    ScalableDisplay(QString port, QRect internalRect) :
        port(port),
        internalGeometry(internalRect),
        externalGeometry(0,0,0,0),
        scaleX(0),
        scaleY(0),
        serialNumber(""),
        displaySerialNumber(""),
        displayProductName("")
    { }

    QString port;
    QRect internalGeometry;
    QRect externalGeometry;
    double scaleX;
    double scaleY;
    QString serialNumber;
    QString displaySerialNumber;
    QString displayProductName;
    QList<QString> edidData;
};


QList<ScalableDisplay*> parseDisplays() {

    // We will start by using xrandr to identify the connected displays. At this
    // step we will collect width, height, offsets and scale.
    QString stdout = exec("xrandr --props --verbose");
    QStringList lines = stdout.split('\n');
    QList<ScalableDisplay*> displays;
    ScalableDisplay * display = nullptr;
    QRegularExpressionMatch match;

    QRegularExpression connectedRegex("((?:DP|HDMI)-\\d+)\\s+connected\\s+(?:primary\\s+)?(\\d+).(\\d+).(\\d+).(\\d+).*");
    QRegularExpression disconnectedRegex("(DP|HDMI)-\\d+\\s+disconnected\\s+.*");
    QRegularExpression scale1Regex("\\s+Transform:\\s+([0-9\\.\\+\\-]+).([0-9\\.\\+\\-]+).([0-9\\.\\+\\-]+)");
    QRegularExpression scale2Regex("\\s+([0-9\\.\\+\\-]+).([0-9\\.\\+\\-]+).([0-9\\.\\+\\-]+)");
    QRegularExpression edidStartRegex("\\s+EDID:\\s+");
    QRegularExpression edidDataRegex("\\s+([0-9abcdef]{32})");

    QRegularExpression displaySerialNumberRegex("^\\s+Display Product Serial Number:\\s+'([^']*)'.*");
    QRegularExpression displayProductNameRegex("^\\s+Display Product Name:\\s+'([^']*)'.*");
    QRegularExpression serialNumberRegex("^\\s+Serial Number:\\s+([^\\s]*).*");

    for (int i=0;i!=lines.size();++i) {
        QString & line = lines[i];

        // Look for connected lines
        match = connectedRegex.match(line);
        if (match.hasMatch()) {
            display = new ScalableDisplay(
                    match.captured(1),
                    QRect(
                        match.captured(4).toInt(),
                        match.captured(5).toInt(),
                        match.captured(2).toInt(),
                        match.captured(3).toInt()
                    )
            );

            displays.append(display);

            continue;
        }

        // Look for disconnected lines
        match = disconnectedRegex.match(line);
        if (match.hasMatch()) {
            display = nullptr;
            continue;
        }

        if (display == nullptr)
            continue;

        // Look for scale lines
        match = scale1Regex.match(line);
        if (match.hasMatch()) {
            display->scaleX = match.captured(1).toDouble();
            ++i;

            if (i!=lines.size()) {
                QString & line2 = lines[i];
                match = scale2Regex.match(line2);
                if (match.hasMatch()) {
                    display->scaleY = match.captured(2).toDouble();
                }
            }
            continue;
        }

        // Look for edid
        match = edidStartRegex.match(line);
        if (match.hasMatch()) {
            ++i;

            while (i!=lines.size()) {
                QString & line2 = lines[i];
                match = edidDataRegex.match(line2);

                if (match.hasMatch()) {
                    display->edidData.append(match.captured(1));
                    ++i;
                } else {
                    break;
                }
            }

            continue;
        }
    }

    // Now we will use edid-decode to decode the editData and read the serial numbers and product name
    for (ScalableDisplay * display : displays) {
        QString cmd = "echo \"" + display->edidData.join("") + "\" | edid-decode";
        QStringList lines = exec(cmd).split('\n');

        for (QString & line : lines) {
            match = serialNumberRegex.match(line);
            if (match.hasMatch()) {
                display->serialNumber = match.captured(1);
                continue;
            }

            match = displaySerialNumberRegex.match(line);
            if (match.hasMatch()) {
                display->displaySerialNumber = match.captured(1);
                continue;
            }

            match = displayProductNameRegex.match(line);
            if (match.hasMatch()) {
                display->displayProductName = match.captured(1);
                continue;
            }
        }
    }

    // Now we obtain the externalRect from the QScreens provided by QGuiApplication
    QList<QScreen*> screens = QGuiApplication::screens();

    for (int i=0;i!=screens.size();++i) {
        auto screen = screens[i];

        for (ScalableDisplay * display : displays) {
            if (display->displaySerialNumber == "") {
                if (screen->serialNumber().startsWith(display->serialNumber))
                    display->externalGeometry = screen->geometry();
            } else {
                if (screen->serialNumber().startsWith(display->displaySerialNumber))
                    display->externalGeometry = screen->geometry();
            }
        }
    }

    // This is just an utility to check was was recognized
    print("Found", displays.size(), "displays:");
    for (ScalableDisplay * tmp : displays) {
        print("  Port:", tmp->port);
        print("  InternalGeometry:", tmp->internalGeometry.left(), tmp->internalGeometry.top(), tmp->internalGeometry.width(), tmp->internalGeometry.height());
        print("  ExternalGeometry:", tmp->externalGeometry.left(), tmp->externalGeometry.top(), tmp->externalGeometry.width(), tmp->externalGeometry.height());
        print("  Scale:", tmp->scaleX, tmp->scaleY);
        print("  Serial Number:", tmp->serialNumber);
        print("  Display Serial Number:", tmp->displaySerialNumber);
        print("  Display Product Name:", tmp->displayProductName);
        print();
    }

    return displays;
}

void
readCommands(Core * c)
{
    std::string cmd;
    bool restart = false;

    while (true) {

        std::ifstream ifs(named_pipe);

        while (!restart)
        {
            if (!(ifs >> cmd)) {
                print("Error during cmd read");
                restart = true;
                sleep(1);
                continue;
            }

            print("Got cmd: ", cmd);

            if (cmd == "draw") {
                int x1, y1, x2, y2;
                if (ifs >> x1 >> y1 >> x2 >> y2)
                    c->draw(x1,y1,x2,y2);
            }

            else if (cmd == "erase") {
                int x1, y1, x2, y2;
                if (ifs >> x1 >> y1 >> x2 >> y2)
                     c->erase(x1,y1,x2,y2);
            }

            else if (cmd == "move_page") {
                int rx, ry;
                if (ifs >> rx >> ry)
                    c->movePage(rx,ry);
            }

            else if (cmd == "change_brush_size") {
                int size;
                if (ifs >> size)
                    c->changeBrushSize(size);
            }

            else if (cmd == "change_eraser_size") {
                int size;
                if (ifs >> size)
                    c->changeEraserSize(size);
            }

            else if (cmd == "set_page_mode") {
                int pageMode;
                if (ifs >> pageMode)
                    c->setPageMode(pageMode);
            }

            else if (cmd == "show_previous_page") {
                c->showPreviousPage();
            }

            else if (cmd == "show_next_page") {
                c->showNextPage();
            }

            else if (cmd == "") {
                sleep(1);
            }

            else {
                std::cout << "Unknown command:" << cmd << std::endl;
            }
        }

        restart = false;
    }
}

Core::Core(QObject *parent)
    : QObject{parent},
      pageMode(PageMode::MODE_TRANSPARENT),
      transparentBook(this, false),
      opaqueBook(this, true),
      activeBook(&transparentBook),
      reader(readCommands, this),
      size_brush_index(5),
      size_eraser_index(5),
      size_brush(pow(BRUSH_BASE, size_brush_index)),
      size_eraser(pow(ERASER_BASE, size_eraser_index)),
      brush_color(QColor("#0000ff")),
      width_space(0),
      height_space(0)
{
    QList<ScalableDisplay*> displays = parseDisplays();

    QList<QScreen*> screens = QGuiApplication::screens();

    for (int i=0;i!=screens.size();++i) {
        auto screen = screens[i];
        auto g = screen->geometry();

        Viewport * viewport = new Viewport(screen);
        viewport->setBook(activeBook);
        viewports.append(viewport);

        width_space  = std::max(g.right(), width_space);
        height_space = std::max(g.bottom(), height_space);

        //////////////

        QSize  size   = screen->virtualSize();
        QSize  size2  = screen->availableVirtualSize();
        QSizeF size3  = screen->physicalSize();
        QRect  g2     = screen->availableVirtualGeometry();
        qreal  dots   = screen->logicalDotsPerInch();
        QSize  size4  = screen->availableSize();
        auto   serial = screen->serialNumber();

        print("Screen", i);
        print("  Geometry:", g.left(), g.top(), g.width(), g.height());
        print("  VirtualGeometry: ", g2.left(), g2.top(), g2.width(), g2.height());
        print("  VirtualSize: ", size.width(), size.height());
        print("  AvailableVirtualSize: ", size2.width(), size2.height());
        print("  PhysicalSize: ", size3.width(), size3.height());
        print("  AvailableSize: ", size4.width(), size4.height());
        print("  DotsPerInch: ", dots);
        print("  SerialNumber: ", serial);

        print();
    }

    wup::print("space", width_space, height_space);
    wup::print("sizes", size_brush, size_eraser);
}

void Core::onPageChanged(Book *book, Page *)
{
    for (Viewport * viewport : viewports)
        viewport->setBook(book);
}

void Core::onRepaintPage(Book *, Page *, QRect *rect)
{
    for (Viewport * viewport : viewports)
        viewport->update(rect);
}

void Core::changeBrushSize(int size)
{
    size_brush_index += size;
    size_brush_index = std::min(size_brush_index, MAX_BRUSH_INDEX);
    size_brush_index = std::max(size_brush_index, MIN_BRUSH_INDEX);
    size_brush       = int(pow(BRUSH_BASE, size_brush_index));
}

void Core::changeEraserSize(int size)
{
    size_eraser_index += size;
    size_eraser_index = std::min(size_eraser_index, MAX_BRUSH_INDEX);
    size_eraser_index = std::max(size_eraser_index, MIN_BRUSH_INDEX);
    size_eraser       = int(pow(ERASER_BASE, size_eraser_index));
}

void Core::showPreviousPage()
{
    activeBook->showPreviousPage();
}

void Core::showNextPage()
{
    activeBook->showNextPage();
}

void Core::setPageMode(int iPageMode)
{
    PageMode pageMode = PageMode(iPageMode);

    if (this->pageMode == pageMode)
        return;

    this->pageMode = pageMode;

    switch (pageMode) {
    case MODE_TRANSPARENT:
        print("transparent");
        activeBook = &transparentBook;
        activeBook->setVisible(true);
        break;
    case MODE_OPAQUE:
        print("opaque");
        activeBook = &opaqueBook;
        activeBook->setVisible(true);
        break;
    case MODE_PASSTHROUGH:
        print("passthrough");
        activeBook = &transparentBook;
        activeBook->setVisible(true);
        break;
    case MODE_DISABLED:
        print("disabled");
        activeBook = &transparentBook;
        activeBook->setVisible(false);
        break;
    }

}

void Core::movePage(int rx, int ry) {
    activeBook->movePage(rx, ry);
}

void Core::draw(int x1, int y1, int x2, int y2) {
    // Convert from tablet abs coordinates to multidisplay coordinates
    x1 = (x1 * width_space) / 32767;
    x2 = (x2 * width_space) / 32767;

    y1 = (y1 * height_space) / 32767;
    y2 = (y2 * height_space) / 32767;

    print("Core::draw", x1, y1, x2, y2);

    for (Viewport * viewport : viewports)
        viewport->draw(x1, y1, x2, y2, size_brush, brush_color);
}

void Core::erase(int x1, int y1, int x2, int y2) {
    // Convert from tablet abs coordinates to multidisplay coordinates
    x1 = (x1 * width_space) / 32767;
    x2 = (x2 * width_space) / 32767;

    y1 = (y1 * height_space) / 32767;
    y2 = (y2 * height_space) / 32767;

    for (Viewport * viewport : viewports)
        viewport->erase(x1, y1, x2, y2, size_brush);
}

