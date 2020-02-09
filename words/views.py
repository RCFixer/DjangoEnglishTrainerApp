from random import shuffle
from datetime import timedelta

from django.shortcuts import render, redirect
from django.utils import timezone
from django.views import View
from django.http import HttpResponse

from .models import Words, UserOldWords


def delete_word(current_user, word, bad_words, good_words, new_words):
    if word in bad_words:
        current_user.profile.bad_words.remove(word)
        current_user.save()
    elif word in good_words:
        current_user.profile.good_words.remove(word)
        current_user.save()
    elif word in new_words:
        current_user.profile.new_words.remove(word)
        current_user.save()


def add_in_old_word(word, current_user, days):
    try:
        word_in_db = UserOldWords.objects.filter(user=current_user).get(
            word=word).word
    except:
        UserOldWords.objects.create(user=current_user,
                                    word=word,
                                    word_count=days,
                                    word_update=timezone.now() +
                                    timedelta(days=days))
    else:
        if word == word_in_db:
            add_word = UserOldWords.objects.filter(user=current_user).filter(
                word=word).first()
            add_word.word_count += 1
            add_word.word_update = timezone.now() + timedelta(
                days=round(add_word.word_count * 1.5))
            add_word.save()


def reset_old_word(word, current_user):
    try:
        word_in_db = UserOldWords.objects.filter(user=current_user).get(
            word=word).word
    except:
        return
    else:
        if word == word_in_db:
            add_word = UserOldWords.objects.filter(user=current_user).filter(
                word=word).first()
            add_word.word_count = 1
            add_word.save()


def home(request):
    current_user = request.user  #текущий пользователь
    test_word = Words.objects.get(name="Angle")
    added_words = current_user.profile.added_words.all()
    if timezone.now(
    ) > current_user.profile.new_words_time:  #если у пользователя давно не добавлялись слова - добавить
        current_user.profile.new_words_time = timezone.now() + timedelta(
            hours=24)
        no_added_words = Words.objects.all().difference(added_words)
        if len(no_added_words) >= 5:
            for i in range(0, 5):
                current_user.profile.new_words.add(no_added_words[i])
                current_user.profile.added_words.add(no_added_words[i])
        elif len(no_added_words) < 5:
            for i in no_added_words:
                current_user.profile.new_words.add(i)
                current_user.profile.added_words.add(i)
        old_words = UserOldWords.objects.filter(user=current_user).all()
        for old_word in old_words:
            if timezone.now() > old_word.word_update:
                current_user.profile.good_words.add(old_word.word)
        current_user.profile.save()
    bad_words = current_user.profile.bad_words
    good_words = current_user.profile.good_words
    new_words = current_user.profile.new_words
    Words.objects.all().difference(added_words)
    if '_bad' in request.POST:  #обработка запросов после нажатия на 3 разные кнопки
        bad_word = request.POST.get('word')
        word = Words.objects.get(name=bad_word)
        delete_word(current_user, word, bad_words.all(), good_words.all(),
                    new_words.all())
        reset_old_word(word, current_user)
        current_user.profile.bad_words.add(word)
        current_user.save()
        return redirect('home')
    elif '_good' in request.POST:
        good_word = request.POST.get('word')
        word = Words.objects.get(name=good_word)
        delete_word(current_user, word, bad_words.all(), good_words.all(),
                    new_words.all())
        add_in_old_word(word, current_user, 3)
        current_user.save()
        return redirect('home')
    elif '_easy' in request.POST:
        easy_word = request.POST.get('word')
        word = Words.objects.get(name=easy_word)
        delete_word(current_user, word, bad_words.all(), good_words.all(),
                    new_words.all())
        add_in_old_word(word, current_user, 4)
        return redirect('home')
    words = []
    all_words = [bad_words.all(), good_words.all(), new_words.all()]
    for objects in all_words:  #цикл собирает все текущие для пользователя слова
        for word in objects:
            words.append(word)
    if len(words) == 0:  # если слов на сегодня нет, редирект на главную
        return redirect('/')

    shuffle(words)
    context = {
        'word': words[0],
        'user': current_user,
        'bad_words': bad_words.count(),
        'good_words': good_words.count(),
        'new_words': new_words.count()
    }

    return render(request, 'words/home.html', context)
