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
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_current_user(request):
    serializer = UserFullSerializer(request.user)
    return Response(serializer.data)


class UserList(APIView):
    permission_classes = [isAdminOrReadOnly]

    def get(self, request, format=None):
        username = request.GET.get("username", None)
        users = User.objects.all()
        if (username):

            users = users.filter(username__contains=username)
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
            vias = vias.filter(id__in=viaId.split(","))
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
        if len(viasz.data) == 0:
            serializer = ViasSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response({"status": "created"})
        else:
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

        if "error" in BmsFromID.json():
            if BmsFromID.json()["error"]["code"] == 190:
                serializer = ViasSerializer(viaModel, data={'status': None})
                if serializer.is_valid():
                    serializer.save()
                return Response({"success": False,
                                 "status": "undefined",
                                 "messages": "Via {} Đã được thay đổi mật khẩu nên access token không còn hiệu lực, hãy cập nhật lại".format(via["name"])
                                 })
            return Response({"success": False,
                             "messages": "Via {} Xảy ra lỗi không xác định".format(via["name"])
                             })
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
                if checkingResult.json()["error"]["code"] == 368 or checkingResult.json()["error"]["code"] == 100:
                    serializer = ViasSerializer(viaModel, data={'status': 0})
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

    def getBmById(self, bmid):
        try:
            return Bm.objects.get(bmid=bmid)
        except Bm.DoesNotExist:
            return None

    def getBmStatus(self, bm):
        bmObject = self.getBmById(bm["id"])
        if bmObject == None:
            bm["status"] = None
            return bm
        bmsz = BmsSerializer(bmObject)
        bmInfo = bmsz.data
        bm["status"] = bmInfo["status"]
        return bm

    def filterByVerificationStatus(self, statusFilter, bm):
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
            if("error" in bmsFromUser.json()):
                response["error"]["viaError"].append(via["name"])
            else:
                ownerId = via["id"]
                ownerName = via["name"]
                ownerStatus = via["status"]
                # bmInfo = bmsFromUser.json()["businesses"]["data"]
                bmInfo = filter(
                    lambda x: (self.filterByVerificationStatus(statusFilter, x)), bmsFromUser.json()["businesses"]["data"])
                for business in bmInfo:
                    for bm in listBm:
                        if bm["id"] == business["id"]:
                            bm["owner"] += [{"id": ownerId,
                                             "name": ownerName, "status": ownerStatus}]
                            break
                    else:
                        business["owner"] = [
                            {"id": ownerId, "name": ownerName, "status": ownerStatus}]
                        listBm.append(business)

        listBm = map(lambda x: (self.extractBackupEmail(x)), listBm)
        listBm = map(lambda x: (self.getBmStatus(x)), listBm)
        response["data"] = listBm
        return Response(response)

    # def post(self, request, format=None):
    #     serializer = BmsSerializer(data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CheckBm(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        bmid = request.data["bmid"]
        viaFbIds = request.data["viaFbId"]
        print(viaFbIds)
        if bmid == None:
            return Response({"success": False, "message": "Hãy kiểm tra lại id của BM"})
        if viaFbIds == None:
            return Response({"success": False, "message": "Hãy cung cấp fbid của Via sở hữu bm"})
        vias = Via.objects.filter(
            isDeleted=False, id__in=viaFbIds.split(","))
        viasz = ViasSerializer(vias, many=True)
        print(viasz.data)

        notWorkingVias = []
        checkedVias = []
        bmStatus = 1
        isBmChecked = False
        updateBmStatus = "undefined"
        errorMessage = "Đã có lỗi xảy ra"
        errorLogs = []
        for via in viasz.data:
            print("here")
            if via["status"] == 0 or via["status"] == None or via["status"] == "":
                continue
            getAdAccountsFromBmResult = requests.get(
                url="https://graph.facebook.com/v9.0/{}/owned_ad_accounts".format(
                    bmid),
                params={
                    "access_token": via["accessToken"],
                    "fields": "name,is_notifications_enabled",
                })
            if "error" in getAdAccountsFromBmResult.json():
                error = {"via": via["id"],
                         "message": getAdAccountsFromBmResult.json()["error"]["code"],
                         "code": getAdAccountsFromBmResult.json()["error"]["message"]}
                errorLogs.append(error)
                continue
            adAccountsFromBm = getAdAccountsFromBmResult.json()["data"]
            if len(adAccountsFromBm) == 0:
                return Response({"success": False, "message": "BM hiện tại không sở hữu tài khoản quảng cáo, hãy tạo tài khoản quảng cáo trước khi kiểm tra BM"})
            adAccountId = adAccountsFromBm[0]["id"]
            print(adAccountId)
            updateAdAccoutResult = requests.post(
                url="https://graph.facebook.com/v9.0/{}".format(adAccountId),
                data={
                    "access_token": via["accessToken"],
                    "is_notifications_enabled": "true",
                })
            print(adAccountId)
            if "error" in updateAdAccoutResult.json():
                print(updateAdAccoutResult.json())
                if updateAdAccoutResult.json()["error"]["code"] == 368 or updateAdAccoutResult.json()["error"]["code"] == 100:
                    notWorkingVias.append(
                        {"viaId": via["id"], "name": via["name"]})
                    viaModel = Via.objects.filter(
                        isDeleted=False, fbid=via["fbid"])
                    serializer = ViasSerializer(
                        viaModel, data={'status': 0})
                    if serializer.is_valid():
                        serializer.save()
                        continue
                    error = {via: via["id"],
                             message: "Đã có lỗi xảy ra trong quá trình kết nối với Database"}
                    errorLogs.append(error)
                    continue
                elif updateAdAccoutResult.json()["error"]["code"] == 200 and updateAdAccoutResult.json()["error"]["error_subcode"] == 1815066:
                    bmStatus = 0
                    print("checked")
                else:
                    return Response({
                        "success": False,
                        "message": "Đã có lỗi xảy ra trong quá trình kết nối với facebook với via {}. error code: {}".format(via["name"],
                                                                                                                             updateAdAccoutResult.json()["error"]["code"])
                    })
            isBmChecked = True
            bms = Bm.objects.filter(bmid=bmid)
            bmsz = BmsSerializer(bms, many=True)
            errorMessage = None
            if len(bmsz.data) == 0:
                serializer = BmsSerializer(
                    data={"bmid": bmid, "status": bmStatus})
                updateBmStatus = "created"
                if serializer.is_valid():
                    serializer.save()
                    break
                error = {"via": via["id"],
                         "message": "Đã có lỗi xảy ra trong quá trình kết nối với Database"}
                errorLogs.append(error)
                break
            else:
                serializer = BmsSerializer(
                    bms[0], data={"status": bmStatus})
                updateBmStatus = "updated"
                if serializer.is_valid():
                    serializer.save()
                    break
                error = {"via": via["id"],
                         "message": "Đã có lỗi xảy ra trong quá trình kết nối với Database"}
                errorLogs.append(error)
                break
        print(bmStatus)
        if isBmChecked == True:
            successMessage = "BM không bị giới hạn"
            if bmStatus == 0:
                successMessage = "BM đã bị giới hạn"
            return Response({"success": True, "status": bmStatus, "message": successMessage, "errors": errorLogs})
        return Response({"success": False, "message": errorMessage, "errors": errorLogs})


class BackupBm(APIView):
    permission_classes = [permissions.IsAuthenticated]
    isSuccessfulClearBackup = True

    def clearOldBackupLink(self, backupId, token):
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
