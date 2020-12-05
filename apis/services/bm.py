from apis.serializers import ViasSerializer, BmsSerializer, ProcessSerializer
from apis.models import Via, Bm, Process
from datetime import date, datetime
from apis.services.common import log
import requests


def setCheckingProgress(status):
    checkAllBmStatus = status


def getCheckingProgress():
    return checkAllBmStatus


def getBmById(bmid):
    try:
        return Bm.objects.get(bmid=bmid)
    except Bm.DoesNotExist:
        return None


def getBmStatus(bm):
    bmObject = getBmById(bm["id"])
    if bmObject == None:
        bm["status"] = 2
        return bm
    bmsz = BmsSerializer(bmObject)
    bmInfo = bmsz.data
    bm["status"] = bmInfo["status"]
    return bm


def filterByVerificationStatus(verificationStatusFilter, bm):
    if (verificationStatusFilter != "0" and verificationStatusFilter != None):
        if (verificationStatusFilter == "1"):
            return (bm["verification_status"] != "not_verified")
        elif (verificationStatusFilter == "2"):
            return (bm["verification_status"] == "not_verified")
    else:
        return True


def filterByStatus(statusFilter, bm):
    if (statusFilter != "3" and statusFilter != None):
        if (statusFilter == "1"):
            return (bm["status"] == 1)
        elif (statusFilter == "0"):
            return (bm["status"] == 0)
        elif (statusFilter == "2"):
            return (bm["status"] == 2)
    else:

        return True


def extractBackupEmail(bm):

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


def getListBm(request):
    viaFilter = None
    statusFilter = None
    if request != None:
        viaFilter = request.GET.get("via", None)
        # verificationStatusFilter = request.GET.get("verificationStatus", None)
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
            # bmInfo = filter(
            #     lambda x: (filterByVerificationStatus(verificationStatusFilter, x)), bmsFromUser.json()["businesses"]["data"])
            bmInfo = bmsFromUser.json()["businesses"]["data"]
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

    listBm = map(lambda x: (extractBackupEmail(x)), listBm)
    listBm = map(lambda x: (getBmStatus(x)), listBm)
    listBm = filter(lambda x: (filterByStatus(statusFilter, x)), listBm)
    response["data"] = listBm
    return (response)


def saveBmStatus(bmid, via, bmStatus):
    bms = Bm.objects.filter(bmid=bmid)
    bmsz = BmsSerializer(bms, many=True)

    if len(bmsz.data) == 0:
        serializer = BmsSerializer(
            data={"bmid": bmid, "status": bmStatus})
        updateBmStatus = "created"
        if serializer.is_valid():
            serializer.save()
            return {"via": via["id"],
                    "message": "Đã có lỗi xảy ra trong quá trình kết nối với Database"}
        return True
    else:
        serializer = BmsSerializer(
            bms[0], data={"status": bmStatus})
        updateBmStatus = "updated"
        if serializer.is_valid():
            serializer.save()
            return {"via": via["id"],
                    "message": "Đã có lỗi xảy ra trong quá trình kết nối với Database"}
        errorLogs.append(error)
        return True


def checkBm(bmid, viaFbIds, bmName=None, log=False):

    if bmid == None:
        return ({"success": False, "message": "Hãy kiểm tra lại id của BM"})
    if viaFbIds == None:
        return ({"success": False, "message": "Hãy cung cấp fbid của Via sở hữu bm"})
    vias = Via.objects.filter(
        isDeleted=False, id__in=viaFbIds)
    viasz = ViasSerializer(vias, many=True)

    notWorkingVias = []
    viasLimited = True
    bmStatus = 1
    isBmChecked = False
    updateBmStatus = "undefined"
    errorMessage = "Đã có lỗi xảy ra"
    errorLogs = []
    for via in viasz.data:
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
            saveBmStatusResult = saveBmStatus(bmid, via, 2)
            if log == True:
                log({"process": "checkBM", "log": "BM {} hiện tại không sở hữu tài khoản quảng cáo, hãy tạo tài khoản quảng cáo trước khi kiểm tra BM".format(
                    bmName), "status": "neutral", "error": "ERROR"})
            return ({"success": False, "message": "BM hiện tại không sở hữu tài khoản quảng cáo, hãy tạo tài khoản quảng cáo trước khi kiểm tra BM"})
        adAccountId = adAccountsFromBm[0]["id"]
        updateAdAccoutResult = requests.post(
            url="https://graph.facebook.com/v9.0/{}".format(adAccountId),
            data={
                "access_token": via["accessToken"],
                "is_notifications_enabled": "true",
            })

        if "error" in updateAdAccoutResult.json():
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
                saveBmStatusResult = saveBmStatus(bmid, via, 2)
                if log == True:
                    log({"process": "checkBM", "log": "BM {}. Đã có lỗi xảy ra trong quá trình kết nối với facebook với via {}. error code: {}".format(bmName, via["name"],
                                                                                                                                                       updateAdAccoutResult.json()["error"]["code"]), "status": "false", "error": "FATAL"})
                return ({
                    "success": False,
                    "message": "Đã có lỗi xảy ra trong quá trình kết nối với facebook với via {}. error code: {}".format(via["name"],
                                                                                                                         updateAdAccoutResult.json()["error"]["code"])
                })
        viasLimited = False
        isBmChecked = True
        errorMessage = None
        saveBmStatusResult = saveBmStatus(bmid, via, bmStatus)
        if saveBmStatusResult != True:
            errorLogs.append(saveBmStatusResult)
    if isBmChecked == True:
        successMessage = "BM không bị giới hạn"
        if log == True:
            logMessage = "BM {} không bị giới hạn".format(bmName)
            log({"process": "checkBM", "log": logMessage,
                 "status": "success", "error": "NONE"})
        if bmStatus == 0:
            successMessage = "BM đã bị giới hạn"
            if log == True:
                logMessage = "BM {} đã bị giới hạn".format(bmName)
                log({"process": "checkBM", "log": logMessage,
                     "status": "warning", "error": "NONE"})
        return ({"success": True, "status": bmStatus, "message": successMessage, "errors": errorLogs})

    print(errorMessage)
    if viasLimited == True:
        if log == True:
            log({"process": "checkBM", "log": "Tất cả VIA sở hữu BM {} đều đã bị hạn chế, hãy kiểm tra lại access token của VIA".format(bmName),
                 "status": "warning", "error": "NONE"})
        return ({"success": False, "message": "Tất cả VIA sở hữu BM này đều đã bị hạn chế, hãy kiểm tra lại access token của VIA", "errors": errorLogs})
    if log == True:
        log({"process": "checkBM", "log": "Đã có lỗi không xác định xảy ra với BM {}".format(bmName),
             "status": "warning", "error": "FATAL"})
    return ({"success": False, "message": errorMessage, "errors": errorLogs})


def backupBm(owners, bmid, log=False):
    if(not owners):
        if log == True:
            log({"process": "backupBM", "log": "Chưa cung cấp via cho BM {}".format(bmName),
                 "status": "false", "error": "FATAL"})
        return ({"success": False, "status": "error", "messages": "Chưa cung cấp via"})
    if len(owners) == 0:
        if log == True:
            log({"process": "backupBM", "log": "Chưa cung cấp via cho BM {}".format(bmName),
                 "status": "false", "error": "FATAL"})
        return ({"success": False, "status": "error", "messages": "Chưa cung cấp via"})
    if(not bmid):
        if log == True:
            log({"process": "backupBM", "log": "Không tìm thấy BM {}".format(bmName),
                 "status": "false", "error": "FATAL"})
        return ({"success": False, "status": "error", "messages": "Chưa cung cấp bm"})
    listViasId = []
    for owner in owners:
        listViasId.append(owner["id"])
    vias = Via.objects.filter(id__in=listViasId)
    vias = vias.filter(status=1)
    viasz = ViasSerializer(vias, many=True)
    if len(viasz.data) == 0:
        if log == True:
            log({"process": "backupBM", "log": "BM {} Không được sở hữu bởi Via còn hoạt động".format(bmName),
                 "status": "false", "error": "ERROR"})
        return ({"success": False, "messages": "BM Không được sở hữu bởi Via còn hoạt động"})
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
        if log == True:
            log({"process": "backupBM", "log": "Đã có lỗi xảy ra với BM {}, hãy kiểm tra lại access token".format(bmName),
                 "status": "false", "error": "ERROR"})
        return ({"success": False, "status": "error", "messages": "Đã có lỗi xảy ra, hãy kiểm tra lại access token"})
    if isSuccessfulClearBackup == False:
        if log == True:
            log({"process": "backupBM", "log": "Cấn kiểm tra lại BM {}, việc dọn sạch link backup cũ xảy ra lỗi".format(bmName),
                 "status": "false", "error": "ERROR"})
        return ({"success": True, "status": "warning", "messages": "Cấn kiểm tra lại BM, việc dọn sạch link backup cũ xảy ra lỗi"})
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
    if log == True:
        log({"process": "backupBM", "log": "Làm mới link backup thành công cho BM {}".format(bmName),
             "status": "success", "error": "NONE"})
    return ({"success": True, "status": "success", "messages": "Làm mới link backup thành công", "data": data})


def checkBmProcess(process):
    checkAllBmProcess = Process.objects.filter(name=process)
    checkAllBmProcessSz = ProcessSerializer(checkAllBmProcess, many=True)
    print(checkAllBmProcessSz.data[0]["status"])
    if checkAllBmProcessSz.data == []:
        serializer = ProcessSerializer(
            data={"name": process, "status": 1})
        if serializer.is_valid():
            serializer.save()
            return {"success": True, "process": False}
        else:
            return {"success": False, "process": False}
    if checkAllBmProcessSz.data[0]["status"] == 0:
        serializer = ProcessSerializer(checkAllBmProcess[0],
                                       data={"name": process, "status": 1})
        if serializer.is_valid():
            serializer.save()
            return {"success": True, "process": False}
        else:
            return {"success": False, "process": False}
    return {"success": True, "process": True}

# def get(self, request, format=None):
    #     checkAllBmProcess = Process.objects.filter(name="checkAllBm")
    #     serializer = ProcessSerializer(checkAllBmProcess[0],
    #                                    data={"name": "checkAllBm", "status": 0})
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response({"success": True, "process": False})
    #     return Response({"success": False, "process": False})


def checkAllBms(force=False):
    log = True
    if force == False:
        log = False
        checkProcess = checkBmProcess("checkAllBm")
        if checkProcess["success"] == False:
            return ({"success": False, "status": False, "message": "đã có lỗi xảy ra với hệ thống"})
        if checkProcess["process"] == True:
            return ({"success": True, "status": False, "message": "Quá trình kiểm tra toàn bộ BM đang diễn ra"})
    getListBmResponse = getListBm(None)
    BmList = getListBmResponse["data"]
    checkBmResponseList = []
    for bm in BmList:
        bmid = bm["id"]
        viaFbIds = list(map(lambda owner: owner["id"], bm["owner"]))
        checkBmResponse = checkBm(bmid, viaFbIds, bm, log)
        checkBmResponse["bmid"] = bmid
        checkBmResponse["name"] = bm["name"]
        checkBmResponseList.append(checkBmResponse)

    checkAllBmProcess = Process.objects.filter(name="checkAllBm")
    serializer = ProcessSerializer(checkAllBmProcess[0],
                                   data={"name": "checkAllBm", "status": 0})
    if serializer.is_valid():
        serializer.save()
        return ({"success": True, "status": True, "message":  "Quá trình kiểm tra toàn bộ BM đã hoàn tất"})
    return ({"success": True, "status": True, "message": "Đã có lỗi hệ thống xảy ra", "error": serializer.errors})


def backupAllBms(force=False):
    log = True
    if force == False:
        log = False
        checkProcess = checkBmProcess("backupAllBm")
        if checkProcess["success"] == False:
            return ({"success": False, "status": False, "message": "đã có lỗi xảy ra với hệ thống"})
        if checkProcess["process"] == True:
            return ({"success": True, "status": False, "message": "Quá trình backup toàn bộ BM đang diễn ra"})
    getListBmResponse = getListBm(None)
    BmList = getListBmResponse["data"]
    for bm in BmList:
        bmid = bm["id"]
        viaIds = list(map(lambda owner: owner["id"], bm["owner"]))
        checkBmResponse = backupBm(viaIds, bmid, log)
    return ({"success": True, "status": True, "message": "Quá trình backup toàn bộ BM đã hoàn tất"})
