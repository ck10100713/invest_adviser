from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.forms import UserCreationForm
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse

# Create your views here.

def register(request):
	if request.method == 'POST':
		form = UserCreationForm(request.POST)
		print("Errors", form.errors)
		if form.is_valid():
			form.save()
			return redirect('/')
		else:
			return render(request, 'registration/register.html', {'form':form})
	else:
		form = UserCreationForm()
		context = {'form': form}
		return render(request, 'registration/register.html', context)

def about_view(request):
    return render(request, 'about.html')

def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        # 這裡你可以添加邏輯來處理表單數據，例如發送郵件
        send_mail(
            f"Contact Form Submission from {name}",
            message,
            email,
            [settings.DEFAULT_FROM_EMAIL],  # 發送到你的郵箱
        )
        return HttpResponse("Thank you for your message.")
    
    return render(request, 'contact.html')