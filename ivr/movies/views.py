from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from twilio.twiml.voice_response import VoiceResponse
from .models import Theater, Movie, Show
from django.urls import reverse
import datetime
from django.utils import timezone
from django.conf import settings
from django.http import HttpRequest
from django.core.exceptions import SuspiciousOperation
from twilio.request_validator import RequestValidator
request_validator = RequestValidator(settings.TWILIO_AUTH_TOKEN)

def validate_django_request(request: HttpRequest):
   try:
       signature = request.META['HTTP_X_TWILIO_SIGNATURE']
   except KeyError:
       is_valid_twilio_request = False
   else:
       is_valid_twilio_request = request_validator.validate(
           signature = signature,
           uri = request.get_raw_uri(),
           params = request.POST,
       )
   if not is_valid_twilio_request:
       # Invalid request from Twilio
       raise SuspiciousOperation()
   
@csrf_exempt
def answer(request: HttpRequest) -> HttpResponse:
    validate_django_request(request)
    vr = VoiceResponse()
    vr.say('welcome to movie info!')
    
    with vr.gather(
       action=reverse('choose-movie'),
       finish_on_key='#',
       timeout=20,
   ) as gather:
       gather.say('Please choose a theater and press #')
       theaters = (
           Theater.objects
           .filter(digits__isnull=False)
           .order_by('digits')
       )
       for theater in theaters:
           gather.say(f'For {theater.name} in {theater.address} press {theater.digits}')

    vr.say('We did not receive your selection')
    vr.redirect('')

    return HttpResponse(str(vr), content_type='text/xml')

# movies/views.py

@csrf_exempt
def choose_movie(request: HttpRequest) -> HttpResponse:
   validate_django_request(request)
   vr = VoiceResponse()

   digits = request.POST.get('Digits')
   try:
       theater = Theater.objects.get(digits=digits)

   except Theater.DoesNotExist:
       vr.say('Please select a theater from the list.')
       vr.redirect(reverse('choose-theater'))

   else:
       with vr.gather(
           action=f'{reverse("list-showtimes")}?theater={theater.id}',
           finish_on_key='#',
           timeout=20,
       ) as gather:
           gather.say('Please choose a movie and press #')
           movies = (
               Movie.objects
               .filter(digits__isnull=False)
               .order_by('digits')
           )
           for movie in movies:
               gather.say(f'For {movie.title} press {movie.digits}')

       vr.say('We did not receive your selection')
       vr.redirect(reverse('choose-theater'))

   return HttpResponse(str(vr), content_type='text/xml')

@csrf_exempt
def list_showtimes(request: HttpRequest) -> HttpResponse:
   validate_django_request(request)
   vr = VoiceResponse()

   digits = request.POST.get('Digits')
   theater = Theater.objects.get(id=request.GET['theater'])

   try:
       movie = Movie.objects.get(id=digits)

   except Movie.DoesNotExist:
       vr.say('Please select a movie from the list.')
       vr.redirect(f'{reverse("choose-movie")}?theater={theater.id}')

   else:
       # User selected movie and theater, search shows in the next 12 hours:
       from_time = timezone.now()
       until_time = from_time + datetime.timedelta(hours=12)
       shows = list(
           Show.objects.filter(
               theater=theater,
               movie=movie,
               starts_at__range=(from_time, until_time),
           ).order_by('starts_at')
       )
       if len(shows) == 0:
           vr.say('Sorry, the movie is not playing any time soon in this theater.')
       else:
           showtimes = ', '.join(show.starts_at.time().strftime('%I:%M%p') for show in shows)
           vr.say(f'The movie {movie.title} will be playing at {theater.name} at {showtimes}')

       vr.say('Thank you for using movie info!')
       vr.hangup()

   return HttpResponse(str(vr), content_type='text/xml')
