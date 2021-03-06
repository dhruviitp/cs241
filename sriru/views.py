from django.http import HttpResponse, HttpResponseRedirect
from django.core.context_processors import csrf
from django.template import RequestContext, loader
from django.shortcuts import render, render_to_response, redirect
from django.views import generic
from django.contrib.auth import authenticate, login, logout
from sriru.models import *
from sriru.forms import *
from django import forms
import hashlib

def manual(request):
	return render_to_response('sriru/manual.html')

def prof(request,prof_id):
	p = Professor.objects.get(emp_no=prof_id)
	q = r = a = s = {}
	a = MessageStudProf.objects.filter(msg_to = p, seen = True)
	b = MessageStudProf.objects.filter(msg_to = p, seen = False)	
	q = Project_Unapproved.objects.filter(PI = p,approved=0)
	r = Project_Unapproved.objects.filter(PI = p,approved=2)
	s = Purchase.objects.filter(approval=-1,sanc_head__project__PI = p)
	t = Purchase.objects.filter(approval=0,sanc_head__project__PI = p)
	u = Purchase.objects.filter(approval=1,sanc_head__project__PI = p)
	v = Purchase.objects.filter(approval=2,sanc_head__project__PI = p)
	w = Purchase.objects.filter(approval=3,sanc_head__project__PI = p)
	y = Purchase.objects.filter(approval=4,sanc_head__project__PI = p)
	if 'userprof' in request.session:
		x = request.session['userprof']
		return render_to_response('sriru/prof.html',{'msg_seen':a,'msg_unseen':b,'approvedproj':r,'unapprovedproj':q,'prof':p,'rejpur':s,'pur0':t,'pur1':u,'pur2':v,'pur3':w,'pur4':y,'r':x})
	else:
		return render_to_response('sriru/prof.html',{'approvedproj':r,'prof':p})

def director(request):
	q = r = s = {}	
	q = Project_Unapproved.objects.filter(approved=2)
	r = Project_Unapproved.objects.filter(approved=1)
	s = Purchase.objects.filter(approval=-2)
	if 'userdir' in request.session:
		x = request.session['userdir']
		return render_to_response('sriru/director.html',{'upcomproj':r,'approvedproj':q,'dirpur':s})
	else:
		return HttpResponseRedirect('/sriru/super/')

def stud(request,stud_id):
	p = Student.objects.get(pk=stud_id)
	q = Fellowship.objects.filter(researcher=p)
	if 'userstud' in request.session:
		x = request.session['userstud']
		return render_to_response('sriru/stud.html',{'s':p,'fellow':q,'r':x})
	else:
		return render_to_response('sriru/stud.html',{'s':p})

def proj(request,project_id):
	x = ""
	if '1' in request.session:
		x = request.session['1']
		del request.session['1']
	q = Project_Unapproved.objects.get(pk=project_id)
	p = Sponsorship.objects.filter(project = q)
	if 'userprof' in request.session or 'useroff' in request.session or 'useradmin' in request.session:
		return render_to_response('sriru/proj.html',{'project':q,'spons':p})
	elif 'userstud' in request.session:
		return render_to_response('sriru/proj.html',{'x':x,'project':q,'stud':request.session['userstud']},RequestContext(request))
	elif 'userspons' in request.session:
		return render_to_response('sriru/proj.html',{'x':x,'project':q,'spons':p,'sp':request.session['userspons']},RequestContext(request))
	else:
		return render_to_response('sriru/proj.html',{'project':q})

def msg(request):
	if request.POST:
		if 'userstud' in request.session:
			to = request.POST.get('to')
			from_s = request.POST.get('from')
			msg = request.POST.get('msg')
			proj = request.POST.get('project')
			prof = Professor.objects.get(pk=to)
			stud = Student.objects.get(pk = from_s)
			project = Project_Unapproved.objects.get(pk=proj)
			p = MessageStudProf()
			p.msg_from = stud
			p.msg_to = prof
			p.project = project
			p.msg = msg
			p.save()
			request.session['1'] = "MESSAGE SENT"
			return HttpResponseRedirect('/sriru/proj/'+proj+'/',request)
		if 'userspons' in request.session:
			to = request.POST.get('to')
			from_s = request.POST.get('from')
			msg = request.POST.get('msg')
			proj = request.POST.get('project')
			stud = Sponsor.objects.get(pk = from_s)
			project = Project_Unapproved.objects.get(pk=proj)
			p = MessageSponsAdmin()
			p.msg_from = stud
			p.msg_to = to
			p.project = project
			p.msg = msg
			p.save()
			request.session['1'] = "MESSAGE SENT"
			return HttpResponseRedirect('/sriru/proj/'+proj+'/',request)
		else:
			return redirect('/sriru/')
	else:
		return redirect('/sriru/')

def msg_seen(request,_id):
	if 'userprof' in request.session:
		x = MessageStudProf.objects.get(pk = _id)
		x.seen = True
		x.save()
		y = request.session['userprof']
		return redirect('/sriru/prof/'+y+"/")
	elif 'useradmin' in request.session:
		x = MessageSponsAdmin.objects.get(pk = _id)
		x.seen = True
		x.save()
		return redirect('/sriru/admin')
	else:
		return HttpResponseRedirect('/sriru/')

def spons(request,spons_name):
	p = q = r = {}
	p = Sponsor.objects.get(username=spons_name)
	q = Sponsorship.objects.filter(sponsor=p)
	r = Project_Unapproved.objects.filter(approved=1)
	if 'userspons' in request.session or 'useroff' in request.session or 'useradmin' in request.session:
		x = request.session['userspons']
		return render_to_response('sriru/spons.html',{'spons':p,'q':q,'project':r,'r':x})
	else:
		return render_to_response('sriru/spons.html',{'spons':p})

def tenderlist(request):
	p={}
	p = Purchase_duration.objects.all()
	return render_to_response('sriru/tenderlist.html',{'tender':p})

def tender(request,ten_id):
	p = Purchase_duration.objects.get(pk=ten_id)
	return render_to_response('sriru/tender.html',{'tender':p})

def index(request):
	state = "Please login below to continue"
	x = ""
	if request.POST:
		user = request.POST.get('user')
		password = request.POST.get('pass')
		hash_object = hashlib.sha1(password)
		password = hash_object.hexdigest()
		type = request.POST.get('des')
		if type == 'stu' and Student.objects.filter(roll_no = user, password = password).exists() :
			Student.objects
			s = Student.objects.get(roll_no = user)
			request.session['userstud'] = s.roll_no
			return redirect('/sriru/stud/'+s.roll_no+'/')
		elif type == 'fac' and Professor.objects.filter(emp_no = user, password = password).exists():
			Professor.objects
			p = Professor.objects.get(emp_no = user)
			request.session['userprof'] = p.emp_no
			return redirect('/sriru/prof/'+p.emp_no+'/')
		elif type == 'spons' and Sponsor.objects.filter(username = user, password = password).exists():
			Sponsor.objects
			sp = Sponsor.objects.get(username = user)
			request.session['userspons'] = sp.username
			return redirect('/sriru/spons/'+sp.username+'/')
		else :
			state = "USER-ID Password combination not found"
			return render_to_response('sriru/index.html',{'state':state,'r':x},RequestContext(request))
	return render_to_response('sriru/index.html',{'state':state,'r':x},RequestContext(request))

def superlogin(request):
	state = "Please enter password"
	x = ""
	if request.POST:
		user = request.POST.get('user')
		password1 = request.POST.get('pass')
		hash_object = hashlib.sha1(password1)
		password = hash_object.hexdigest()
		if SuperUser.objects.filter(name = user, password = password).exists() :
			SuperUser.objects
			s = SuperUser.objects.get(name = user)
			if user == 'sriru':
				request.session['useroff'] = s.pk
				return redirect('/sriru/officer')
			elif user == 'admin':
				request.session['useradmin'] = s.pk
				return redirect('/sriru/admin')
		elif SuperUser.objects.filter(name = user, password = password1).exists():
			s = SuperUser.objects.get(name = user)
			request.session['userdir'] = s.pk
			return redirect('/sriru/director')
		else :
			state = "USER-ID Password combination not found"
			return render_to_response('sriru/superlogin.html',{'state':state,'r':x},RequestContext(request))
	return render_to_response('sriru/superlogin.html',{'state':state,'r':x},RequestContext(request))

def logout1(request):
	try:
		del request.session['userstud']
	except KeyError:
		pass
	return HttpResponseRedirect('/sriru/')

def logout2(request):
	try:
		del request.session['userprof']
	except KeyError:
		pass
	return HttpResponseRedirect('/sriru/')

def logout3(request):
	try:
		del request.session['userspons']
	except KeyError:
		pass
	return HttpResponseRedirect('/sriru/')

def logout4(request):
	try:
		del request.session['useroff']
	except KeyError:
		pass
	return HttpResponseRedirect('/sriru/super')

def logout5(request):
	try:
		del request.session['useradmin']
	except KeyError:
		pass
	return HttpResponseRedirect('/sriru/super')

def logout6(request):
	try:
		del request.session['userdir']
	except KeyError:
		pass
	return HttpResponseRedirect('/sriru/super')

def generateTable(request,proj_id):
	q = Project_Unapproved.objects.get(pk=proj_id)
	p = Sanctioned_Head.objects.filter(project = q)
	for x in p:
		x.left_amt = x.given_amt - x.used_amt
		x.save()
	return render_to_response('sriru/sanctable.html',{'sanc':p})

def apprsanc(request,proj_id):
	q = Project_Unapproved.objects.get(pk=proj_id)
	p = Sanctioned_Head.objects.filter(project = q)
	if request.POST:
		for name in request.POST:
			if name == "csrfmiddlewaretoken" or name == "submit":
				r = ""
			else:
				r = Sanctioned_Head.objects.get(pk=name)
				r.appr_amount = request.POST.get(name)
				r.save()
		return HttpResponseRedirect('/sriru/admin')
	return render_to_response('sriru/appr_sanchead.html',{'sanc':p,'proj':q, 'proj_id':proj_id},RequestContext(request))

def up_sanc(request,proj_id):
	q = Project_Unapproved.objects.get(pk=proj_id)
	p = Sanctioned_Head.objects.filter(project = q)
	if request.POST:
		for name in request.POST:
			if name == "csrfmiddlewaretoken" or name == "submit":
				r = ""
			else:
				r = Sanctioned_Head.objects.get(pk=name)
				x = r.given_amt
				r.given_amt = request.POST.get(name)
				r.given_amt = int(r.given_amt) + x
				r.save()
		return HttpResponseRedirect('/sriru/admin')
	return render_to_response('sriru/up_sanc.html',{'sanc':p,'proj':q, 'proj_id':proj_id},RequestContext(request))

def copi(request,prof_id):
	q = Professor.objects.get(emp_no=prof_id)
	p = Project_Unapproved.objects.filter(PI = q)
	if request.POST:
		for name in request.POST:
			if name == "csrfmiddlewaretoken" or name == "submit":
				r = ""
			else:
				r = Project_Unapproved.objects.get(pk=name)
				s = request.POST.get(name)
				t = Professor.objects.get(emp_no=s)
				r.save()
				r.co_PI.add(t)
				r.save()
		x = request.session['userprof']
		return HttpResponseRedirect('/sriru/prof/'+x+'/')
	return render_to_response('sriru/copi.html',{'proj':p,'prof':q},RequestContext(request))

def projupdt(request,proj_id):
	p = Project_Unapproved.objects.get(id = proj_id)
	if request.POST:
		p.updates = request.POST.get('update')
		p.save()
		x = request.session['userprof']
		return HttpResponseRedirect('/sriru/prof/'+x+'/')
	return render_to_response('sriru/projupdt.html',{'proj':p},RequestContext(request))

def officer(request):
	p = {}
	p = Purchase.objects.filter(approval=0)
	q = {}
	q = Project_Unapproved.objects.filter(approved=0)
	if 'useroff' in request.session:
		return render_to_response("sriru/officer.html",{"purchase":p,"project":q},RequestContext(request))
	else:
		return HttpResponseRedirect('/sriru/super')

def admin(request):
	a = b = q = p = r = s = t = {}
	a = MessageSponsAdmin.objects.filter(msg_to='admin', seen = True)
	b = MessageSponsAdmin.objects.filter(msg_to='admin', seen = False)
	p = Purchase.objects.filter(approval=1)
	q = Purchase.objects.filter(approval=2)
	r = Purchase.objects.filter(approval=3)
	s = Project_Unapproved.objects.filter(approved=1)
	t = Project_Unapproved.objects.filter(approved=2)
	if 'useradmin' in request.session:
		return render_to_response('sriru/admin.html',{'msg_seen':a,'msg_unseen':b,'project':s,'project1':t,'purchase':p,'purchase1':q,'purchase2':r})
	else:
		return HttpResponseRedirect('/sriru/super')

def grant(request,proj_id):
	if request.POST:
		form = GrantForm(request.POST)
		if form.is_valid():
			form.save()
			return HttpResponseRedirect('/sriru/up_sanc/'+proj_id+'/')
	else:
		form = GrantForm()
		form.fields['sponsorship'].queryset = Sponsorship.objects.filter(project=Project_Unapproved.objects.get(pk=proj_id))

	args = {}
	args.update(csrf(request))

	args['form'] = form
	args['proj_id'] = proj_id

	return render_to_response('sriru/grant.html',args)

def approve1(request,pur_id):
	Purchase.objects
	p = Purchase.objects.get(pk=pur_id)
	p.approval=1
	p.save()
	return HttpResponseRedirect("/sriru/officer")

def reject1(request,pur_id):
	Purchase.objects
	p = Purchase.objects.get(pk=pur_id)
	p.approval=-1
	p.save()
	return HttpResponseRedirect("/sriru/officer")

def rejdir(request,pur_id):
	Purchase.objects
	p = Purchase.objects.get(pk=pur_id)
	p.approval = -2
	p.save()
	return HttpResponseRedirect("/sriru/officer")

def approve2(request,pur_id):
	Purchase.objects
	p = Purchase.objects.get(pk=pur_id)
	p.approval +=1
	p.save()
	return HttpResponseRedirect("/sriru/purchasedur") #pur_dur form

def dirpur(request,pur_id):
	Purchase.objects
	p = Purchase.objects.get(pk=pur_id)
	p.approval += 1
	p.save()
	return HttpResponseRedirect("/sriru/admin")

def approve3(request,pur_id):
	Purchase.objects
	p = Purchase.objects.get(pk=pur_id)
	p.approval +=1
#	p.sanc_head.given_amt += 	
	p.save()
	return HttpResponseRedirect("/sriru/comppurchase") #comp_pur form

def dirapprove(request,pur_id):
	Purchase.objects
	p = Purchase.objects.get(pk=pur_id)
	p.approval = 1	
	p.save()
	return HttpResponseRedirect("/sriru/director") 

def das(request):
	Completed_Purchase.objects
	Purchase.objects
	p = {}
	q = {}
	q = Purchase.objects.filter(approval=3)
	p = Completed_Purchase.objects.filter(purchase=q)
	amt = 0
	for i in p:
		amt += i.cost
	return render_to_response('sriru/das.html',{'comp_pur':p,'amt':amt})

def dascomp(request):
	Completed_Purchase.objects
	Purchase.objects
	p = {}
	q = {}
	q = Purchase.objects.filter(approval=3)
	p = Completed_Purchase.objects.filter(purchase=q)
	for i in p:
		j = i.purchase
		j.approval = 4
		j.save()
		i.save()
	return HttpResponseRedirect('/sriru/admin')



def projapprove(request,proj_id):
	Project_Unapproved
	p = Project_Unapproved.objects.get(pk=proj_id)
	p.approved += 1
	p.save()
	return HttpResponseRedirect("/sriru/officer")

def projreject(request,pro_id):
	Project_Unapproved
	p = Project_Unapproved.objects.get(pk=pro_id)
	p.approved -= 1
	p.save()
	return HttpResponseRedirect("/sriru/officer")

def sanction(request):
	if request.POST:
		form = SanctionHead(request.POST)
		if form.is_valid():
			form.save()
			if 'submit1' in request.POST:
				return HttpResponseRedirect('/sriru/sanctions')
			else:
				x = request.session['userprof']
				return HttpResponseRedirect('/sriru/prof/'+x+'/')
	else:
		form = SanctionHead()

	args = {}
	args.update(csrf(request))

	args['form'] = form

	return render_to_response('sriru/sanction.html',args)

def newproj(request):
	if request.POST:
		form = ProjectForm(request.POST)
		if form.is_valid():
			form.save()
#			x = request.session['user']
			return HttpResponseRedirect('/sriru/sanctions')
	else:
		form = ProjectForm()

	args = {}
	args.update(csrf(request))

	args['form'] = form

	return render_to_response('sriru/form_project.html',args)

def fellowship(request):
	if request.POST:
		form = FellowshipForm(request.POST)
		if form.is_valid():
			form.save()
			x = request.session['userprof']
			return HttpResponseRedirect('/sriru/prof/'+x+'/')
	else:
		form = FellowshipForm()

	args = {}
	args.update(csrf(request))

	args['form'] = form

	return render_to_response('sriru/fellowship.html',args)


def approveproj(request,proj_id):
	p = Project_Unapproved.objects.get(pk=proj_id)
	p.approved = 2
	p.save()
	return HttpResponseRedirect('/sriru/sponsorship/'+proj_id+'/')

def updateSancHead(request,proj_id):
	Project_Unapproved.objects
	Sanctioned_Head.objects
	p = Project_Unapproved.objects.get(pk=proj_id)
	q = Sanctioned_Head.objects.filter(project=p)
	data = {'Approved Amount': q.appr_amount}
        form = UserQueueForm(initial=data)
	render_to_response('sriru/appr_sanchead',{'form':form})

def addsponsorship(request,proj_id):
	if request.POST:
		form = SponsorshipForm(request.POST)
		if form.is_valid():
			form.save()
#			x = request.session['user']
			if 'submit1' in request.POST:
				return HttpResponseRedirect('/sriru/sponsorship/'+proj_id+'/')
			else:
				return HttpResponseRedirect('/sriru/appr_sanchead/'+proj_id+'/')
	else:
		form = SponsorshipForm()

	args = {}
	args.update(csrf(request))

	args['form'] = form
	args['proj_id'] = proj_id

	return render_to_response('sriru/form_sponsorship.html',args)

def purchase(request):
	if request.POST:
		form = PurchaseForm(request.POST)
		if form.is_valid():
			p=form.save()
			p.tot_est_cost = p.est_cost * p.quantity
			p.save()
			x = request.session['userprof']
			return HttpResponseRedirect('/sriru/prof/'+x+'/')
	else:
		form = PurchaseForm()
	args = {}
	args.update(csrf(request))
	args['form'] = form

	return render_to_response('sriru/purchase.html',args)

def purchaseduration(request):
	if request.POST:
		form = PurchaseDurationForm(request.POST)
		if form.is_valid():
			form.save()
			return HttpResponseRedirect('/sriru/admin')
	else:
		form = PurchaseDurationForm()
	args = {}
	args.update(csrf(request))
	args['form'] = form

	return render_to_response('sriru/purchasedur.html',args)

def completepurchase(request):
	if request.POST:
		form = CompletedPurchaseForm(request.POST)
		if form.is_valid():
			b = form.save()
			c = b.purchase.sanc_head
			c.used_amt += b.cost
			c.save() 
			return HttpResponseRedirect('/sriru/admin')
	else:
		form = CompletedPurchaseForm()
	args = {}
	args.update(csrf(request))
	args['form'] = form

	return render_to_response('sriru/comppurchase.html',args)

def vendadd(request):
	if request.POST:
		form = AddVendors(request.POST)
		if form.is_valid():
			form.save()
			return HttpResponseRedirect('/sriru/admin')
	else:
		form = AddVendors()
	args = {}
	args.update(csrf(request))
	args['form'] = form
	return render_to_response('sriru/vendadd.html',args)

def sponsadd(request):
	if request.POST:
		form = AddSpons(request.POST)
		if form.is_valid():
			b = Sponsor()
			b = form.save(commit=False)
			p = b.password
			hash_object = hashlib.sha1(p)
			b.password = hash_object.hexdigest()
			b.save()
			return HttpResponseRedirect('/sriru/admin')
	else:
		form = AddSpons()
	args = {}
	args.update(csrf(request))
	args['form'] = form
	return render_to_response('sriru/sponsadd.html',args)

def profadd(request):
	if request.POST:
		form = AddProf(request.POST)
		if form.is_valid():
			b = Professor()
			b = form.save(commit=False)
			p = b.password
			hash_object = hashlib.sha1(p)
			b.password = hash_object.hexdigest()
			b.save()
			return HttpResponseRedirect('/sriru/admin')
	else:
		form = AddProf()
	args = {}
	args.update(csrf(request))
	args['form'] = form
	return render_to_response('sriru/profadd.html',args)

def studadd(request):
	if request.POST:
		form = AddStudent(request.POST)
		if form.is_valid():
			b = Student()
			b = form.save(commit=False)
			p = b.password
			hash_object = hashlib.sha1(p)
			b.password = hash_object.hexdigest()
			b.save()
			return HttpResponseRedirect('/sriru/admin')
	else:
		form = AddStudent()
	args = {}
	args.update(csrf(request))
	args['form'] = form

	return render_to_response('sriru/studadd.html',args)

def changepass(request):
	state = ""
	b = False
	npwd = ""
	pwd = ""
	user_npwd = ""
	user_cpwd = "c"
	user = ""
	if request.POST:
		user = request.POST.get('user_name')
		user_pwd = request.POST.get('user_pwd')
		user_npwd = request.POST.get('user_npwd')
		user_cpwd = request.POST.get('user_cpwd')
		hash_object = hashlib.sha1(user_pwd)
		pwd = hash_object.hexdigest()
		#pwd = user_pwd		
		hash_object1 = hashlib.sha1(user_cpwd)
		npwd = hash_object1.hexdigest()
		#npwd = user_cpwd 
	if user_npwd == user_cpwd:
		b = True
	if 'userprof' in request.session:
		x = request.session['userprof']
		if Professor.objects.filter(pk=user,password=pwd).exists() and b == True:
			p = Professor.objects.get(pk=user)
			p.password=npwd
			p.save()
			return redirect('/sriru/prof/'+x+'/')
		elif request.POST and b == False:
			state = "Password doesn't match"
		return render_to_response('sriru/changepass.html',{'a':x,'state':state},RequestContext(request))
	elif 'useradmin' in request.session:
		x = request.session['useradmin']
		if SuperUser.objects.filter(name='admin',password=pwd).exists() and b == True:
			p = SuperUser.objects.get(pk=user)
			p.password=npwd
			p.save()
			return redirect('/sriru/admin')
		elif request.POST and b == False:
			state = "Password doesn't match"
		return render_to_response('sriru/changepass.html',{'d':x,'state':state},RequestContext(request))
	elif 'useroff' in request.session:
		x = request.session['useroff']
		if SuperUser.objects.filter(name='sriru',password=pwd).exists() and b == True:
			p = SuperUser.objects.get(pk=user)
			p.password=npwd
			p.save()
			return redirect('/sriru/officer')
		elif request.POST and b == False:
			state = "Password doesn't match"
		return render_to_response('sriru/changepass.html',{'c':x,'state':state},RequestContext(request))
	elif 'userspons' in request.session:
		x = request.session['userspons']
		if Sponsor.objects.filter(pk=user,password=pwd).exists() and b == True:
			p = Sponsor.objects.get(pk=user)
			p.password=npwd
			p.save()
			return redirect('/sriru/spons/'+x+'/')
		elif request.POST and b == False:
			state = "Password doesn't match"
		return render_to_response('sriru/changepass.html',{'e':x,'state':state},RequestContext(request))
	elif 'userstud' in request.session:
		x = request.session['userstud']
		if Student.objects.filter(pk=user,password=pwd).exists() and b == True:
			p = Student.objects.get(pk=user)
			p.password=npwd
			p.save()
			return redirect('/sriru/stud/'+x+'/')
		elif request.POST and b == False:
			state = "Password doesn't match"
		return render_to_response('sriru/changepass.html',{'b':x,'state':state},RequestContext(request))
	else:
		return HttpResponseRedirect('/sriru/')

def deptadd(request):
	if request.POST:
		form = DeptForm(request.POST)
		if form.is_valid():
			form.save()
			return HttpResponseRedirect('/sriru/admin')
	else:
		form = DeptForm()
	args = {}
	args.update(csrf(request))
	args['form'] = form

	return render_to_response('sriru/deptadd.html',args)

def search_project(request,text):
	if text is None:
		text = ''	
	projects = Project_Unapproved.objects.filter(title__contains=text)

	return render_to_response('sriru/ajax_search.html',{'projects':projects})

