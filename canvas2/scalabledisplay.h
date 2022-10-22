#ifndef SCALABLEDISPLAY_H
#define SCALABLEDISPLAY_H

#include <QRect>
#include <QScreen>
#include <QString>



class ScalableDisplay {
public:

    ScalableDisplay(QString port, QRect internalRect);

    QString port;
    QRect internalGeometry;
    QRect externalGeometry;
    double scaleX;
    double scaleY;
    QString serialNumber;
    QString displaySerialNumber;
    QString displayProductName;
    QList<QString> edidData;
    QScreen *screen;
    double normX;
    double normY;

public:
    static QList<ScalableDisplay*> parseDisplays();

};

#endif // SCALABLEDISPLAY_H
