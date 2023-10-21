from django.shortcuts import render


from .models import *
from uuid import uuid4
from django.contrib.sessions.models import Session
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.core.cache import cache
from django.contrib.auth import authenticate
from django.conf import settings
from django.utils import timezone
from django.core.validators import validate_email





#---------->  FUNCTIONS  <----------#

def is_valid_email(email):
    return validate_email(email)

def user_exist(username):
    try:
        CustomUser.objects.get(username=username)
        return True
    except CustomUser.DoesNotExist:
        return False 
    
def email_exist(email):
    try:
        CustomUser.objects.get(email=email)
        return True
    except CustomUser.DoesNotExist:
        return False 

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0] 
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


#---------->  END FUNCTIONS  <----------#




#---------->  VIEWS  <----------#

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
 
    ip = get_client_ip(request)

    # Get login attemps for antispam / bruteforce attacks
    attempts = cache.get(ip, 0)

    # Check if the attempts have exceeded the limit
    if attempts >= settings.MAX_REGISTRATION_ATTEMPTS:
        return Response({"detail": "Too many registration attempts."}, status=status.HTTP_429_TOO_MANY_REQUESTS)

    # Get username, password and mail from request
    username = request.data.get("username")
    email = request.data.get("email")
    password = request.data.get("password")

    # Check if username, email and password are not empty
    if not username or not password or not email:
        return Response({"detail": "Username, mail and password required."}, status=status.HTTP_400_BAD_REQUEST)
    # Check username length
    if len(username) < 14:
        # Increse login attemps
        attempts += 1
        return Response({"detail": "The username must be at least 14 characters long."}, status=status.HTTP_400_BAD_REQUEST)

    # Check password length for security
    if len(password) < 14:

        # Increse login attemps
        attempts += 1

        return Response({"detail": "The password must be at least 14 characters long."}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if user already exist
    if user_exist(username=username):

        # Increse login attemps
        attempts += 1

        return Response({"detail": "Username already exist."}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check email format
    if is_valid_email(email=email):
        return Response({"detail": "E-mail not valid."}, status=status.HTTP_400_BAD_REQUEST)
    
    if email_exist(email=email):

        # Increse login attemps
        attempts += 1

        return Response({"detail": "Username already exist."}, status=status.HTTP_400_BAD_REQUEST)

    # Crete new user in db
    user = CustomUser.objects.create_user(username=username, email=email, password=password, email_confirmed=False)

    # Get auth token
    token = Token.objects.create(user=user)

    # Increase registration attemps
    cache.set(ip, attempts, settings.REGISTRATION_TIMEOUT_SECONDS)

    # Return token and message
    return Response({"token": token.key,
                     "detail": "Registered successfully."}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    # Get username and password from request
    username = request.data.get("username")
    password = request.data.get("password")

    # Check if credentials are valid, so let login the user
    user = authenticate(request, username=username, password=password)
    # Check auth status and login
    if user is not None:
        # Get auth token
        token, created = Token.objects.get_or_create(user=user)

        # Return login token
        return Response({'token': token.key, "detail": "Logged."}, status=status.HTTP_202_ACCEPTED)
    else:
        return Response({"detail": "Wrong credentials."}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def unlog_all_sessions(request):
    """
    View function to delete all user's sessions
    """

    # Get user
    User = get_user_model()
    user = User.objects.get(username=request.user.username)

    # Get all sessions
    sessions = Session.objects.filter(expire_date__gte=timezone.now())

    # Look for the user's sessions
    for session in sessions:
        session_data = session.get_decoded()
        if user.id == session_data.get('_auth_user_id'):
            session.delete()  # Delete the session













#---------->  END VIEWS  <----------#




