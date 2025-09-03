import pytest

from django.contrib.auth.models import User
from django.urls import reverse
from products.models import Customer

@pytest.mark.django_db
def test_get_all_users(api_client):
    user_1 = User.objects.create(
        username="user1", 
        email="u1@tests.com"
    )
    user_2 = User.objects.create(
        username="user2", 
        email="u2@tests.com", 
        is_active=False
    )
    url = reverse('users-list')
    response = api_client.get(url)
    result = response.json()

    assert response.status_code == 200
    assert result == [
        {
            "email": user_1.email,
            "pk": user_1.pk,
            "first_name": '',
            "username":user_1.username,
            "last_name": '',
            "is_active": True            
        },
        {
            "email": user_2.email,
            "pk": user_2.pk,
            "first_name": '',
            "username":user_2.username,
            "last_name": '',
            "is_active": False            
        }
    ]


@pytest.mark.django_db
def test_get_all_users_empty_users(api_client):
    url = reverse('users-list')
    response = api_client.get(url)
    body = response.json()

    assert response.status_code == 200
    assert body == []


@pytest.mark.django_db
def test_get_all_users_with_11_user(api_client):
    for x in range(11):
        User.objects.create(
            username=f"user{x}", 
            email=f"u{x}@tests.com"
        )
    url = reverse('users-list')
    response = api_client.get(url)
    body = response.json()

    assert response.status_code == 200
    assert len(body) == 11

@pytest.mark.django_db
def test_user_create(api_client):
    payload = {
        "username": "test_user",
        "email": "test@gmail.com",
        "first_name": "test name",
        "last_name": "test lastname",
        "is_active": True,
        "password": "fake123"
    }

    url = reverse('users-list')
    response = api_client.post(path=url, data=payload, format='json')
    body = response.json()

    users = User.objects.all()
    user = users.first()   # usamos siempre la instancia

    # asserts básicos
    assert response.status_code == 201
    assert "password" not in body
    assert body['username'] == 'test_user'
    assert body['email'] == 'test@gmail.com'
    assert body['first_name'] == 'test name'
    assert body['last_name'] == 'test lastname'
    assert body['is_active'] is True
    assert users.count() == 1
    assert user.email == 'test@gmail.com'

    # # assert de Customer (si tu lógica lo crea)
    # assert Customer.objects.all().count() == 1
    # assert Customer.objects.filter(name=user.username).exists()

    # # validar la contraseña
    # assert user.check_password('fake123')

@pytest.mark.django_db
def test_user_retrieve(api_client):
    user_1 = User.objects.create(
        username="user1", 
        email="u1@tests.com"
    )
    user_2 = User.objects.create(
        username="user2", 
        email="u2@tests.com",
        is_active= False
    )

    url = reverse('users-detail', args=[user_2.pk])
    response = api_client.get(url)

    status =response.status_code
    data = response.json()

    assert status == 200
    assert data['username'] == user_2.username
    assert data['email'] == user_2.email

@pytest.mark.django_db
def test_user_retrieve_not_found(api_client):
    user_1 = User.objects.create(
        username="user1", 
        email="u1@tests.com"
    )
    user_2 = User.objects.create(
        username="user2", 
        email="u2@tests.com",
        is_active= False
    )

    url = reverse('users-detail', args=["3"])
    response = api_client.get(url)

    status =response.status_code
    data = response.json()

    assert status == 404
    assert data['detail'] == 'No User matches the given query.'

@pytest.mark.django_db
def test_update_put_user(api_client):
    user = User.objects.create(
        username="user1", 
        email="u1@tests.com",
        first_name="nombre viejo",
        last_name="apellido viejo",
    )

    payload = {
        "username" : "user1", 
        "email":"u1@tests.com",
        "first_name" : "nombre nuevo",
        "last_name" : "apellido nuevo",
    }

    url = reverse("users-detail", args=[user.pk])
    response = api_client.put(url, payload, format='json')

    assert response.status_code == 200
    user.refresh_from_db()
    assert user.first_name == 'nombre nuevo'


# @pytest.mark.django_db
# def test_update_patch_user(api_client):
#     user_1 = User.objects.create(
#         username="user1", 
#         email="u1@tests.com",
#         first_name="nombre viejo",
#         last_name="nombre viejo",
#     )


@pytest.mark.django_db
def test_update_delete_user(api_client):
    user = User.objects.create(
        username="user1", 
        email="u1@tests.com",
        first_name="nombre viejo",
        last_name="nombre viejo",
        is_active= True
    )

    url = reverse("users-detail", args=[user.pk])
    response = api_client.delete(url)

    assert response.status_code == 200  
    user.refresh_from_db()
    assert user.is_active is False
    assert response.json()['detail'] == f"User {user.username} deactivated"

    url = reverse("users-detail", args=[user.pk])