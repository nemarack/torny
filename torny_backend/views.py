from rest_framework.views import APIView
from .models import User, Tournament, UserInTournament, Profile, Pool
from rest_framework.response import Response
from django.core import serializers
from django.contrib.auth import authenticate
import json


def serialize_model(data):
    data = serializers.serialize("json", [data])
    struct = json.loads(data)
    return json.dumps(struct[0])


# from datetime import datetime
class CreateTournament(APIView):

    def post(self, request):
        """
        creates a tournament with the given information
        """
        tournament = Tournament(name=request.data['name'],
                                date=request.data['date'],
                                weapon=request.data['weapon'])
        tournament.save()

        data = serialize_model(tournament)

        return Response(data.id)


class RegisterUser(APIView):
    """
    creates a new user and corresponding profile
    """

    def post(self, request):
        user = User.objects.create_user(
                request.data['user'],
                request.data['email'],
                request.data['pass'],
                )

        profile = Profile(
            user=user,
            username=request.data['user'],
            usfa_id=request.data['usfa'],
            date_of_birth=request.data['dob'],
            foil_rating=request.data['rfoil'],
            saber_rating=request.data['rsaber'],
            epee_rating=request.data['repee'],
            foil_director_rating=request.data['dfoil'],
            saber_director_rating=request.data['dsaber'],
            epee_director_rating=request.data['depee'])

        profile.save()

        # TODO: Authenticate Data before storing

        return Response("{\"result\":\"success\"}")


class AuthenticateUser(APIView):

    def post(self, request):
        user = authenticate(
                username=request.data['user'],
                password=request.data['pass'])
        if user is None:
            return Response("Bad Username or Password")

        return Response("success")


class Tournaments(APIView):

    def get(self, request, id=None):
        """
        creates a tournament with the given information
        """
        if id:
            data = serialize_model(Tournament.objects.get(id=id))
        else:
            data = serializers.serialize("json", Tournament.objects.all())
        return Response(data)


class RegisterUserInTournament(APIView):

    def post(self, request):
        user_id = request.data['user_id'] or request.user.id
        profile = Profile.objects.get(user=user_id)

        registration = UserInTournament(

            tournament=request.data['tournament_id'],
            user=profile.id,
            role=request.data['role'],
            status=request.data['status']
        )

        return Response(serialize_model(registration))


class Seeding(APIView):

    def post(self, request):
        tournament = Tournament.objects.get(id=request.data['tournament_id'])
        if tournament.weapon == 'foil':
            rating = 'foil_rating'
            d_rating = 'foil_director_rating'
        elif tournament.weapon == 'saber':
            rating = 'saber_rating'
            d_rating = 'saber_director_rating'
        elif tournament.weapon == 'epee':
            rating = 'epee_rating'
            d_rating = 'epee_director_rating'

        fencers = tournament.users.objects.filter(role=1).order_by(rating)
        directors = tournament.users.objects.filter(role=2).order_by(d_rating)

        fencers_count = fencers.count()
        directors_count = directors.count()
        pool_size = fencers_count / directors_count
        top = 0
        for director in directors:
            fencers_in_pool = fencers[top:top + pool_size]
            top = top + pool_size
            pool = Pool(tournament=tournament.id, director=director.id,
                        fencers=fencers_in_pool)
            pool.save()

        return Response('Success')


class ListUsers(APIView):
    """
    View to list all users in the system.
    """

    def get(self, request, format=None):
        """
        Return a list of all users.
        """
        # usernames = [user.username for user in User.objects.all()]
        # return Response(usernames)
