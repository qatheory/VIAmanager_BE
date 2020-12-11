from apis.serializers import ViasSerializer, BmsSerializer, ProcessSerializer
from apis.models import Via, Bm, Process
from datetime import date, datetime
from apis.services.common import log
import requests


def getViafromId(id):
    try:
        return Via.objects.get(pk=id)
    except Via.DoesNotExist:
        return "error"


def checkVias(pk, log=False):
    viaModel = getViafromId(pk)
    if viaModel == "error":
        return ({"success": False,
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
            if log == True:
                log({"process": "checkVia", "log": "Via {} Đã được thay đổi mật khẩu nên access token không còn hiệu lực, hãy cập nhật lại".format(
                    via["name"]), "status": "false", "error": "ERROR"})
            return ({"success": False,
                     "status": "undefined",
                     "messages": "Via {} Đã được thay đổi mật khẩu nên access token không còn hiệu lực, hãy cập nhật lại".format(via["name"])
                     })
        if log == True:
            log({"process": "checkVia", "log": "Via {} Xảy ra lỗi không xác định".format(
                via["name"]), "status": "false", "error": "FATAL"})
        return ({"success": False,
                 "messages": "Via {} Xảy ra lỗi không xác định".format(via["name"])
                 })

    listBusiness = BmsFromID.json()["businesses"]["data"]
    if len(listBusiness) == 0:
        if log == True:
            log({"process": "checkVia", "log": "Via {} không hoạt động, user chưa được kết nối với BM".format(
                via["name"]), "status": "false", "error": "ERROR"})
        return ({"success": False,
                 "messages": "Via không hoạt động, user chưa được kết nối với BM"})
    listPendingUsers = []
    listBusinessContainBackup = list(
        filter(lambda x: "pending_users" in x, listBusiness))

    # if("pending_users" in listBusiness[0]):
    #     listPendingUsers = listBusiness[0]["pending_users"]["data"]
    # print(listBusinessContainBackup)
    if len(listBusinessContainBackup) == 0:
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
        print(checkingResult.json())
        if "error" in checkingResult.json():
            if checkingResult.json()["error"]["code"] == 368 or checkingResult.json()["error"]["code"] == 100:
                serializer = ViasSerializer(viaModel, data={'status': 0})
                if serializer.is_valid():
                    serializer.save()
                    if log == True:
                        log({"process": "checkVia", "log": "Via {} hiện đã bị hạn chế".format(
                            via["name"]), "status": "warning", "error": "NONE"})
                    return ({"success": True,
                             "status": False,
                             "messages": "Via {} hiện đã bị hạn chế".format(via["name"])
                             })
                if log == True:
                    log({"process": "checkVia", "log": "Via {} hiện đã bị hạn chế. Tuy nhiên có lỗi khi kết nối với Database".format(
                        via["name"]), "status": "warning", "error": "ERROR"})
                return ({"success": True,
                         "status": False,
                         "messages": "Via {} hiện đã bị hạn chế. Tuy nhiên có lỗi khi kết nối với Database".format(via["name"])
                         })
            if log == True:
                log({"process": "checkVia", "log": "Đã có lỗi xảy ra hãy thử kiểm tra lại access token của Via {}".format(
                    via["name"]), "status": "false", "error": "FATAL"})
            return ({"success": False,
                     "messages": "Đã có lỗi xảy ra hãy thử kiểm tra lại access token của Via"})
        serializer = ViasSerializer(viaModel, data={'status': 1})
        if serializer.is_valid():
            serializer.save()
            return ({"success": True,
                     "status": True,
                     "messages": "Via {} hiện đang hoạt động".format(via["name"])
                     })
        if log == True:
            log({"process": "checkVia", "log": "Via {} hiện đang hoạt động. Tuy nhiên có lỗi khi kết nối với Database".format(
                via["name"]), "status": "success", "error": "ERROR"})
        return ({"success": True,
                 "status": True,
                 "messages": "Via {} hiện đang hoạt động. Tuy nhiên có lỗi khi kết nối với Database".format(via["name"])
                 })
    else:
        backupUser = listBusinessContainBackup[0]["pending_users"]["data"]
        print(backupUser)
        createdDate = datetime.strptime(
            backupUser[0]["created_time"], "%Y-%m-%dT%H:%M:%S%z")
        formattedDate = createdDate.strftime("%d_%m_%Y")
        selectedPendingUser = backupUser[0]
        checkingResult = requests.post(
            url="https://graph.facebook.com/v8.0/{}".format(
                selectedPendingUser["id"]),
            data={
                "access_token":
                via["accessToken"],
                "role": "ADMIN",
                # "email": "{}@backup.data".format(formattedDate)
            })
        print(checkingResult.json())
        if "error" in checkingResult.json():
            if checkingResult.json()["error"]["code"] == 368:
                serializer = ViasSerializer(viaModel, data={'status': 0})
                if serializer.is_valid():
                    serializer.save()
                    if log == True:
                        log({"process": "checkVia", "log": "Via {} hiện đã bị hạn chế".format(
                            via["name"]), "status": "warning", "error": "NONE"})
                    return ({"success": True,
                             "status": False,
                             "messages": "Via {} hiện đã bị hạn chế".format(via["name"])
                             })
                if log == True:
                    log({"process": "checkVia", "log": "Via {} hiện đã bị hạn chế. Tuy nhiên có lỗi khi kết nối với Database".format(
                        via["name"]), "status": "warning", "error": "ERROR"})
                return ({"success": True,
                         "status": False,
                         "messages": "Via {} hiện đã bị hạn chế. Tuy nhiên có lỗi khi kết nối với Database".format(via["name"])
                         })
            if log == True:
                log({"process": "checkVia", "log": "Đã có lỗi xảy ra hãy thử kiểm tra lại access token của Via {}".format(
                    via["name"]), "status": "false", "error": "FATAL"})
            return ({"success": False,
                     "messages": "Đã có lỗi xảy ra trong quá trình kết nối với Facebook"})
        serializer = ViasSerializer(viaModel, data={"status": 1})
        if serializer.is_valid():
            serializer.save()
            return ({"success": True,
                     "status": True,
                     "messages": "Via {} hiện đang hoạt động".format(via["name"])
                     })
        if log == True:
            log({"process": "checkVia", "log": "Via {} hiện đang hoạt động. Tuy nhiên có lỗi khi kết nối với Database".format(
                via["name"]), "status": "success", "error": "ERROR"})
        return ({"success": True,
                 "status": True,
                 "messages": "Via {} hiện đang hoạt động. Tuy nhiên có lỗi khi kết nối với Database".format(via["name"])
                 })
    if log == True:
        log({"process": "checkVia", "log": "Lỗi không xác định với Via {}".format(
            via["name"]), "status": "false", "error": "FATAL"})
    return ({"success": False,
             "messages": "Lỗi không xác định"})


def checkViaProcess():
    checkAllViaProcess = Process.objects.filter(name="checkAllVia")
    checkAllViaProcessSz = ProcessSerializer(checkAllViaProcess, many=True)
    if checkAllViaProcessSz.data == []:
        serializer = ProcessSerializer(
            data={"name": "checkAllVia", "status": 1})
        if serializer.is_valid():
            serializer.save()
            return {"success": True, "process": False}
        else:
            return {"success": False, "process": False}
    if checkAllViaProcessSz.data[0]["status"] == 0:
        serializer = ProcessSerializer(checkAllViaProcess[0],
                                       data={"name": "checkAllVia", "status": 1})
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
#         return ({"success": True, "process": False})
#     return ({"success": False, "process": False})


def checkAllVias(force=False):
    log = True
    if force == False:
        log = False
        checkProcess = checkViaProcess()
        if checkProcess["success"] == False:
            return ({"success": False, "status": False, "message": "đã có lỗi xảy ra với hệ thống"})
        if checkProcess["process"] == True:
            return ({"success": True, "status": False, "message": "Quá trình kiểm tra toàn bộ VIA đang diễn ra"})
    viaModel = Via.objects.filter(isDeleted=False)
    viasz = ViasSerializer(viaModel, many=True)
    vias = viasz.data
    for via in vias:
        checkVias(via["id"], log)
    checkAllViaProcess = Process.objects.filter(name="checkAllVia")
    serializer = ProcessSerializer(checkAllViaProcess[0],
                                   data={"name": "checkAllVia", "status": 0})
    if serializer.is_valid():
        serializer.save()
        return ({"success": True, "status": True, "message":  "Quá trình kiểm tra toàn bộ VIA đã hoàn tất"})
    return ({"success": True, "status": True, "message": "Đã có lỗi hệ thống xảy ra", "error": serializer.errors})
