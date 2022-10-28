#include <QApplication>
#include <QDateTime>
#include <core.h>

FILE * logFile = nullptr;

void logHandler(QtMsgType type, const QMessageLogContext &context, const QString &msg)
{
    if (logFile == nullptr)
        return;

    QByteArray dateTime = QDateTime::currentDateTime().toString(Qt::ISODateWithMs).toLocal8Bit();
    QByteArray localMsg = msg.toLocal8Bit();

    switch (type) {
    case QtDebugMsg:
        fprintf(logFile, "%s Debug: %s\n", dateTime.constData(), localMsg.constData());
        break;
    case QtInfoMsg:
        fprintf(logFile, "%s Info: %s\n", dateTime.constData(), localMsg.constData());
        break;
    case QtWarningMsg:
        fprintf(logFile, "%s Warning: %s\n", dateTime.constData(), localMsg.constData());
        break;
    case QtCriticalMsg:
        fprintf(logFile, "%s Critical: %s\n", dateTime.constData(), localMsg.constData());
        break;
    case QtFatalMsg:
        fprintf(logFile, "%s Fatal: %s\n", dateTime.constData(), localMsg.constData());
        abort();
    }

    fflush(logFile);
}

int main(int argc, char *argv[])
{
    putenv((char *)"QT_AUTO_SCREEN_SCALE_FACTOR=0");
    putenv((char *)"QT_ENABLE_HIGHDPI_SCALING=0");

    logFile = fopen("./main.log.qt", "w");
    qInstallMessageHandler(logHandler); // Install the handler

    QApplication a(argc, argv);
    Core core(&a);

    return a.exec();
}
