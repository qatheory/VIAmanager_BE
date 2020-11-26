from apis.serializers import ViasSerializer, BmsSerializer
from apis.models import Via, Bm
import requests

checkAllBmStatus = False


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
        bm["status"] = None
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
    if (statusFilter != "2" and statusFilter != None):
        if (statusFilter == "1"):
            return (bm["status"] == 1)
        elif (statusFilter == "0"):
            return (bm["status"] == 0)
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
    listBm = list(
        map(lambda x: (filterByStatus(statusFilter, x)), listBm))
    response["data"] = listBm
    return (response)


def checkBm(bmid, viaFbIds):
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
                return ({
                    "success": False,
                    "message": "Đã có lỗi xảy ra trong quá trình kết nối với facebook với via {}. error code: {}".format(via["name"],
                                                                                                                         updateAdAccoutResult.json()["error"]["code"])
                })
        viasLimited = False
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
    if isBmChecked == True:
        successMessage = "BM không bị giới hạn"
        if bmStatus == 0:
            successMessage = "BM đã bị giới hạn"
        return ({"success": True, "status": bmStatus, "message": successMessage, "errors": errorLogs})

    print(errorMessage)
    if viasLimited == True:
        return ({"success": False, "message": "Tất cả VIA sở hữu BM này đều đã bị hạn chế, hãy kiểm tra lại access token của VIA", "errors": errorLogs})
    return ({"success": False, "message": errorMessage, "errors": errorLogs})
