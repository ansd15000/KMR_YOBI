def getMethod(request):
    if request.get_json() :
        return request.get_json()
    elif request.form :
        return dict(request.form)