from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import default_token_generator
from rest_framework import serializers, exceptions
from rest_framework_simplejwt.tokens import AccessToken


from reviews.models import User, Category, Comment, Genre, Review, Title

USERNAME_REGEX = r'^(?!me\Z)^[\w.@+-]+\Z'
USERNAME_FIELD = serializers.RegexField(USERNAME_REGEX, max_length=150)


class SignUpSerializer(serializers.ModelSerializer):
    username = USERNAME_FIELD
    email = serializers.EmailField(max_length=254)

    class Meta:
        model = User
        fields = ('email', 'username')

    def validate(self, data):
        if not User.objects.filter(username=data.get('username'),
                                   email=data.get('email')).exists():

            if User.objects.filter(username=data.get('username')).exists():
                raise exceptions.ValidationError(
                    'Пользователь с таким именем уже зарегистрирован')
            elif User.objects.filter(email=data.get('email')).exists():
                raise exceptions.ValidationError(
                    'Данный email уже используется')

        return data


class TokenSerializer(serializers.ModelSerializer):
    username = USERNAME_FIELD
    confirmation_code = serializers.CharField(max_length=150)

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')

    def validate(self, data):
        """Получение jwt токена"""
        user = get_object_or_404(User, username=data['username'])
        if default_token_generator.check_token(user,
                                               data['confirmation_code']):
            token = AccessToken.for_user(user)
            return {'token': str(token)}

        raise exceptions.ParseError("Введен не верный код")


class UsersSerializer(serializers.ModelSerializer):
    username = USERNAME_FIELD

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name',
                  'bio', 'role')

    def validate(self, data):
        """Проверка данных на уникальность"""
        if User.objects.filter(username=data.get('username')).exists():
            raise exceptions.ValidationError(
                'Пользователь с таким именем уже зарегистрирован')
        elif User.objects.filter(email=data.get('email')).exists():
            raise exceptions.ValidationError('Данный email уже используется')

        return data


class UserIsMeSerializer(serializers.ModelSerializer):
    username = USERNAME_FIELD

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name',
                  'bio', 'role')
        read_only_fields = ('role',)


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для модели Category."""

    class Meta:
        model = Category
        exclude = ('id',)


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Genre."""

    class Meta:
        model = Genre
        exclude = ('id',)


class TitleGETSerializer(serializers.ModelSerializer):
    """Сериализатор объектов класса Title при GET запросах."""

    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'rating',
            'description',
            'genre',
            'category'
        )


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор объектов класса Title при небезопасных запросах."""

    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Review."""

    author = serializers.StringRelatedField(
        read_only=True
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate(self, data):
        """Запрещает пользователям оставлять повторные отзывы."""
        if not self.context.get('request').method == 'POST':
            return data
        author = self.context.get('request').user
        title_id = self.context.get('view').kwargs.get('title_id')
        if Review.objects.filter(author=author, title=title_id).exists():
            raise serializers.ValidationError(
                'Ошибка! Отзыв на это произведение уже написан.'
            )
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор объектов класса Comment."""

    author = serializers.StringRelatedField(
        read_only=True
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
