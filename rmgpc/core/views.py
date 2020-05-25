import os
import json
import subprocess

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.utils.translation import gettext
from django.utils import translation
from django.conf import settings as st
from django.contrib.auth import views as auth_views

from .models import Sequence, Mode, Manual, Auto, Settings_base
from .misc import config, parser


def _gather_info():
    seq_all = Sequence.objects.all()
    manual_all = Manual.objects.all()
    auto_all = Auto.objects.all()
    pin_input = Mode.objects.filter(mode='I')
    return (seq_all, manual_all, auto_all, pin_input)

class MyLogin(auth_views.LoginView):

    template_name = 'login.html'
    extra_context = {
        'cur_lang': lambda: Settings_base.objects.get(name='default').lang
    }


@login_required
def get_man_status(request):
    out = {}
    for man in Manual.objects.all():
        out[man.id] = man.active_now
    out = json.dumps(out)
    return HttpResponse(out, content_type='application/json')


@login_required
def home(request):
    # request.session.set_expiry(300)
    cur_lang = Settings_base.objects.get(name='default').lang
    translation.activate(cur_lang)
    seq_all, manual_all, auto_all, pin_input = _gather_info()
    context = {
        'seq_all': seq_all,
        'manual_all': manual_all,
        'auto_all': auto_all,
        'pin_input': pin_input,
    }
    response = render(request, 'home.html', context)
    response.set_cookie(st.LANGUAGE_COOKIE_NAME, cur_lang)
    return response


@login_required
def new_manual(request):
    new_name = request.POST['new_manual']
    is_act_always = request.POST['active_always']
    if not int(is_act_always):
        active_pin = request.POST['active_pin']
        active_state = request.POST['active_state']
    else:
        active_pin = 'no'
        active_state = 'no'
    seq_all, manual_all, auto_all, pin_input = _gather_info()
    if Manual.objects.filter(
        name=new_name,
        active_always=is_act_always,
        active_pin=active_pin,
        active_state=active_state
    ):
        if active_state == 'L':
            active_state = gettext('Low')
        else:
            active_state = gettext('High')
        if not int(is_act_always):
            error_message_man = gettext('Sequence "%(name)s" active when\
            %(state)s on pin "%(pin)s" is already in manual!') % {
                'name': new_name,
                'state': active_state,
                'pin': active_pin
            }
        else:
            error_message_man = gettext('Sequence "%s" is already in \
                manual!') % new_name
        manual_all = Manual.objects.all()
        response = render(request, 'home.html', {
            'error_message_man': error_message_man,
            'manual_all': manual_all,
            'seq_all': seq_all,
            'auto_all': auto_all,
            'pin_input': pin_input,
        })
        return response
    else:
        manual = Manual(
            name=new_name,
            active_always=is_act_always,
            active_pin=active_pin,
            active_state=active_state)
        manual.save()
        return HttpResponseRedirect(reverse('home'))


@login_required
def execute_man(request):
    man_id = request.POST['id']
    name = Manual.objects.get(pk=man_id).name
    name = name.replace(' ', '_') + '.sh'
    path_file = os.path.join(config.SEQ_DIR, name)
    os.system('bash %s' % path_file)
    return HttpResponseRedirect(reverse('home'))


@login_required
def delete_man(request):
    for i in (list(request.POST.keys())):
        if i.isdigit():
            Manual.objects.get(pk=i).delete()
    return HttpResponseRedirect(reverse('home'))


@login_required
def new_auto(request):
    new_name = request.POST['new_auto_name']
    new_pin = request.POST['new_auto_pin']
    new_state = request.POST['new_auto_state']
    new_relief = request.POST['new_auto_relief']
    seq_all, manual_all, auto_all, pin_input = _gather_info()
    if Auto.objects.filter(
        name=new_name,
        trigger_pin=new_pin,
        trigger_state=new_state,
        on_relief=new_relief
    ):
        if new_state == 'L':
            new_state = gettext('Low')
        else:
            new_state = gettext('High')
        error_message_auto = gettext('Sequence "%(name)s" waiting for\
        %(state)s on pin "%(pin)s" (relief = %(relief)s) is already in \
        auto!') % {
            'name': new_name,
            'state': new_state,
            'pin': new_pin,
            'relief': new_relief
        }
        return render(request, 'home.html', {
            'error_message_auto': error_message_auto,
            'manual_all': manual_all,
            'auto_all': auto_all,
            'seq_all': seq_all,
            'pin_input': pin_input,
        })
    else:
        path_file = os.path.join(config.WORK_DIR, 'auto.py')
        name = new_name.replace(' ', '_')
        relief = new_relief.replace(' ', '_')
        subprocess.Popen([
            config.INTERPRETER, path_file, name, new_pin, new_state, relief])
        auto = Auto(
            name=new_name,
            trigger_pin=new_pin,
            trigger_state=new_state,
            on_relief=new_relief)
        auto.save()
        path_file = os.path.join(config.WORK_DIR, 'auto.txt')
        with open(path_file, 'a') as file:
            print(name, new_pin, new_state, relief, file=file)
        return HttpResponseRedirect(reverse('home'))


@login_required
def delete_auto(request):
    for i in (list(request.POST.keys())):
        if i.isdigit():
            auto = Auto.objects.get(pk=i)
            name = auto.name.replace(' ', '_')
            pin = auto.trigger_pin
            state = auto.trigger_state
            on_relief = auto.on_relief
            inf = ' '.join([name, pin, state, on_relief])
            os.system(
                "kill -9 $(ps aux | grep -v \
                        'awk' | awk '/%s/{print $2}')" % inf)
            path_file = os.path.join(config.WORK_DIR, 'auto.txt')
            with open(path_file, 'r') as file:
                out = []
                for line in file.readlines():
                    if inf not in line:
                        out.append(line)
            print(out)
            print(inf)
            with open(path_file, 'w') as file:
                for line in out:
                    print(line, file=file, end='')
            auto.delete()
    return HttpResponseRedirect(reverse('home'))


def redirect_view(request):
    return redirect('home')


@login_required
def mode(request):
    mode_initial = Mode.objects.all()
    return render(request, 'mode.html', {'mode_initial': mode_initial})


@login_required
def mode_save(request):
    for i in config.PIN_SET:
        pin = i
        new_mode = request.POST[pin]
        old_mode = Mode.objects.get(pin=pin).mode
        if old_mode != new_mode:
            m = Mode.objects.get(pin=pin)
            m.mode = new_mode
            m.save()
    path_file = os.path.join(config.WORK_DIR, 'set_mode.txt')
    with open(path_file, 'w') as file:
        for line in Mode.objects.all():
            print('%s %s' % (line.pin, line.mode), file=file)
    path_file = os.path.join(config.WORK_DIR, 'set_mode.py')
    os.system('python3 %s' % path_file)
    return HttpResponseRedirect(reverse('mode'))


@login_required
def sequence(request):
    seq_all = Sequence.objects.all()
    return render(request, 'sequence.html', {'seq_all': seq_all})


@login_required
def new_seq(request):
    new_name = request.POST['name']
    new_content = request.POST['content']
    seq_all = Sequence.objects.all()
    if (not new_name) or (not new_content):
        error_message_add = gettext('Name or content is empty!')
        return render(request, 'sequence.html', {
            'error_message_add': error_message_add,
            'seq_all': seq_all,
            'placeholder_content': new_content,
            'placeholder_name': new_name,
        })
    if Sequence.objects.filter(name=new_name):
        error_message_add = gettext('Name %s is already in use!') % new_name
        return render(request, 'sequence.html', {
            'error_message_add': error_message_add,
            'seq_all': seq_all,
            'placeholder_content': new_content,
        })
    else:
        check_passed, mistake = parser.spell_check(new_content, new_name)
        if not check_passed:
            error_message_add = gettext('Mistake detected! %s') % mistake
            return render(request, 'sequence.html', {
                'error_message_add': error_message_add,
                'seq_all': seq_all,
                'placeholder_content': new_content,
                'placeholder_name': new_name,
            })
        else:
            seq = Sequence(name=new_name, content=new_content)
            seq.save()
            return HttpResponseRedirect(reverse('sequence'))


@login_required
def delete_seq(request):
    seq_all = Sequence.objects.all()
    for i in (list(request.POST.keys())):
        if i.isdigit():
            seq_id = i
            seq = Sequence.objects.get(pk=seq_id)
            man_count = Manual.objects.filter(name=seq.name).count()
            auto_count = Auto.objects.filter(name=seq.name).count()
            if man_count or auto_count:
                error_message_delete = gettext('Sequence "%s" is used in \
                    triggers! Delete triggers first!') % seq.name
                return render(request, 'sequence.html', {
                    'error_message_delete': error_message_delete,
                    'seq_all': seq_all,
                })
            name = seq.name.replace(' ', '_') + '.sh'
            path_file = os.path.join(config.SEQ_DIR, name)
            os.remove(path_file)
            seq.delete()
    return HttpResponseRedirect(reverse('sequence'))


@login_required
def settings_page(request):
    cur_set = Settings_base.objects.get(name='default')
    context = {'cur_set': cur_set}
    return render(request, 'settings.html', context)


@login_required
def settings_new(request):
    cur_set = Settings_base.objects.get(name='default')
    # set language
    old_lang = cur_set.lang
    new_lang = request.POST['set_lang']
    if old_lang != new_lang:
        cur_set.lang = new_lang
        cur_set.save()
    translation.activate(new_lang)
    context = {'cur_set': cur_set}
    response = render(request, 'settings.html', context)
    response.set_cookie(st.LANGUAGE_COOKIE_NAME, new_lang)
    return response
    # set ...
