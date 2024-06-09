import graphene
import graphql_jwt
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from graphene_django import DjangoObjectType
from graphene import Schema
from graphql_jwt.shortcuts import get_token

from blog import models

class UserType(DjangoObjectType):
    class Meta:
        model = User

class AuthorType(DjangoObjectType):
    class Meta:
        model = models.Profile

class PostType(DjangoObjectType):
    class Meta:
     model = models.Post

class TagType(DjangoObjectType):
    class Meta:
        model = models.Tag

    
class ObtainJSONWebToken(graphene.Mutation):
    token = graphene.String()
    user = graphene.Field(UserType)

    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)

    @classmethod
    def mutate(cls, root, info, username, password):
        user = authenticate(username=username, password=password)
        if user is None:
            raise Exception('Invalid username or password')

        if not user.is_active:
            raise Exception('User is inactive')

        token = get_token(user)
        return cls(token=token, user=user)

class CreateUser(graphene.Mutation):
    user = graphene.Field(UserType)

    class Arguments:
        username = graphene.String(required=True)
        password = graphene.String(required=True)
        email = graphene.String()

    def mutate(self, info, username, password, email=None):
        if not email:
            email = 'default@example.com'
        user = User.objects.create_user(username=username, password=password, email=email)
        return CreateUser(user=user)
    
class Query(graphene.ObjectType):
    me = graphene.Field(UserType)
    all_posts = graphene.List(PostType)
    post_by_id = graphene.Field(PostType, id=graphene.Int())
    author_by_username = graphene.Field(AuthorType, username= graphene.String())
    post_by_slug = graphene.Field(PostType, slug=graphene.String())
    posts_by_author= graphene.List(PostType, username=graphene.String())
    posts_by_tag= graphene.List(PostType,  tag=graphene.String(required=True))
    related_posts = graphene.List(PostType, meta_description=graphene.String())

    def resolve_me(self, info):
        user= info.context.user
        if not user.is_authenticated:
            raise Exception('Not logged in')
        return user

    def resolve_all_posts(root, info):
        return(
            models.Post.objects.prefetch_related("tags").select_related("author").all()
        )
    
    def resolve_author_by_username(root, info, username):
        return models.Profile.objects.select_related("user").get(user_name = username)
    
    def resolve_post_by_slug(self, info, slug):
        try:
            return models.Post.objects.get(slug=slug)
        except models.Post.DoesNotExist:
            return None
    
    def resolve_posts_by_author(root, info, username):
        return(models.Post.objects.prefetch_related("tags").select_related("author").filter(author_user_username= username))
    
    def resolve_posts_by_tag(self, info, tag):
        try:
            return models.Tag.objects.get(name=tag)
        except models.Tag.DoesNotExist:
            return None

    def resolve_post_by_id(self, info, id):
        try:
            return models.Post.objects.get(pk=id)
        except models.Post.DoesNotExist:
            return None

    def resolve_related_posts(self, info, meta_description):
        return models.Post.objects.filter(metaDescription_icontains=meta_description).exclude(metaDescription=meta_description)
    
class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    token_auth = ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    delete_token_cookie = graphql_jwt.DeleteJSONWebTokenCookie.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    delete_refresh_token_cookie = graphql_jwt.DeleteRefreshTokenCookie.Field()
   

schema = Schema(query=Query, mutation=Mutation)