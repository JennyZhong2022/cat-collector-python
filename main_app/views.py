from django.shortcuts import render, redirect
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic import ListView, DetailView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Cat, Toy
from .forms import FeedingForm


# Create your views here.
def home(request):
  return render(request, 'home.html')

def about(request):
  return render(request, 'about.html')

@login_required
def cats_index(request):
  # cats = Cat.objects.all()

  # only show's user's cats
  # cats=request.user.cat_set.all()  this work same as below
  cats = Cat.objects.filter(user=request.user)
  
  return render(request, 'cats/index.html', {
    'cats': cats
  })

@login_required
def cats_detail(request, cat_id):
  cat = Cat.objects.get(id=cat_id)
  # First, create a list of the toy ids that the cat DOES have
  id_list = cat.toys.all().values_list('id')
  # Query for the toys that the cat doesn't have
  # by using the exclude() method vs. the filter() method
  toys_cat_doesnt_have = Toy.objects.exclude(id__in=id_list)
  # instantiate FeedingForm to be rendered in detail.html
  feeding_form = FeedingForm()
  return render(request, 'cats/detail.html', {
    'cat': cat, 'feeding_form': feeding_form,
    'toys': toys_cat_doesnt_have
  })

class CatCreate(LoginRequiredMixin,CreateView):
  model = Cat
  fields = ['name', 'breed', 'description', 'age']
  
  def form_valid(self,form):
    # form.instance is the cat
    # Assign the logged in user (self.request.user is the logged in user)
    form.instance.user=self.request.user
     # Let the CreateView's form_valid method
    #  do its regular work(saving the object and redirect)
    return super().form_valid(form)

class CatUpdate(LoginRequiredMixin,UpdateView):
  model = Cat
  fields = ['breed', 'description', 'age']

class CatDelete(LoginRequiredMixin,DeleteView):
  model = Cat
  success_url = '/cats'

@login_required
def add_feeding(request, cat_id):
  # create a ModelForm instance using 
  # the data that was submitted in the form
  form = FeedingForm(request.POST)
  # validate the form
  if form.is_valid():
    # We want a model instance, but
    # we can't save to the db yet
    # because we have not assigned the
    # cat_id FK.
    new_feeding = form.save(commit=False)
    new_feeding.cat_id = cat_id
    new_feeding.save()
  return redirect('detail', cat_id=cat_id)

class ToyList(LoginRequiredMixin,ListView):
  model = Toy

class ToyDetail(LoginRequiredMixin,DetailView):
  model = Toy

class ToyCreate(LoginRequiredMixin,CreateView):
  model = Toy
  fields = '__all__'

class ToyUpdate(LoginRequiredMixin,UpdateView):
  model = Toy
  fields = ['name', 'color']

class ToyDelete(LoginRequiredMixin,DeleteView):
  model = Toy
  success_url = '/toys'

@login_required
def assoc_toy(request, cat_id, toy_id):
  Cat.objects.get(id=cat_id).toys.add(toy_id)
  return redirect('detail', cat_id=cat_id)

@login_required
def unassoc_toy(request, cat_id, toy_id):
  Cat.objects.get(id=cat_id).toys.remove(toy_id)
  return redirect('detail', cat_id=cat_id)


def signup(request):
  error_message = ''
  if request.method == 'POST':
    # This is how to create a 'user' form object
    # that includes the data from the browser
    form = UserCreationForm(request.POST)
    if form.is_valid():
      # This will add the user to the database
      user = form.save()
      # This is how we log a user in via code
      login(request, user)
      return redirect('index')
    else:
      error_message = 'Invalid sign up - try again'
  # A bad POST or a GET request, so render signup.html with an empty form
  form = UserCreationForm()
  context = {'form': form, 'error_message': error_message}
  return render(request, 'registration/signup.html', context)   
