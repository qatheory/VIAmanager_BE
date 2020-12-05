from apis.services.bm import checkAllBms
from apis.services.vias import checkVias, checkAllVias


def autoCheckVias():
    checkAllViasResult = checkAllVias(True)
    print(checkAllViasResult)
    return True


def autoCheckBms():
    checkAllBmsResult = checkAllBms(True)
    print(checkAllBmsResult)
    return True


def autoBackupBms():
    backupAllBmsResult = backupAllBms(True)
    print(backupAllBmsResult)
    return True
