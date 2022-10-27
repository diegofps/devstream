#include <QApplication>
#include <core.h>

FILE * logFile = nullptr;

void logHandler(QtMsgType type, const QMessageLogContext &context, const QString &msg)
{
    if (logFile == nullptr)
        return;

    QByteArray localMsg = msg.toLocal8Bit();

    switch (type) {
    case QtDebugMsg:
        fprintf(logFile, "\n\nDebug, %s:%u, %s\n%s", context.file, context.line, context.function, localMsg.constData());
        break;
    case QtInfoMsg:
        fprintf(logFile, "\n\nInfo, %s:%u, %s\n%s", context.file, context.line, context.function, localMsg.constData());
        break;
    case QtWarningMsg:
        fprintf(logFile, "\n\nWarning, %s:%u, %s\n%s", context.file, context.line, context.function, localMsg.constData());
        break;
    case QtCriticalMsg:
        fprintf(logFile, "\n\nCritical, %s:%u, %s\n%s", context.file, context.line, context.function, localMsg.constData());
        break;
    case QtFatalMsg:
        fprintf(logFile, "\n\nFatal, %s:%u, %s\n%s", context.file, context.line, context.function, localMsg.constData());
        abort();
    }

    fflush(logFile);
}

int main(int argc, char *argv[])
{
    logFile = fopen("./main.log.qt", "w");
    qInstallMessageHandler(logHandler); // Install the handler

    QApplication a(argc, argv);
    Core core(&a);

    return a.exec();
}
