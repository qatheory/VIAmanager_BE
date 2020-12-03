def log(logData):
    serializer = ViasSerializer(data=logData)
    if serializer.is_valid():
        serializer.save()
