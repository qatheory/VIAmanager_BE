from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework import permissions, authentication
from rest_framework import generics
from apis.serializers import UserSerializer, UserFullSerializer, UserUpdate
from apis.serializers import ViasSerializer, BMsSerializer
from apis.models import Via, BM
from rest_framework.decorators import api_view, permission_classes
import requests

# User APIView


class UserList(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, format=None):
        users = User.objects.all()
        serializer = UserFullSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        user = request.data
        if not user:
            return Response({'response': 'error', 'message': 'No data found'})
        serializer = UserSerializer(data=user)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetail(APIView):
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
        serializer = UserUpdate(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        user = self.get_object(pk)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CreateUserView(APIView):
    permission_classes = (permissions.AllowAny, )

    def post(self, request):
        user = request.data.get('user')
        if not user:
            return Response({'response': 'error', 'message': 'No data found'})
        serializer = UserSerializerWithToken(data=user)
        if serializer.is_valid():
            saved_user = serializer.save()
        else:
            return Response({
                "response": "error",
                "message": serializer.errors
            })
        return Response({
            "response": "success",
            "message": "user created succesfully"
        })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_current_user(request):
    serializer = UserFullSerializer(request.user)
    return Response(serializer.data)


# @api_view(['GET'])
# @permission_classes([permissions.IsAuthenticated])
# def get_bm(request):
#     userID = serializer.data["appID"]
#     access_token = serializer.data["accessToken"]
#     resp = requests.get(
#         url=f"https://graph.facebook.com/v8.0/{userID}/businesses", params={
#             "access_token": access_token
#         })
#     listBMid = resp.json()['data']
#     listBMinfo = []
#     for bm in listBMid:
#         bmid = bm["id"]
#         rawBMinfo = requests.get(
#             url=f"https://graph.facebook.com/v8.0/{bmid}", params={
#                 "fields": "id,name,link,verification_status,payment_account_id",
#                 "access_token": access_token
#             })
#         BMinfo = rawBMinfo.json()
#         print(BMinfo)
#         listBMinfo.append(BMinfo)
#         return Response(listBMinfo)

# def get_workspace_from_id(workspaceID):
#     try:
#         return Workspace.objects.get(pk=workspaceID)
#     except Workspace.DoesNotExist:
#         raise Http404


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_ads_acc(request):
    vias = Via.objects.all()
    viasz = ViasSerializer(vias, many=True)
    listVias = viasz.data
    print(viasz.data)
    listAdsAcc = []
    for via, index in viasz.data.items():
        print(via)
        # adsAccIds = requests.get(
        #     url=f"https://graph.facebook.com/v8.0/{via.fbid}", params={
        #         "access_token": via.accessToken,
        #         "fields": "adaccounts"
        #     })
        # listAdsAcc.append(listAdsAcc.json()['data'])
    print(listAdsAcc)
    # listAdsAccountsID = resp.json()['data']
    # listAdsAccountsInfo = []
    # for adsAccount in listAdsAccountsID:
    #     adsAccountID = adsAccount["id"]
    #     rawAdsAccountInfo = requests.get(
    #         url=f"https://graph.facebook.com/v8.0/{adsAccountID}/", params={
    #             "fields": "name,account_status,amount_spent,balance,disable_reason",
    #             "access_token": access_token
    #         })
    #     adsAccountInfo = rawAdsAccountInfo.json()
    #     adsAccountInfo["viaID"] = viaID
    #     adsAccountInfo["via"] = viaName
    #     print(adsAccountInfo)
    #     listAdsAccountsInfo.append(adsAccountInfo)
    return Response({
        "success": "true",
        # "data": listAdsAccountsInfo
    })


# VIA APIViews


class AdsAccList(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        vias = Via.objects.filter(isDeleted=False)
        viasz = ViasSerializer(vias, many=True)
        listVias = viasz.data
        listAdsAcc = []
        for via in viasz.data:
            adsAccFromID = requests.get(
                url="https://graph.facebook.com/v8.0/{}".format(via["fbid"]), params={
                    "access_token": via["accessToken"],
                    "fields": "name,adaccounts{name,account_status,amount_spent,balance,business,disable_reason,is_prepay_account,spend_cap}"
                })
            ownerId = adsAccFromID.json()["id"]
            ownerName = adsAccFromID.json()["name"]
            for adsAcc in adsAccFromID.json()["adaccounts"]["data"]:
                for account in listAdsAcc:
                    if account['id'] == adsAcc["id"]:
                        account["owner"] += [{"id": ownerId,
                                              "name": ownerName, "via": via["name"]}]
                        break
                else:
                    adsAcc["owner"] = [{"id": ownerId,
                                        "name": ownerName, "via": via["name"]}]
                    listAdsAcc.append(adsAcc)

        print(listAdsAcc)
        return Response(listAdsAcc)

    def post(self, request, format=None):
        serializer = ViasSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ViaList(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        name = request.GET.get('name', None)
        email = request.GET.get('email', None)
        fbName = request.GET.get('fbName', None)
        fbid = request.GET.get('fbid', None)
        label = request.GET.get('label', None)
        status = request.GET.get('status', None)
        vias = Via.objects.filter(isDeleted=False)

        if(name):
            vias = vias.filter(name__contains=name)
        if(fbName):
            vias = vias.filter(fbName__contains=fbName)
        if(email):
            vias = vias.filter(email__contains=email)
        if(fbid):
            vias = vias.filter(fbid=fbid)
        if(label):
            vias = vias.filter(label=label)
        if(status):
            vias = vias.filter(status=status)

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

    # def delete(self, request, pk, format=None):
    #     via = self.get_object(pk)
    #     via.delete()
    #     return Response(status=status.HTTP_204_NO_CONTENT)


class BMList(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        bms = BM.objects.all()
        serializer = BMsSerializer(bms, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        serializer = BMsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BMDetail(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return BM.objects.get(pk=pk)
        except BM.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        bm = self.get_object(pk)
        serializer = ViasSerializer(bm)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        bm = self.get_object(pk)
        serializer = ViasSerializer(bm, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        bm = self.get_object(pk)
        bm.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Workspace APIview
# class WorkspaceList(APIView):

#     permission_classes = [permissions.IsAuthenticated]

#     def get(self, request, format=None):
#         workspaces = Workspace.objects.all()
#         serializer = WorkspaceFullSerializer(workspaces, many=True)
#         return Response(serializer.data)

#     def post(self, request, format=None):
#         serializer = WorkspaceSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save(createdBy=self.request.user)
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class WorkspaceDetail(APIView):
#     permission_classes = [permissions.IsAuthenticated]

#     def get_object(self, pk):
#         try:
#             return Workspace.objects.get(pk=pk)
#         except Workspace.DoesNotExist:
#             raise Http404

#     def get(self, request, pk, format=None):
#         workspace = self.get_object(pk)
#         serializer = WorkspaceFullSerializer(workspace)
#         return Response(serializer.data)

#     def put(self, request, pk, format=None):
#         workspace = self.get_object(pk)
#         serializer = WorkspaceSerializer(workspace, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def delete(self, request, pk, format=None):
#         workspace = self.get_object(pk)
#         workspace.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
