from django.shortcuts import render,redirect,get_object_or_404

from django.views.generic import View

from . models import DistrictChoices,CourseChoices,BatchChoices,TrainerChoices

from django . db . models import Q

from django . db import transaction

from . utility import get_admission_number,get_password,sent_email

from authentication . permissions import  permission_roles

from . models import StudentsView

from . forms import  StudentsRegisterForm

from authentication.models import Profile

from django.contrib.auth.decorators import login_required

from django.utils.decorators import method_decorator

import threading

import datetime

from payments.models import Payment

# from payments.forms import PaymentStructureForm

# Create your views here.
    
class GetStudentObject:

    def get_student(self,request,uuid):

        try:

            student = StudentsView.objects.get(uuid=uuid)

            return student

        except :

            return render(request,'errorpages/error-404.html')

# @method_decorator(login_required(login_url='login'),name='dispatch')
# @method_decorator(permission_roles(roles=['Admin', 'Sales']),name='dispatch')
class DashBoardView(View):

    def get(self,request,*args,**kwargs):

        return render(request,'students/dashboard.html')
    

@method_decorator(permission_roles(roles=['Admin', 'Sales','Academic Counsellor','Trainer']),name='dispatch')
  
class StudentsListView(View):

    def get(self,request,*args,**kwargs):

        query = request.GET.get('query')

        role  = request.user.role

        if role in ['Trainer']:

            all_students = StudentsView.objects.filter(active_status = True,trainer__profile = request.user)

            if query:

                all_students = StudentsView.objects.filter(Q(active_status = True)&Q(trainer__profile = request.user)&
                                                                                    (Q(first_name__icontains = query)|Q(last_name__icontains = query)|
                                                                                    Q(email__icontains = query)|Q(contact_num__icontains = query)|
                                                                                    Q(house_name__icontains = query)|Q(pincode__icontains = query)|
                                                                                    Q(course__name__icontains = query)|Q(batch__name__icontains = query)))

        elif role in ['Academic Counsellor']:

            all_students = StudentsView.objects.filter(active_status = True,batch__academic_counsellor__profile = request.user)

            if query:

                all_students = StudentsView.objects.filter(Q(active_status = True)&Q(batch__academic_counsellor__profile = request.user)&
                                                                                (Q(first_name__icontains = query)|Q(last_name__icontains = query)|
                                                                                Q(email__icontains = query)|Q(contact_num__icontains = query)|
                                                                                Q(house_name__icontains = query)|Q(pincode__icontains = query)|
                                                                                Q(course__name__icontains = query)|Q(batch__name__icontains = query)))
            
        else:

            all_students = StudentsView.objects.filter(active_status = True)

            if query:

                all_students = StudentsView.objects.filter(Q(active_status = True)&Q(batch__academic_counsellor__profile = request.user)&
                                                                                (Q(first_name__icontains = query)|Q(last_name__icontains = query)|
                                                                                Q(email__icontains = query)|Q(contact_num__icontains = query)|
                                                                                Q(house_name__icontains = query)|Q(pincode__icontains = query)|
                                                                                Q(course__name__icontains = query)|Q(batch__name__icontains = query)))
                


        
            # email, phn no, pincode, house name

        # all_students = StudentsView.objects.all()

        data = {'students' : all_students,'query' : query} 

        return render(request,'students/students.html',context=data)
    
class FormListView(View):

    def get(self,request,*args,**kwargs):

        form =  StudentsRegisterForm()

        # payment_structure_form = PaymentStructureForm()

        # data = {'districts' : DistrictChoices,'courses' : CourseChoices,'batches' : BatchChoices,'trainers' : TrainerChoices,'form' : form}

        # data = {'numbers' : [1,2,3,4,5]}

        data = {'form' : form}

        return render(request,'students/form.html',context=data)
    
    def post(self,request,*args,**kwargs):

        form = StudentsRegisterForm(request.POST,request.FILES)

        # payment_structure_form = StudentsRegisterForm(request.POST)

        if form.is_valid():

            with transaction.atomic():

                student = form.save(commit=False)

                student.adm_number = get_admission_number()

                # student.join_date = '2025-02-05'

                username = student.email

                password = get_password()

                print(password)

                profile = Profile.objects.create_user(username=username,password=password,role='Student')

                student.profile = profile

                student.save()

                # payment section

                fee = student.course.pffer_fee if student.course.offer_fee else student.course.fee

                Payment.objects.create(student=student,amount=fee)

                # sending login credentials to student through mail

                subject = 'Login Credentials'

                # sender = settings.EMAIL_HOST_USER

                recepients = [student.email]

                template = 'email/login-credentials.html'

                join_date = student.join_date

                date_after_10_days = join_date + datetime.timedelta(days=10)

                print(date_after_10_days)

                context = {'name' : f'{student.first_name} {student.last_name}','username' : username,'password' : password,'date_after_10_days' : date_after_10_days}

                # sent_email(subject,recepients,template,context)

                thread = threading.Thread(target=sent_email,args=(subject,recepients,template,context))

                thread.start()

                # if payment_structure_form.is_valid():

                return redirect('students-list')
        
        else:

            data = {'form' : form}

            return render(request,'students/form.html',context=data)
        
@method_decorator(permission_roles(roles=['Admin', 'Sales','Academic Counsellor','Trainer']),name='dispatch')       
class StudentDetailView(View):

    def get(self,request,*args,**kwargs):

        uuid = kwargs.get('uuid')

        # student = get_object_or_404(StudentsView,pk=pk)

        student = GetStudentObject().get_student(request,uuid)

        data = {'student' : student}

        return render(request,'students/student-detail.html',context=data)
    
@method_decorator(permission_roles(roles=['Admin']),name='dispatch')
class StudentDeleteView(View):

    def get(self,request,*args,**kwargs):

        uuid = kwargs.get('uuid')

        # try:

        #     student = StudentsView.objects.get(uuid=uuid)

        # except:

        #     return redirect('error-404')

        student = GetStudentObject().get_student(request,uuid)
        
        # student.delete()

        student.active_status = False

        student.save()

        return redirect('students-list')

@method_decorator(permission_roles(roles=['Admin', 'Sales','Academic Counsellor','Trainer']),name='dispatch')   
class StudentUpdateView(View):

    def get(self,request,*args,**kwargs):

        uuid = kwargs.get('uuid')

        student = GetStudentObject().get_student(request,uuid)

        form = StudentsRegisterForm(instance=student)

        data = {'form' : form}

        return render(request,'students/student-update.html',context=data)
    
    def post(self,request,*args,**kwargs):

        uuid = kwargs.get('uuid')

        student = GetStudentObject().get_student(request,uuid)

        form = StudentsRegisterForm(request.POST,request.FILES,instance=student)

        if form.is_valid():

            form.save()

            return redirect('students-list')
        
        else:

            data = {'form' : form}

            return render(request,'students/student-update.html',context=data)
        
        


        # form_data = request.POST

        # first_name = form_data.get('first_name')

        # last_name = form_data.get('last_name')

        # photo = request.FILES.get('photo')

        # email = form_data.get('email')

        # contact_num = form_data.get('contact_num')

        # house_name = form_data.get('house_name')

        # post_office = form_data.get('post_office')

        # district = form_data.get('district')

        # pincode = form_data.get('pincode')

        # course = form_data.get('course')

        # batch = form_data.get('batch')

        # batch_date = form_data.get('batch_date')

        # trainer = form_data.get('trainer')

        # print(first_name)
        # print(last_name)
        # print(photo)
        # print(email)
        # print(contact_num)
        # print(house_name)
        # print(post_office)
        # print(district)
        # print(pincode)
        # print(course)
        # print(batch)
        # print(batch_date)
        # print(trainer)

        # adm_num = get_admission_number

        # join_date = '2024-08-16'

        # students.objects.create(first_name=first_name,
        #                         last_name=last_name,
        #                         photo=photo,
        #                         email=email,
        #                         contact_num=contact_num,
        #                         house_name=house_name,
        #                         post_office=post_office,
        #                         district=district,
        #                         pincode=pincode,
        #                         course=course,
        #                         batch=batch,
        #                         batch_date=batch_date,
        #                         join_date=join_date,
        #                         trainer_name=trainer)

        # return render(request,'students/students.html')

        
    
# class CourseListView(View):

#     def get(self,request,*args,**kwargs):

#         return render(request,'students/course.html')
    
# class BatchListView(View):

#     def get(self,request,*args,**kwargs):

#         return render(request,'students/batch.html')
    
