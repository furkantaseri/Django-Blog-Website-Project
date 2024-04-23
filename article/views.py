from django.shortcuts import render, HttpResponse, redirect, get_object_or_404, reverse
from django.contrib.auth.decorators import login_required
from .forms import ArticleForm
from .models import Article, Comment
from django.contrib import messages
from django.db.models import Count

# Create your views here.


def articles(request):

    keyword = request.GET.get("keyword")

    if keyword:
        articles = Article.objects.filter(title__contains=keyword)
        return render(request, "articles.html", {"articles": articles})

    articles = Article.objects.all()

    return render(request, "articles.html", {"articles": articles})


def index(request):
    most_commented_articles = Comment.objects.values('article_id').annotate(
        comment_count=Count('id')).order_by('-comment_count')[:10]
    most_commented_article_ids = [
        str(article_id_list['article_id']) for article_id_list in most_commented_articles]
    articles = []
    for i in most_commented_article_ids:
        articles += Article.objects.filter(id=i)

    latest_articles = Article.objects.order_by('-created_date')[:10]

    context = {"articles": articles, "most_commented_articles":
               most_commented_articles, "latest_articles": latest_articles}

    return render(request, "index.html", context)


def about(request):
    return render(request, "about.html")


@login_required(login_url="user:login")
def dashboard(request):

    articles = Article.objects.filter(author=request.user)

    context = {
        "articles": articles
    }

    return render(request, "dashboard.html", context)


@login_required(login_url="user:login")
def addArticle(request):

    form = ArticleForm(request.POST or None, request.FILES or None)

    if form.is_valid():

        article = form.save(commit=False)
        article.author = request.user
        article.save()

        messages.success(request, "Makale Başarıyla Oluşturuldu")
        return redirect("article:dashboard")

    return render(request, "addarticle.html", {"form": form})


def detail(request, id):

    article = get_object_or_404(Article, id=id)

    comments = article.comments.all()

    return render(request, "detail.html", {"article": article, "comments": comments})


@login_required(login_url="user:login")
def updateArticle(request, id):
    article = get_object_or_404(Article, id=id)
    form = ArticleForm(request.POST or None,
                       request.FILES or None, instance=article)

    if form.is_valid():

        article = form.save(commit=False)
        article.author = request.user
        article.save()

        messages.success(request, "Makale Başarıyla Güncellendi")
        return redirect("article:dashboard")

    return render(request, "update.html", {"form": form})


@login_required(login_url="user:login")
def deleteArticle(request, id):

    article = get_object_or_404(Article, id=id)

    article.delete()

    messages.success(request, "Makale Başarıyla Silindi")
    return redirect("article:dashboard")


def addComment(request, id):
    article = get_object_or_404(Article, id=id)

    if request.method == "POST":
        comment_author = request.user
        comment_content = request.POST.get("comment_content")

        newComment = Comment(comment_author=comment_author,
                             comment_content=comment_content)

        newComment.article = article

        newComment.save()

        return redirect(reverse("article:detail", kwargs={"id": id}))

    pass
