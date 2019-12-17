# Stdlib imports
import json
from random import randint
from datetime import date, timedelta
import datetime

# Django core imports
from django.conf import settings

from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
import django.http

from django.core.mail import send_mail  # mailer

# Model imports
from users.models import CustomUser
from .models import Lesson, Teacher, Slot3

# Local module imports
from .forms import LessonForm
from .slots import slots4dayofweek, index2time, time2index
from .gmail import send
from .gsheets import test as gstest, GSheetSlotRequest
from prices import *

# new
import bookingapp.business_settings as bs

KIEV_TIMEOFFSET = 2 #kyiv timeoffset


def slotmaker(request):
    """ /slotmaker produce lesson slots according to data in google spreadsheets"""
    if not request.user.is_superuser:
        return redirect('home')
    
    if request.method == "GET":
        today = (datetime.datetime.now().date()).isoformat()[:10]
        return render(request, 'slotmaker.html', {'today':today})

    if request.method == "POST":
        data = request.POST
        start = fixDateForSafari(data['start'])
        finish = fixDateForSafari(data['finish'])
        
        greq = GSheetSlotRequest()
        teachers: list = greq.get_teacher_names()

        format_str = '%Y-%m-%d'  # The date format
        s = datetime.datetime.strptime(start, format_str)
        f = datetime.datetime.strptime(finish, format_str)
        delta = f - s
        
        # Loop thru each teacher to fill their schedule
        for t in teachers:
            
            # Select teacher if present in our records, or fall back to creating a record
            teacher_name = t.strip().lower()
            try:
                teacher = Teacher.objects.get(slug=teacher_name)
            except Teacher.DoesNotExist:
                teacher = Teacher.objects.create(slug=teacher_name, color=hex(abs(hash(teacher_name)))[2:8])

            weekload = greq.get_corrected_slots_for_teacher_m(t, '!A2:H49') # formerly: '!A18:H41'
            
            for i in range(delta.days + 1):
                cur = s + timedelta(i)

                # Delete all previous unbooked slots
                Slot3.objects.filter(kydate=cur.date(), teacher=teacher, student_id__isnull=True).delete()

                # Get slots for current weekday
                slots = weekload[cur.weekday()]

                index = 0
                # formery, index = 8, because we started at 8:00, 
                # but now we traverse all the way 00:00-23:30
                for el in slots:
                    if el == 1:
                        curdt = cur + timedelta(hours=index)
                        #maybe we need also check teacher
                        booked = Slot3.objects.filter(teacher = teacher)\
                                              .filter(kydatetime=curdt.strftime("%Y-%m-%d %H:%M:%S"))\
                                              .exists()
                        if not booked:
                            Slot3.objects.create(kydate=cur.date(), 
                                                 kydatetime=curdt.strftime("%Y-%m-%d %H:%M:%S"),
                                                 kytime=index, 
                                                 teacher=teacher)
                    index += 0.5

        return redirect('home')


def timeoffset(request):
    """ saves information about user offset in profile """
    request.user.timeoffset = request.POST['timeoffset']
    request.user.city = request.POST['city']  # request.META.get('TZ')
    request.user.save()
    return redirect('home')


def slots(request):
    """ /slots displays list of available slots for proper day, by default - current day"""
    today = datetime.datetime.now().isoformat()[:10]
    return render(request, 'slots.html', {'today': today, 'slots': Slot3.objects.freeSlotsForMonth()})


@login_required
def alllessons(request):
    """ /alllessons - displays list of booked lesson for proper day"""
    strdate = request.GET.get('date')
    format_str = '%Y-%m-%d'
    lessons = []
    if strdate:
        strdate = fixDateForSafari(strdate)
        date = datetime.datetime.strptime(strdate, format_str).date()
        lessons = Slot3.objects.allLessonsForaDay(date)
    return render(request, 'alllessons.html', {'date': strdate, 'lessons': lessons})


def intToUTC(val):
    if val > -1:
        return '+' + str(val)
    return str(val)


@method_decorator(csrf_exempt, name='dispatch')
@login_required
def booked(request):
    """ endpoint for booking lessons"""
    bookingStart = (datetime.datetime.now() + datetime.timedelta(days=2)).isoformat()[:10]
    today = (datetime.datetime.now().date()).isoformat()[:10]
    user = request.user
    lessons = Slot3.objects.bookedForUser(user.id)
    total = len(lessons)

    if request.method == "POST":
        form = LessonForm(request.POST)
        if form.is_valid():
            user = request.user
            print('from ' + request.user.username)
            lesson = form.save(commit=False)
            stud_id = request.user.id
            print('requested date ' + str(lesson.date) + ' time ' + str(lesson.hour))
            bookingStartDateTime = datetime.datetime.now() + datetime.timedelta(days=2)

            tid = None
            if Teacher.objects.filter(slug=user.lastteacher).exists():
                tid = Teacher.objects.get(slug=user.lastteacher).id
            slot2 = None
            if tid and Slot3.objects.isSlotAvailable(lesson.date, lesson.hour, tid):
                slot1 = Slot3.objects.get(kydate=lesson.date, kytime=lesson.hour, teacher_id=tid)
                slot2 = Slot3.objects.get(kydate=lesson.date, kytime=lesson.hour + 0.5, teacher_id=tid)
            else:
                anyteacherSlots = Slot3.objects.filter(kydate=lesson.date, kytime=lesson.hour,
                                                       student_id__isnull=True).order_by('?')
                for slot1 in anyteacherSlots:
                    if not Slot3.objects.isSlotAvailable(slot1.kydate, slot1.kytime, slot1.teacher_id):
                        continue
                    slot2 = Slot3.objects.get(kydate=lesson.date, kytime=lesson.hour + 0.5, teacher_id=slot1.teacher_id)
                    user.lastteacher = Teacher.objects.get(id=slot1.teacher_id).slug

            if slot2:
                print('there is a slot ' + str(slot1.id) + ' ' + str(slot2.id))
                slot1.student_id = user.id
                slot2.student_id = user.id
                user.hours -= 1
                slot1.save()
                slot2.save()
                user.save()

                # Send confirmations emails
                # to the front desk admin:

                rendered = render_to_string('email/booked-admin.html',
                                            {'username': user.username,
                                             'datetime': slot1.kydatetime.isoformat().replace('T', " "),
                                             'teacher': user.lastteacher})
                
                # send(settings.DEFAULT_TO_EMAIL, rendered, '[BookingApp] for admin: lesson booked')
                send_mail(
                    subject=f'[BookingApp] {user.username} booked a lesson',
                    message=f'{user.username} has booked a lesson with {user.lastteacher} at {slot1.kydatetime.isoformat().replace("T", " ")}',
                    from_email='super Bot',
                    recipient_list=bs.notify_emails['frontdesk'],
                    html_message=rendered
                )


                localdatetime = slot1.kydatetime + timedelta(hours=user.timeoffset - KIEV_TIMEOFFSET)
                rendered = render_to_string('email/booked.html',
                                            {'datetime': localdatetime.isoformat().replace('T', " "),
                                             'timeoffset': intToUTC(user.timeoffset), 'teacher': user.lastteacher})
                
                # send(user.email, rendered, '[BookingApp] lesson booked')
                send_mail(
                    subject='You have booked a lesson at super School',
                    message=f'Lesson booked!\nTime:{localdatetime.isoformat().replace("T", " ")}\nTeacher:{user.lastteacher}',
                    from_email='super Bot',
                    recipient_list=[user.email],
                    html_message=rendered
                )

            else:
                bookingError = 'Sorry, but this time is busy'

        return redirect('home')

    else:  # not post
        form = LessonForm()
    callback = 'http://booking.superschool.com.ua/callback/'

    return render(request, 'booked.html',
                  {'today': today, 'bookingStart': bookingStart, 'usertimezone': user.timeoffset, 'usercity': user.city,
                   'slots': Slot3.objects.freeSlotsForMonth(), 'lessons': lessons, 'form': form, 'total': total,
                   'city': request.META.get('TZ'),
                   'price1': PRICE1, 'price5': PRICE5, 'price10': PRICE10,
                   })


# return HttpResponse("Hello, world. You're at the booking index.")


@login_required
def unbook(request):
    """ endpoint which allows to unbook"""
    user = request.user
    id = request.POST.get('id')
    slot1 = Slot3.objects.get(id=id)
    slot1.student_id = None
    slot1.save()
    slot2 = Slot3.objects.get(kydate=slot1.kydate, kytime=slot1.kytime + 0.5, teacher_id=slot1.teacher_id)
    slot2.student_id = None
    slot2.save()
    user.hours += 1
    user.save()
    
    # Send unbook confirmation emails
    
    # To school's front desk
    teacher = Teacher.objects.get(id=slot1.teacher_id).slug
    dt = slot1.kydatetime
    rendered = render_to_string('email/unbooked.html',
                                {'username': user.username, 'datetime': dt.isoformat().replace("T", " "),
                                 'timeoffset': intToUTC(KIEV_TIMEOFFSET), 'teacher': teacher})
    
    # send(settings.DEFAULT_TO_EMAIL, rendered, '[BookingApp] for admin: lesson unbooked')
    send_mail(
        subject=f'[BookingApp]: {user.username} has unbooked a lesson',
        message=f'{user.username} unbooked a lesson with {teacher} at {dt.isoformat().replace("T", " ")}',
        from_email='super Bot',
        recipient_list=bs.notify_emails['frontdesk'],
        html_message=rendered
    )

    # To user
    localdatetime = dt + timedelta(hours=user.timeoffset - 2)
    rendered = render_to_string('email/unbooked.html',
                                {'username': user.username, 'datetime': localdatetime.isoformat().replace("T", " "),
                                 'timeoffset': intToUTC(user.timeoffset),
                                 'teacher': teacher})
    
    # send(user.email, rendered, '[BookingApp] lesson unbooked')
    send_mail(
        subject='You have unbooked a lesson with super School',
        message=f'Lesson with {teacher} at {localdatetime.isoformat().replace("T", " ")} unbooked successfully.',
        from_email='super Bot',
        recipient_list=[user.email],
        html_message=rendered
    )

    return redirect('home')


@method_decorator(csrf_exempt, name='dispatch')
def callback(request):
    """ endpoint for processing callbacks from fondy payment system """
    if request.method != "POST":
        print('its GET')
        return render(request, 'error.html', {})
    print(request.POST)
    if request.POST.get('response_status') == 'success':
        user = CustomUser.objects.get(email=request.POST.get('sender_email'))
        income = int(request.POST.get('actual_amount')) / 100
        if income == PRICE1:
            user.hours += 1
        elif income == PRICE5:
            user.hours += 5
        elif income == PRICE10:
            user.hours += 10
        user.save()

        # Send notification email to school about payment
        rendered = render_to_string('email/income.html', {'money': income, 'username': user.username})
        
        # send(settings.DEFAULT_TO_EMAIL, rendered, '[BookingApp] money from user')
        send_mail(
            subject=f'[BookingApp] {income} UAH received from {user.username}',
            message=f'User {user.username} has paid {income} UAH to the school.\nTheir balance is now {user.hours}',
            from_email='super Bot',
            recipient_list=bs.notify_emails['business'],
            html_message=rendered
        )


    return redirect('home')

def fixDateForSafari(s):
    """ reformat data string if taken from Safari"""
    if s[2] == '/':
        return s[6:] + '-' + s[:2] + '-' + s[3:5]
    return s

