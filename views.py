from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from django.contrib import messages
from .models import Beneficiary, Campaign, Donation
from .serializers import CampaignSerializer, DonationSerializer

# Create your views here.

def home(request):
    return render(request, 'index.html')

@login_required
def beneficiaries(request):
    all_beneficiaries = Beneficiary.objects.all()
    return render(request, 'beneficiaries.html', {'beneficiaries': all_beneficiaries})

@login_required
def donate(request, beneficiary_id):
    beneficiary = get_object_or_404(Beneficiary, id=beneficiary_id)
    if request.method == 'POST':
        amount = request.POST.get('amount')  # Get the amount from the form
        Donation.objects.create(donor=request.user, beneficiary=beneficiary, amount=amount)
        messages.success(request, f'Thank you for donating ${amount} to {beneficiary.name}!')
        return redirect('home')
    return render(request, 'donate.html', {'beneficiary': beneficiary})

def about(request):
    return render(request, 'about.html')

def contact(request):
  if request.method == "POST":
    name = request.POST.get("name")
    email = request.POST.get("email")
    subject = request.POST.get("subject")
    message = request.POST.get("message")

    # Construct the email message
    full_message = f"From: {name} <{email}>\n\n{message}"

    try:
      # Send the email
      send_mail(subject, full_message, email, ["your_email@example.com"])
      messages.success(request, "Your message has been sent successfully!")
    except Exception as e:
      messages.error(request, f"Error sending message: {str(e)}")

    return redirect("contact")  # Redirect back to the contact page

  return render(request, "contact.html")


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log the user in after registration
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']  # Updated to use username instead of email
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Redirect to homepage after login
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')

def logout_user(request):
    logout(request)
    return redirect('home')

@api_view(['GET', 'POST'])
def campaign_list(request):
    if request.method == 'GET':
        campaigns = Campaign.objects.all()
        serializer = CampaignSerializer(campaigns, many=True)
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = CampaignSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def make_donation(request):
    serializer = DonationSerializer(data=request.data)
    if serializer.is_valid():
        donation = serializer.save()
        if donation.campaign:  # Ensure the campaign field exists
            campaign = donation.campaign
            campaign.current_amount += donation.amount
            campaign.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




