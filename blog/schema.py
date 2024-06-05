import graphene
from django.contrib.auth import get_user_model
from graphene_django import DjangoObjectType
from graphene import Schema

from blog import models

class UserType(DjangoObjectType):
    class Meta:
        model = get_user_model()

class AuthorType(DjangoObjectType):
    class Meta:
        model = models.Profile

class PostType(DjangoObjectType):
    class Meta:
     model = models.Post

class TagType(DjangoObjectType):
    class Meta:
        model = models.Tag

class Query(graphene.ObjectType):
    all_posts = graphene.List(PostType)
    post_by_id = graphene.Field(PostType, id=graphene.Int())
    author_by_username = graphene.Field(AuthorType, username= graphene.String())
    post_by_slug = graphene.Field(PostType, slug=graphene.String())
    posts_by_author= graphene.List(PostType, username=graphene.String())
    posts_by_tag= graphene.List(PostType, tag= graphene.String())
    related_posts = graphene.List(PostType, meta_description=graphene.String())

    def resolve_all_posts(root, info):
        return(
            models.Post.objects.prefetch_related("tags").select_related("author").all()
        )
    
    def resolve_author_by_username(root, info, username):
        return models.Profile.objects.select_related("user").get(user_name = username)
    
    def resolve_post_by_slug(root, info, slug):
        return(
            models.Post.objects.prefetch_related("tags").select_related("author").get(slug=slug)
        )
    
    def resolve_posts_by_author(root, info, username):
        return(models.Post.objects.prefetch_related("tags").select_related("author").filter(author_user_username= username))
    
    def resolve_posts_by_tag(root, info, tag):
        return(models.Post.objects.prefetch_related("tags").select_related("author").filter(tag_name_iexact=tag))
    
    def resolve_post_by_id(self, info, id):
        try:
            return models.Post.objects.get(pk=id)
        except models.Post.DoesNotExist:
            return None

    def resolve_related_posts(self, info, meta_description):
        return models.Post.objects.filter(metaDescription_icontains=meta_description).exclude(metaDescription=meta_description)

schema = Schema(query=Query)