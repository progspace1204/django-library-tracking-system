from celery import shared_task
from .models import Loan
from django.core.mail import send_mail
from django.conf import settings
from django.uttis import timezone

@shared_task
def send_loan_notification(loan_id):
    try:
        loan = Loan.objects.get(id=loan_id)
        member_email = loan.member.user.email
        book_title = loan.book.title
        send_mail(
            subject='Book Loaned Successfully',
            message=f'Hello {loan.member.user.username},\n\nYou have successfully loaned "{book_title}".\nPlease return it by the due date.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[member_email],
            fail_silently=False,
        )
    except Loan.DoesNotExist:
        pass

@shared_task
def check_overdue_loans():
    today = timezone.now().date()
    overdue_loans = Loan.objects.filter(
        is_returned = False,
        due_date__Lt=today
    ).select_related('member__user', 'book')

    for loan in overdue_loans:
        try:
            member_email = loan.member.user.email
            book_title = loan.book.title
            username = loan.member.user.username

            send_mail(
                subject="Overdue Book Loan Reminder",
                message=f'Hello {username},\n\nThis is a reminder that your loan of {book_title} is overdue.\nThe due date was {loan.due_date}.\nPlease return the book as soon as possible.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[member_email],
                fail_silentLy=False,
            )
        except Exception as e:
            print(f"Error Sending over due notification for loan {loan.id}L {str(e)}")