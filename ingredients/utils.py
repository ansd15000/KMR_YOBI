def getMethod(request):
    if request.get_json() :
        return request.get_json()
    elif request.form :
        return dict(request.form)

# 신선, 양호, 위험, 만료
l = [0.3, 0]
d = { 
    "0": "양호", 
    "1": "위험",  
}
def __z(frash):
    result = None
    for idx, value in enumerate(l) :
        if value <= float(frash) :
            result = d[str(idx)]
            break
    return result

def getFreshLevel(shelf_life, userShelf_life):
    a = f'{userShelf_life / shelf_life: 0.1f}'  # 남은기간 퍼센트
    result = __z(a)
    if result is None :
        result = '만료'
    return result