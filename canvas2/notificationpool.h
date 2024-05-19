#ifndef NOTIFICATIONPOOL_H
#define NOTIFICATIONPOOL_H

#include <QBrush>
#include <QFont>
#include <QPainter>
#include <QPen>
#include <QTime>

class Notification
{
private:
    QString _title;
    QString _extra;
    long _expireTime;
    QString _label;

public:
    Notification()
    {

    }

    Notification(QString & title, QString & extra) :
        _title(title),
        _extra(extra)
    {
        updateLabel();
    }

    Notification(QString & title, QString & extra, long expireTime) :
        _title(title),
        _extra(extra),
        _expireTime(expireTime)
    {
        updateLabel();
    }

    void setTitle(QString & value) { _title = value; updateLabel(); }
    void setExtra(QString & value) { _extra = value; updateLabel(); }
    void setExpireTime(long value) { _expireTime = value; }

    QString const & title() const { return _title; }
    QString const & extra() const { return _extra; }
    QString const & label() const { return _label; }
    long expireTime() const { return _expireTime; }

private:
    void updateLabel() { _label = QString("%1 (%2)").arg(_title).arg(_extra); }
};

struct Region
{
    int _left, _top, _right, _bottom;
    int left() const { return _left; }
    int top() const { return _top; }
    int right() const { return _right; }
    int bottom() const { return _bottom; }
};

class NotificationPool
{
public:

    NotificationPool();
    void onPaint(QPainter & painter, QRect const & geometry);
    void setNotification(QString notification);
    void setStrongNotification(QString title, QString extra, bool visible);
    void setWeakNotification(QString title, QString extra);
    long dropExpiredNotifications();

private:
    int paintNotification(QPainter &painter, const Notification &n, const QFont &font, const QBrush &brush, const QPen &pen, const int y, const QRect &geometry);

private:

    QPen notificationPen;
    QBrush notificationStrongBrush;
    QBrush notificationWeakBrush;
//    QString notification;
    QFont notificationFont;

    QList<Notification> strongNotifications;
    QList<Notification> weakNotifications;

    Region const padding {40,15,50,15};
    Region const margin {20,10,20,10};
    qreal const round {10.0};

};

#endif // NOTIFICATIONPOOL_H
