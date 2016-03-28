# -*- coding: utf-8 -*-

# specific utils for bootstrap

##
# mongo version : database is the mongodb object
def update_kw_tm(kw,incr,database):
    #prev = utils.fetchone_sqlite('SELECT cumtermhood,ids FROM relevant WHERE keyword=\''+kw+'\';',database)
    prev = database.relevant.find_one({'keyword':kw})
    #t = 0
    #ids=''
    #print(prev)
    if prev is not None:
        #t = prev[0]+incr
        #ids = prev[1]
        #utils.insert_sqlite('UPDATE relevant SET keyword=\''+kw+'\',cumtermhood='+str(t)+',ids=\''+ids+'\' WHERE keyword=\''+kw+'\';',database)
        prev['cumtermhood']=prev['cumtermhood']+incr
        database.relevant.find_one_and_update({'keyword':kw},prev)
    else :
        # insert
        #utils.insert_sqlite('INSERT INTO relevant VALUES (\''+kw+'\','+str(incr)+',\'\');',database)
        database.relevant.insert_one({'keyword':kw,'cumtermhood':incr,'ids':[]})



def update_kw_dico(i,kwlist,database):
    # update id -> kws dico
    #prev = utils.fetchone_sqlite('SELECT keywords FROM dico WHERE id=\''+i+'\';',database)
    #kws = set()
    prev = database.dico.find_one({'id':i})
    #if prev is not None: kws = set(prev[0].split(";"))
    #for kw in kwlist :
    #    kws.add(kw)
    #if prev is not None:
    #    utils.insert_sqlite('UPDATE dico SET id=\''+i+'\',keywords=\''+utils.implode(kws,";")+'\' WHERE id=\''+i+'\';',database)
    #else :
    #    utils.insert_sqlite('INSERT INTO dico VALUES (\''+i+'\',\''+utils.implode(kws,";")+'\')',database)
    if prev is not None:
        kwset=set(prev['keywords'])
        for kw in kwlist :
            kwset.add(kw)
        prev['keywords']=kwset
        database.relevant.find_one_and_update({'id':i},prev)
    else :
        database.relevant.insert_one({'id':i,'keywords':kwlist})

    # update kw -> id
    for kw in kwlist :
        #prev = utils.fetchone_sqlite('SELECT * FROM relevant WHERE keyword=\''+kw+'\';',database)
        #ids = set()
        prev = database.relevant.find_one({'keyword':kw})
        if prev is not None :
            #ids = set(prev[2].split(";"))
            ids=set(prev['ids'])
            ids.add(i)
            prev['ids']=ids
            #utils.insert_sqlite('UPDATE relevant SET keyword=\''+kw+'\',cumtermhood='+str(prev[1])+',ids=\''+utils.implode(ids,";")+'\' WHERE keyword=\''+kw+'\';',database)
            database.relevant.find_one_and_update({'keyword':kw},prev)
        else :# this case must never happen
            #utils.insert_sqlite('INSERT INTO relevant VALUES (\''+kw+'\',0,\''+i+'\');',database)
            database.relevant.insert_one({'keyword':kw,'cumtermhood':0,'ids':[i]})


def update_count(bootstrapSize,database):
    #prev = utils.fetchone_sqlite('SELECT value FROM params WHERE key=\'count\'',database)
    prev=database.params.find_one({'key':'count'})
    if prev is not None:
        #t=prev[0]+bootstrapSize
	    #utils.insert_sqlite('UPDATE params SET value='+str(t)+' WHERE key=\'count\';',database)
        prev['value']=prev['value']+bootstrapSize
        database.params.find_one_and_update({'key':'count'},prev)
    else :
	    #utils.insert_sqlite('INSERT INTO params VALUES (\'count\','+str(bootstrapSize)+')',database)
        database.params.insert_one({'key':'count','value':bootstrapSize})