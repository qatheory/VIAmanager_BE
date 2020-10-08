from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework import permissions
from rest_framework import generics
from apis.serializers import UserSerializer, UserFullSerializer
from apis.serializers import WorkspaceSerializer, WorkspaceFullSerializer
from apis.serializers import ViasSerializer
from apis.models import Workspace, Via


# User APIView
class UserList(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, format=None):
        users = User.objects.all()
        serializer = UserFullSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetail(generics.RetrieveAPIView):
    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        user = self.get_object(pk)
        serializer = UserFullSerializer(user)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        user = self.get_object(pk)
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        user = self.get_object(pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# VIA APIViews
class ViaList(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        vias = Via.objects.all()
        serializer = ViasSerializer(vias, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = ViasSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ViaDetail(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return Via.objects.get(pk=pk)
        except Via.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        via = self.get_object(pk)
        serializer = ViasSerializer(via)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        via = self.get_object(pk)
        serializer = ViasSerializer(via, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        via = self.get_object(pk)
        via.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Workspace APIview
class WorkspaceList(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        workspaces = Workspace.objects.all()
        serializer = WorkspaceFullSerializer(workspaces, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = WorkspaceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(createdBy=self.request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class WorkspaceDetail(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return Workspace.objects.get(pk=pk)
        except Workspace.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        workspace = self.get_object(pk)
        serializer = WorkspaceFullSerializer(workspace)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        workspace = self.get_object(pk)
        serializer = WorkspaceSerializer(workspace, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        workspace = self.get_object(pk)
        workspace.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
