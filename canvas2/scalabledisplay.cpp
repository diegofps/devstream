#include "scalabledisplay.h"

#include <QApplication>
#include <QRegularExpression>


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


ScalableDisplay::ScalableDisplay(QString port, QRect internalRect) :
    port(port),
    internalGeometry(internalRect),
    externalGeometry(0,0,0,0),
    scaleX(0),
    scaleY(0),
    serialNumber(""),
    displaySerialNumber(""),
    displayProductName(""),
    screen(nullptr)
{

}

void ScalableDisplay::setExternalGeometry(const QRect & rect) {
    qDebug("Updating externalGeometry for %s", qUtf8Printable(serialNumber));
    this->externalGeometry = rect;
}

QList<ScalableDisplay*> ScalableDisplay::parseDisplays() {

    // We will start by using xrandr to identify the connected displays. At this
    // step we will collect width, height, offsets and scale.

    QString cmd = "xrandr --props --verbose";
    QString stdout = exec(cmd);
    QStringList lines = stdout.split('\n');
    QList<ScalableDisplay*> displays;
    ScalableDisplay * display = nullptr;
    QRegularExpressionMatch match;

    qDebug("xrandr's stdout for %s:\n%s", qUtf8Printable(cmd), qUtf8Printable(stdout));

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
        QString stdout = exec(cmd);

        qDebug("edid-decode's stdout for %s:\n%s", qUtf8Printable(cmd), qUtf8Printable(stdout));

        QStringList lines = stdout.split('\n');

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

    if (screens.size() == 1 && displays.size() == 1) {
        auto screen = screens[0];
        auto *display = displays[0];
        display->externalGeometry = screen->geometry();
        display->screen = screen;
    }

    else {
        for (int i=0;i!=screens.size();++i) {
            auto screen = screens[i];
            qDebug("Looking for screen %s", qUtf8Printable(screen->serialNumber()));

            for (ScalableDisplay * display : displays) {
                if (display->displaySerialNumber == "") {
                    if (screen->serialNumber().startsWith(display->serialNumber)) {
                        display->externalGeometry = screen->geometry();
                        display->screen = screen;
                        break;
                    }
                } else {
                    if (screen->serialNumber().startsWith(display->displaySerialNumber)) {
                        display->externalGeometry = screen->geometry();
                        display->screen = screen;
                        break;
                    }
                }
            }
        }
    }

    // Now we calculate normX and normY

    double normX=0;
    double normY=0;

    for (ScalableDisplay * display : displays) {
        if (display->scaleX > normX)
            normX = display->scaleX;
        if (display->scaleY > normY)
            normY = display->scaleY;
    }

    for (ScalableDisplay * display : displays) {
        display->normX = 1.0 / normX;
        display->normY = 1.0 / normY;
    }

    qDebug("Found %lld displays:", displays.size());

    for (ScalableDisplay * tmp : displays) {
        qDebug("  Port: %s", qUtf8Printable(tmp->port));
        qDebug("  InternalGeometry: %d %d %d %d", tmp->internalGeometry.left(), tmp->internalGeometry.top(), tmp->internalGeometry.width(), tmp->internalGeometry.height());
        qDebug("  ExternalGeometry: %d %d %d %d", tmp->externalGeometry.left(), tmp->externalGeometry.top(), tmp->externalGeometry.width(), tmp->externalGeometry.height());
        qDebug("  Scale: %F %F", tmp->scaleX, tmp->scaleY);
        qDebug("  Serial Number: %s", qUtf8Printable(tmp->serialNumber));
        qDebug("  Display Serial Number: %s", qUtf8Printable(tmp->displaySerialNumber));
        qDebug("  Display Product Name: %s", qUtf8Printable(tmp->displayProductName));
        qDebug();
    }

    return displays;
}
