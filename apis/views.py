from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework import permissions, authentication
from rest_framework import generics
from apis.serializers import UserSerializer, UserFullSerializer, UserUpdate, UserResetPasswordSerializer
from apis.serializers import ViasSerializer, BmsSerializer
from apis.models import Via, Bm
from rest_framework.decorators import api_view, permission_classes
import asyncio
import multiprocessing as mp
from django.db.models import Q
import requests
from datetime import date, datetime


class isAdminOrReadOnly(permissions.BasePermission):
    ADMIN_ONLY_AUTH_CLASSES = [
        authentication.BasicAuthentication,
        authentication.SessionAuthentication
    ]

    def has_permission(self, request, view):
        user = request.user
        print(user.is_superuser)

        if request.method in permissions.SAFE_METHODS:
            return True

        if user and user.is_authenticated:
            if user.is_superuser:
                return user.is_superuser or \
                    not any(isinstance(request._authenticator, x)
                            for x in self.ADMIN_ONLY_AUTH_CLASSES)
            else:
                return False
        return False


# User APIView


class UserList(APIView):
    permission_classes = [isAdminOrReadOnly]

    def get(self, request, format=None):
        username = request.GET.get("username", None)
        users = User.objects.all()
        if (username):

            users = users.filter(username__contains=username)
            print(users)
        serializer = UserFullSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        user = request.data
        if not user:
            return Response({"response": "error", "message": "No data found"})
        serializer = UserSerializer(data=user)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetail(APIView):
    permission_classes = [isAdminOrReadOnly]

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


class UserResetPassword(APIView):
    permission_classes = [isAdminOrReadOnly]

    def get_object(self, pk):
        try:
            return User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise Http404

    def put(self, request, pk, format=None):
        user = self.get_object(pk)
        serializer = UserResetPasswordSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateUserView(APIView):
    permission_classes = (permissions.AllowAny, )

    def post(self, request):
        user = request.data.get("user")
        if not user:
            return Response({"response": "error", "message": "No data found"})
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


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def get_current_user(request):
    serializer = UserFullSerializer(request.user)
    return Response(serializer.data)


# @api_view(["GET"])
# @permission_classes([permissions.IsAuthenticated])
# def get_bm(request):
#     userID = serializer.data["appID"]
#     access_token = serializer.data["accessToken"]
#     resp = requests.get(
#         url=f"https://graph.facebook.com/v8.0/{userID}/businesses", params={
#             "access_token": access_token
#         })
#     listBMid = resp.json()["data"]
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


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def get_ads_acc(request):
    vias = Via.objects.all()
    viasz = ViasSerializer(vias, many=True)
    listVias = viasz.data
    print(viasz.data)
    mergedListAdsAcc = []
    for via, index in viasz.data.items():
        print(via)
        # adsAccIds = requests.get(
        #     url=f"https://graph.facebook.com/v8.0/{via.fbid}", params={
        #         "access_token": via.accessToken,
        #         "fields": "adaccounts"
        #     })
        # mergedListAdsAcc.append(mergedListAdsAcc.json()["data"])
    print(mergedListAdsAcc)
    # mergedListAdsAccountsID = resp.json()["data"]
    # mergedListAdsAccountsInfo = []
    # for adsAccount in mergedListAdsAccountsID:
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
    #     mergedListAdsAccountsInfo.append(adsAccountInfo)
    return Response({
        "success": "true",
        # "data": mergedListAdsAccountsInfo
    })


# VIA APIViews


class AdsAccList(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def filterAdsAccByStatus(self, statusFilter, adsAcc):
        if (statusFilter != "0"):
            if (statusFilter == "1"):
                return (adsAcc["account_status"] == 1
                        or adsAcc["account_status"] == 201)
            elif (statusFilter == "2"):
                return (adsAcc["account_status"] == 2
                        or adsAcc["account_status"] == 101
                        or adsAcc["account_status"] == 102
                        or adsAcc["account_status"] == 202)
            elif (statusFilter == "3"):
                return (adsAcc["account_status"] == 3
                        or adsAcc["account_status"] == 7
                        or adsAcc["account_status"] == 8
                        or adsAcc["account_status"] == 9)
        else:
            return True

    def get(self, request, format=None):
        viaFilter = request.GET.get("via", None)
        statusFilter = request.GET.get("status", None)
        vias = Via.objects.filter(isDeleted=False)
        response = {
            "error": {"viaError": []}
        }
        if (viaFilter):
            vias = vias.filter(id=viaFilter)

        viasz = ViasSerializer(vias, many=True)
        listVias = viasz.data
        mergedListAdsAcc = []
        for via in viasz.data:
            adsAccFromID = requests.get(
                url="https://graph.facebook.com/v8.0/{}".format(via["fbid"]),
                params={
                    "access_token":
                    via["accessToken"],
                    "fields":
                    "name,adaccounts{name,account_status,amount_spent,balance,business,disable_reason,is_prepay_account,spend_cap}"
                })
            if("error" in adsAccFromID.json()):
                response["error"]["viaError"].append(via["name"])
            else:
                ownerId = adsAccFromID.json()["id"]
                ownerName = adsAccFromID.json()["name"]
                ListAdsAcc = filter(
                    lambda x: (self.filterAdsAccByStatus(statusFilter, x)),
                    adsAccFromID.json()["adaccounts"]["data"])
                for adsAcc in ListAdsAcc:

                    for account in mergedListAdsAcc:
                        if account["id"] == adsAcc["id"]:
                            account["owner"] += [{
                                "id": ownerId,
                                "name": ownerName,
                                "via": via["name"],
                                "viaId": via["id"]
                            }]
                            break
                    else:
                        adsAcc["owner"] = [{
                            "id": ownerId,
                            "name": ownerName,
                            "via": via["name"],
                            "viaId": via["id"]
                        }]
                        mergedListAdsAcc.append(adsAcc)
        response["data"] = mergedListAdsAcc
        return Response(response)

    def post(self, request, format=None):
        serializer = ViasSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ViaList(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, format=None):
        viaId = request.GET.get("id", None)
        name = request.GET.get("name", None)
        email = request.GET.get("email", None)
        fbName = request.GET.get("fbName", None)
        fbid = request.GET.get("fbid", None)
        label = request.GET.get("label", None)
        status = request.GET.get("status", None)
        vias = Via.objects.filter(isDeleted=False)
        if (viaId):
            vias = vias.filter(id__in=",".join(viaId))
        if (name):
            vias = vias.filter(name__contains=name)
        if (fbName):
            vias = vias.filter(fbName__contains=fbName)
        if (email):
            vias = vias.filter(email__contains=email)
        if (fbid):
            vias = vias.filter(fbid=fbid)
        if (label):
            vias = vias.filter(label=label)
        if (status):
            vias = vias.filter(status=status)

        serializer = ViasSerializer(vias, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        vias = Via.objects.filter(isDeleted=False, fbid=request.data["fbid"])
        viasz = ViasSerializer(vias, many=True)
        print(viasz.data)
        if len(viasz.data) == 0:
            serializer = ViasSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"status": "created"})
        serializer = ViasSerializer(vias[0], data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "updated"})
        return Response({"status": "error"})


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


class CheckVia(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return Via.objects.get(pk=pk)
        except Via.DoesNotExist:
            return "error"

    def get(self, request, pk, format=None):
        viaModel = self.get_object(pk)
        if viaModel == "error":
            return Response({"success": False,
                             "messages": "Via Không tồn tại"})
        viasz = ViasSerializer(viaModel)

        via = viasz.data
        BmsFromID = requests.get(
            url="https://graph.facebook.com/v8.0/{}".format(via["fbid"]),
            params={
                "access_token":
                    via["accessToken"],
                    "fields": "businesses{id,name,pending_users{created_time}}"
            })

        #
        listBusiness = BmsFromID.json()["businesses"]["data"]
        if len(listBusiness) == 0:
            return Response({"success": False,
                             "messages": "Via không hoạt động, user chưa được kết nối với BM"})
        listPendingUsers = []
        if("pending_users" in listBusiness[0]):
            listPendingUsers = listBusiness[0]["pending_users"]["data"]

        if len(listPendingUsers) == 0:
            today = date.today()
            formattedDate = today.strftime("%d_%m_%Y")
            checkingResult = requests.post(
                url="https://graph.facebook.com/v8.0/{}/business_users".format(
                    listBusiness[0]["id"]),
                data={
                    "access_token":
                    via["accessToken"],
                    "role": "ADMIN",
                    "email": "{}@backup.data".format(formattedDate)})
            if "error" in checkingResult.json():
                return Response({"success": False,
                                 "messages": "Đã có lỗi xảy ra hãy thử kiểm tra lại access token của Via"})
            serializer = ViasSerializer(viaModel, data={'status': 1})
            if serializer.is_valid():
                serializer.save()
                return Response({"success": True,
                                 "status": True,
                                 "messages": "Via {} hiện đang hoạt động".format(via["name"])
                                 })
            return Response({"success": True,
                             "status": True,
                             "messages": "Via {} hiện đang hoạt động. Tuy nhiên có lỗi khi kết nối với Database".format(via["name"])
                             })

        else:
            createdDate = datetime.strptime(
                listPendingUsers[0]["created_time"], "%Y-%m-%dT%H:%M:%S%z")
            formattedDate = createdDate.strftime("%d_%m_%Y")
            selectedPendingUser = listPendingUsers[0]
            checkingResult = requests.post(
                url="https://graph.facebook.com/v8.0/{}".format(
                    selectedPendingUser["id"]),
                data={
                    "access_token":
                    via["accessToken"],
                    "role": "ADMIN",
                    "email": "{}@backup.data".format(formattedDate)
                })
            if "error" in checkingResult.json():
                if checkingResult.json()["error"]["code"] == 368:
                    serializer = ViasSerializer(viaModel, data={'status': 0})
                    print(serializer.is_valid())
                    if serializer.is_valid():
                        serializer.save()
                        return Response({"success": True,
                                         "status": False,
                                         "messages": "Via {} hiện đã bị hạn chế".format(via["name"])
                                         })
                    return Response({"success": True,
                                     "status": False,
                                     "messages": "Via {} hiện đã bị hạn chế. Tuy nhiên có lỗi khi kết nối với Database".format(via["name"])
                                     })
                return Response({"success": False,
                                 "messages": "Đã có lỗi xảy ra trong quá trình kết nối với Facebook"})
            serializer = ViasSerializer(viaModel, data={"status": 1})
            if serializer.is_valid():
                serializer.save()
                return Response({"success": True,
                                 "status": True,
                                 "messages": "Via {} hiện đang hoạt động".format(via["name"])
                                 })
            return Response({"success": True,
                             "status": True,
                             "messages": "Via {} hiện đang hoạt động. Tuy nhiên có lỗi khi kết nối với Database".format(via["name"])
                             })
        return Response({"success": False,
                         "messages": "Lỗi không xác định"})


class BmList(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def filterBmByStatus(self, statusFilter, bm):
        if (statusFilter != "0" and statusFilter != None):
            if (statusFilter == "1"):
                return (bm["verification_status"] != "not_verified")
            elif (statusFilter == "2"):
                return (bm["verification_status"] == "not_verified")
        else:
            return True

    def extractBackupEmail(self, bm):

        if("pending_users" in bm):
            if (len(bm["pending_users"]["data"]) != 0):
                bm["backup_email"] = bm["pending_users"]["data"][0]["email"]
                bm["backup_link"] = bm["pending_users"]["data"][0]["invite_link"]
                bm["expiration_date"] = bm["pending_users"]["data"][0]["expiration_time"]
                bm.pop('pending_users', None)
                return bm
        bm["backup_email"] = ""
        bm["backup_link"] = ""
        bm["expiration_date"] = ""
        bm.pop('pending_users', None)
        return bm

    def get(self, request, format=None):
        viaFilter = request.GET.get("via", None)
        statusFilter = request.GET.get("status", None)
        vias = Via.objects.filter(isDeleted=False)
        response = {
            "error": {"viaError": []}
        }
        if (viaFilter):
            vias = vias.filter(id=viaFilter)

        viasz = ViasSerializer(vias, many=True)
        listBm = []
        listVias = viasz.data
        for via in viasz.data:
            bmsFromUser = requests.get(
                url="https://graph.facebook.com/v8.0/{}".format(
                    via["fbid"]),
                params={
                    "fields": "businesses{id,link,name,verification_status,pending_users{id,email,created_time,expiration_time,invite_link}}",
                    "access_token": via["accessToken"],
                })
            print(via["id"])
            if("error" in bmsFromUser.json()):
                response["error"]["viaError"].append(via["name"])
            else:
                ownerId = via["id"]
                ownerName = via["name"]
                # bmInfo = bmsFromUser.json()["businesses"]["data"]
                bmInfo = filter(
                    lambda x: (self.filterBmByStatus(statusFilter, x)), bmsFromUser.json()["businesses"]["data"])
                for business in bmInfo:
                    for bm in listBm:
                        if bm["id"] == business["id"]:
                            bm["owner"] += [{"id": ownerId, "name": ownerName}]
                            break
                    else:
                        business["owner"] = [
                            {"id": ownerId, "name": ownerName}]
                        listBm.append(business)
        listBm = map(lambda x: (self.extractBackupEmail(x)), listBm)
        response["data"] = listBm
        return Response(response)

    # def post(self, request, format=None):
    #     serializer = BmsSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BmBackup(APIView):
    permission_classes = [permissions.IsAuthenticated]
    isSuccessfulClearBackup = True

    async def clearOldBackupLink(self, backupId, token):
        deleteBackupResponse = requests.delete(
            url="https://graph.facebook.com/v8.0/{}".format(backupId),
            params={
                "access_token": token
            })
        deleteBackupResult = deleteBackupResponse.json()
        if(deleteBackupResult["success"] == False):
            isSuccessfulClearBackup = False

    def post(self, request, format=None):
        owners = request.data["owners"]
        bmid = request.data["bmid"]
        # print("{} {}".format(owners, bmid))
        if(not owners):
            return Response({"success": False, "status": "error", "messages": "Chưa cung cấp via"})
        if len(owners) == 0:
            return Response({"success": False, "status": "error", "messages": "Chưa cung cấp via"})
        if(not bmid):
            return Response({"success": False, "status": "error", "messages": "Chưa cung cấp bm"})
        listViasId = []
        for owner in owners:
            listViasId.append(owner["id"])
        vias = Via.objects.filter(id__in=listViasId)
        vias = vias.filter(status=1)
        viasz = ViasSerializer(vias, many=True)
        if len(viasz.data) == 0:
            return Response({"success": False, "messages": "BM Không được sở hữu bởi Via còn hoạt động"})
        # print(viasz.data[0]["id"])
        via = viasz.data[0]
        listPendingUsersResponse = requests.get(
            url="https://graph.facebook.com/v8.0/{}/pending_users".format(
                bmid),
            params={
                "access_token": via["accessToken"]
            })
        listPendingUsers = listPendingUsersResponse.json()["data"]
        isSuccessfulClearBackup = True
        for pendingUsers in listPendingUsers:
            deleteBackupResponse = requests.delete(
                url="https://graph.facebook.com/v8.0/{}".format(
                    pendingUsers["id"]),
                params={
                    "access_token": via["accessToken"]
                })
            deleteBackupResult = deleteBackupResponse.json()
            if(deleteBackupResult["success"] == False):
                isSuccessfulClearBackup = False
        print(isSuccessfulClearBackup)
        today = date.today()
        formattedDate = today.strftime("%d_%m_%Y")
        createBackupResponse = requests.post(
            url="https://graph.facebook.com/v8.0/{}/business_users".format(
                bmid),
            data={
                "access_token":
                    via["accessToken"],
                    "email": "{}@backup.data".format(formattedDate),
                    "role": "ADMIN"
            })
        createBackupResult = createBackupResponse.json()
        if("error" in createBackupResult):
            print(createBackupResult)
            return Response({"success": False, "status": "error", "messages": "Đã có lỗi xảy ra, hãy kiểm tra lại access token"})
        if isSuccessfulClearBackup == False:
            return Response({"success": True, "status": "warning", "messages": "Cấn kiểm tra lại BM, việc dọn sạch link backup cũ xảy ra lỗi"})
        BackupInfoResponse = requests.get(
            url="https://graph.facebook.com/v8.0/{}".format(
                createBackupResult["id"]),
            params={
                "access_token":
                    via["accessToken"],
                    "fields": "invite_link,expiration_time,email,id",
            })
        BackupInfo = BackupInfoResponse.json()
        data = {"backup_email": BackupInfo["email"],
                "backup_link": BackupInfo["invite_link"],
                "expiration_date": BackupInfo["expiration_time"]}
        return Response({"success": True, "status": "success", "messages": "Làm mới link backup thành công", "data": data})


class BmDetail(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return Bm.objects.get(pk=pk)
        except Bm.DoesNotExist:
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


class BmAdsAcc(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return Via.objects.get(pk=pk)
        except Via.DoesNotExist:
            raise Http404

    def get(self, request, format=None):
        selectedVia = request.GET.get("via", None)
        selectedBm = request.GET.get("bm", None)
        via = self.get_object(selectedVia)
        serializer = ViasSerializer(via)
        viaInfo = serializer.data
        bmInfo = requests.get(
            url="https://graph.facebook.com/v8.0/{}/owned_ad_accounts/".format(
                selectedBm),
            params={
                "fields": "name,account_status,disable_reason",
                "access_token": viaInfo["accessToken"]
            })
        return Response(bmInfo.json()["data"])


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
