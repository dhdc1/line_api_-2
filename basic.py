import json

if __name__ == "__main__":
    print('Start Here.')
    x = {
      
    }
    x['json']={
        
    }
    x['json']['contents']=[]
    
    n = list()
    n.append({
        'name':1
    })
    n.append({'name':2})
    x['json']['contents'].append({'actions':n})
    x['json']['contents'].append({'actions':[]})



    print(json.dumps(x))
