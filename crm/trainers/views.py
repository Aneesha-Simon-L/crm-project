from django.shortcuts import render,redirect,get_object_or_404

from django.views.generic import View

from . models import DistrictChoices

from django . db . models import Q

from django . db import transaction

from . utility import get_employee_id,get_password

from authentication . permissions import  permission_roles

from . models import Trainers

from . forms import  TrainersRegisterForm

from authentication.models import Profile

# from django.contrib.auth.decorators import login_required

from django.utils.decorators import method_decorator

# Create your views here.
    
class GetTrainerObject:

    def get_trainer(self,request,uuid):

        try:

            trainer = Trainers.objects.get(uuid=uuid)

            return trainer

        except:

            return render(request,'errorpages/error-404.html')

# @method_decorator(login_required(login_url='login'),name='dispatch')
# @method_decorator(permission_roles(roles=['Admin', 'Sales']),name='dispatch')
class DashBoardView(View):

    def get(self,request,*args,**kwargs):

        return render(request,'students/dashboard.html')
    

@method_decorator(permission_roles(roles=['Admin','Academic Counsellor']),name='dispatch')
  
class TrainerListView(View):

    def get(self,request,*args,**kwargs):

        query = request.GET.get('query')

        trainers = Trainers.objects.filter(active_status = True)

        if query:

                trainers = Trainers.objects.filter(Q(active_status = True)&(Q(first_name__icontains = query)|Q(last_name__icontains = query)|
                                                                                Q(email__icontains = query)|Q(contact_num__icontains = query)|
                                                                                Q(house_name__icontains = query)|Q(pincode__icontains = query)|
                                                                                Q(course__name__icontains = query)|Q(batch__name__icontains = query)))               

        data = {'trainers' : trainers,'query' : query} 

        return render(request,'trainers/trainer.html',context=data)
    
class TrainerFormView(View):

    def get(self,request,*args,**kwargs):

        form =  TrainersRegisterForm()

        # data = {'districts' : DistrictChoices,'courses' : CourseChoices,'batches' : BatchChoices,'trainers' : TrainerChoices,'form' : form}

        # data = {'numbers' : [1,2,3,4,5]}

        data = {'form' : form}

        return render(request,'trainers/trainer-form.html',context=data)
    
    def post(self,request,*args,**kwargs):

        form = TrainersRegisterForm(request.POST,request.FILES)

        if form.is_valid():

            with transaction.atomic():

                trainer = form.save(commit=False)

                trainer.employee_id = get_employee_id()

                # student.join_date = '2025-02-05'

                username = trainer.email

                password = get_password()

                print(password)

                profile = Profile.objects.create_user(username=username,password=password,role='Trainer')

                trainer.profile = profile

                trainer.save()

            return redirect('trainers-list')
        
        else:

            data = {'form' : form}

            return render(request,'trainers/trainer-form.html',context=data)
        
@method_decorator(permission_roles(roles=['Admin', 'Sales','Academic Counsellor','Trainer']),name='dispatch')       
class TrainerDetailView(View):

    def get(self,request,*args,**kwargs):

        uuid = kwargs.get('uuid')

        # student = get_object_or_404(StudentsView,pk=pk)

        trainer = GetTrainerObject().get_trainer(request,uuid)

        data = {'trainer' : trainer}

        return render(request,'trainers/trainer-detail.html',context=data)
    
@method_decorator(permission_roles(roles=['Admin']),name='dispatch')
class TrainerDeleteView(View):

    def get(self,request,*args,**kwargs):

        uuid = kwargs.get('uuid')

        # try:

        #     student = StudentsView.objects.get(uuid=uuid)

        # except:

        #     return redirect('error-404')

        trainer = GetTrainerObject().get_trainer(request,uuid)
        
        # trainer.delete()

        trainer.active_status = False

        trainer.save()

        return redirect('trainer-list')

@method_decorator(permission_roles(roles=['Admin', 'Sales','Academic Counsellor','Trainer']),name='dispatch')   
class TrainerUpdateView(View):

    def get(self,request,*args,**kwargs):

        uuid = kwargs.get('uuid')

        trainer = GetTrainerObject().get_trainer(request,uuid)

        form = TrainersRegisterForm(instance=trainer)

        data = {'form' : form}

        return render(request,'trainers/trainer-update.html',context=data)
    
    def post(self,request,*args,**kwargs):

        uuid = kwargs.get('uuid')

        student = GetTrainerObject().get_trainer(request,uuid)

        form = TrainersRegisterForm(request.POST,request.FILES,instance=student)

        if form.is_valid():

            form.save()

            return redirect('trainers-list')
        
        else:

            data = {'form' : form}

            return render(request,'trainers/trainers-update.html',context=data)
        