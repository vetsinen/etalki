from django.db import models
from users.models import CustomUser
from django.utils import timezone
import datetime
from django.forms.models import model_to_dict
import json

#used by Lesson form
class Lesson(models.Model):
    date = models.DateField(default='2018-12-06')
    hour = models.FloatField(default=10.0)

    class Meta:
        ordering = ["date", "hour"]

    # @property
    # def full_name(self):
    #     return '%s-%s:00 by %s' % (self.date, self.hour, self.teacher)


class Teacher(models.Model):
    slug = models.CharField(max_length=20)
    color = models.CharField(max_length=6, null=True)

    def __str__(self):
        return self.slug


class SlotManager(models.Manager):
    def freeSlotsForMonth(self):
        rez = {}
        bookingStartDateTime = datetime.datetime.now() + datetime.timedelta(days=2)  # .isoformat()[:10]
        rows0 = self.filter(kydatetime__gt=bookingStartDateTime, student_id__isnull=True).all().order_by('kydatetime')
        rows1 = []
        for el in rows0:
            if self.filter(kydate=el.kydatetime, kytime=el.kytime+0.5, teacher_id=el.teacher_id, student_id__isnull=True).exists():
                rows1.append(el)
        for row in rows1:
            date = row.kydate.isoformat()[:10]
            if date in rez:
                rez[date].add(row.kytime)
            else:
                rez[date] = {row.kytime}
        nrez = {}

        for el in rez.keys():
            nrez[el] = sorted( list(rez[el]))

        return json.dumps(nrez)

    def bookedForUser(self, id):
        rez = []
        kytomezone = 2
        usertimezone = CustomUser.objects.get(id=id).timeoffset
        debookingStartDateTime = datetime.datetime.now() + datetime.timedelta(days=1)
        rows = self.filter(kydatetime__gt=datetime.datetime.now(), student_id=id).all().order_by('teacher_id')
        for row in rows:
            userdate = row.kydatetime + datetime.timedelta(hours=(usertimezone - kytomezone))
            slot = {"datetime": userdate.isoformat().replace('T', " "),
                    "teacher": Teacher.objects.get(id=row.teacher_id).slug}
            if row.kydatetime > debookingStartDateTime:
                slot['id'] = row.id
            rez.append(slot)

        nrez=[]
        for i in range(0,len(rez),2):
            nrez.append(rez[i])
        return nrez

    def allLessonsForaDay(self, date):
        rez = []
        flag = True
        for row in self.filter(kydate=date, student_id__isnull=False).all().order_by('kydatetime','teacher_id'):
            if flag:
                rez.append({
                    "datetime": row.kydatetime.isoformat().replace('T', " "),
                    "student": CustomUser.objects.get(id=row.student_id).email,
                    "teacher": Teacher.objects.get(id=row.teacher_id).slug,
                    "color": Teacher.objects.get(id=row.teacher_id).color,
                })
            flag=not flag
        return rez

    def isSlotAvailable(self,kydate, kytime, tid):
        s1 = self.filter(kydate=kydate, kytime = kytime, teacher_id=tid,  student_id__isnull=True).exists()
        s2 = self.filter(kydate=kydate, kytime=kytime+0.5, teacher_id=tid,  student_id__isnull=True).exists()
        return  s1 and s2

class Slot3(models.Model):
    kydate = models.DateField(blank=False)
    kydatetime = models.DateTimeField(blank=True)
    kytime = models.FloatField(blank=False)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    student = models.ForeignKey(CustomUser, blank=True, null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.kydate.isoformat()

    objects = SlotManager()
