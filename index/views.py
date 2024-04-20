from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.forms import UserCreationForm

# Create your views here.
def index(request):
    return render(request, 'index.html')

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