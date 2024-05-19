#include "notificationpool.h"

#include <QFontMetrics>
#include <QTimer>
#include <QTime>
#include <QPainter>

NotificationPool::NotificationPool() :
    notificationFont("Ubuntu", 12, 400, false)
{
    notificationPen.setColor(qRgba(255,255,255,64));

    notificationStrongBrush.setColor(qRgba(128,0,0,255));
    notificationStrongBrush.setStyle(Qt::SolidPattern);

    notificationWeakBrush.setColor(qRgba(0,0,128,255));
    notificationWeakBrush.setStyle(Qt::SolidPattern);
}

void NotificationPool::setStrongNotification(QString title, QString extra, bool visible)
{
    for (qsizetype i=0;i!=strongNotifications.size();++i)
    {
        auto & n = strongNotifications[i];

        if (n.title() != title)
            continue;

        if (visible)
            n.setExtra(extra);
        else
            strongNotifications.erase(strongNotifications.constBegin() + i);

        return;
    }

    if (visible)
        strongNotifications.push_back(Notification (title, extra));
}

void NotificationPool::setWeakNotification(QString title, QString extra)
{

    for (qsizetype i=0;i!=weakNotifications.size();++i)
    {
        auto & n = weakNotifications[i];

        if (n.title() != title)
            continue;

        weakNotifications.erase(weakNotifications.constBegin() + i);
        break;
    }

    long currentTime = time(NULL);
    qDebug() << "Creating weak notification at" << currentTime;
    long expireTime = currentTime + 1;

    weakNotifications.push_back(Notification(title, extra, expireTime));
    qDebug() << "  Created weak notification:" << title << ", " << extra << ", " << expireTime;
}

long NotificationPool::dropExpiredNotifications()
{
    long currentTime = time(NULL);
    long nextExpireTime = -1;
    qsizetype j = 0;

    qDebug() << "Dropping expired notifications, currentTime = " << currentTime;

    for (qsizetype i=0;i!=weakNotifications.size();++i)
    {
        auto & n = weakNotifications[i];

        if (n.expireTime() > currentTime)
        {
            qDebug() << "  Notification still alive:" << n.title() << ", " << n.extra() << ", " << n.expireTime();
            if (j != i)
                weakNotifications[j] = weakNotifications[i];
            ++j;

            if (nextExpireTime == -1 || n.expireTime() < nextExpireTime)
                nextExpireTime = n.expireTime();
        }
        else
        {
            qDebug() << "  Found an expired notification:" << n.title() << ", " << n.extra() << ", " << n.expireTime();
        }
    }

    weakNotifications.resize(j);
    qDebug() << "  Weak notifications has size = " << weakNotifications.size();

    return nextExpireTime == -1 ? -1 : nextExpireTime - currentTime;
}

void NotificationPool::onPaint(QPainter & painter, const QRect & geometry)
{
    int y = 100;

    for (auto it=strongNotifications.begin();it!=strongNotifications.end();++it)
        y += paintNotification(painter, *it, notificationFont, notificationStrongBrush, notificationPen, y, geometry);

    for (auto it=weakNotifications.rbegin();it!=weakNotifications.rend();++it)
        y += paintNotification(painter, *it, notificationFont, notificationWeakBrush, notificationPen, y, geometry);
}

int NotificationPool::paintNotification(
        QPainter & painter,
        Notification const & n,
        QFont const & font,
        QBrush const & brush,
        QPen const & pen,
        int const y,
        QRect const & geometry)
{
    QFontMetrics fm(font);
    QRect messageSize = fm.boundingRect(n.label());

    QRect rect(geometry.width() - margin.left() - margin.right() - messageSize.width() - padding.right(),
               y + padding.top(),
               messageSize.width() + margin.left() + margin.right(),
               messageSize.height() + margin.top() + margin.bottom());

    painter.setPen(Qt::NoPen);
    painter.setBrush(brush);
    painter.drawRoundedRect(rect, round, round);

    QPoint point(geometry.width() - messageSize.width() - padding.right() - margin.right(),
                 y + padding.top() + margin.top() + messageSize.height() - fm.underlinePos());

    painter.setPen(pen);
    painter.setBrush(Qt::NoBrush);
    painter.setFont(font);
    painter.drawText(point, n.label());

    return padding.top() + margin.top() + messageSize.height() + margin.bottom() + padding.bottom();
}

