from celery import shared_task
from .models import Score, User
from .utils import format_report
from .mail import send_email
import datetime
import csv



# task 1 download csv report for user
# user(client) triggered asyn job

@shared_task(ignore_result=False, name='download_csv_report')
def download_csv_report():
    scores = Score.query.all()  # Fetch all scores from the database
    csv_file_name = f"scores_{datetime.datetime.now().strftime('%f')}.csv"
    with open(f"static/{csv_file_name}", 'w', newline = "") as csvfile:
        sr_no = 1
        score_csv = csv.writer(csvfile, delimiter=',')
        score_csv.writerow(['Sr No', 'Quiz ID', 'User ID', 'Time Stamp of Attempt', 'Total Scored', 'Total Possible', 'Completion Time'])
        for score in scores:
            score_csv.writerow([sr_no, score.quiz_id, score.user_id, score.time_stamp_of_attempt, score.total_scored, score.total_possible, score.completion_time])
            sr_no += 1

    return csv_file_name


# task 2 monthly report send via mail
# scheduled job  via crontab

@shared_task(ignore_result=False, name='download_monthly_report')
def Monthly_report():
    users = User.query.all()
    for user in users[1:]:
        user_data = {}
        user_data['id'] = user.id
        user_data['name'] = user.student_profile.name if user.student_profile else user.email
        user_data['email'] = user.email
        user_report = []
        for score in user.quiz_attempts:
            user_report.append({
                'quiz_id': score.quiz_id,
                'total_scored': score.total_scored,
                'total_possible': score.total_possible,
                'completion_time': score.completion_time
            })
        user_data['report'] = user_report
        message = format_report('static/mail_details.html', user_data)
        send_email(user.email, subject='Monthly Report - QuizzApp', message = message)

    return "Monthly report send"


# task3 update sent via g-chat webhook
# backend (endpoint) triggered async job

@shared_task(ignore_result=False, name='quiz_remainder')
def quiz_remainder(email):
    text = f"Hello user {email}, this is a reminder for your quiz. Please check your dashboard for more details."
    response = requests.post(
        'https://chat.googleapis.com/v1/spaces/AAQAHE4byLM/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=BxMq64CBm9fiZQpF-2Jr15rvPJlWyzj3MEeQUogmhkQ',
        headers={
            'Content-Type': 'application/json'
            },
        json={
            'text': text
        })
    return "Remainder sent successfully"