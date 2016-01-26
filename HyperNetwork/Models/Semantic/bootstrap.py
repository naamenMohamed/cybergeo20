# -*- coding: utf-8 -*-

# bootstrap for relevant terms extraction

import numpy,kwFunctions,utils
from multiprocessing import Pool


def test_bootstrap() :
    corpus = utils.get_data('SELECT id FROM refdesc WHERE abstract_keywords IS NOT NULL LIMIT 2000;','../../Data/dumps/20160126_cybergeo.sqlite3')
    for kwLimit in [50,100,200] :
        for subCorpusSize in [100,500,1000,2000] :
            bootstrapSize=25
            [relevantkw,relevant_dico,allkw] = bootstrap_subcorpuses(corpus,kwLimit,subCorpusSize,bootstrapSize)
            utils.export_dico_csv(relevant_dico,'res/conv_dico/bootstrap_relevantDico_kwLimit'+str(kwLimit)+'_subCorpusSize'+str(subCorpusSize)+'_bootstrapSize'+str(bootstrapSize),True)
            utils.export_list(relevantkw,'res/conv_kw/kw_'+str(kwLimit)+'_subCorpusSize'+str(subCorpusSize),False)
	    for i in range(len(allkw)) :
		local_kw = allkw[i]
		utils.export_list(relevantkw,'res/conv_kw/kw_'+str(kwLimit)+'_subCorpusSize'+str(subCorpusSize)+'_run'+str(i),False)


def run_bootstrap() :
    kwLimit=200
    subCorpusSize=10000
    bootstrapSize=30
    corpus = utils.get_data('SELECT id FROM refdesc WHERE abstract_keywords IS NOT NULL LIMIT 20000;','../../Data/dumps/20160126_cybergeo.sqlite3')
    [relevantkw,relevant_dico] = bootstrap_subcorpuses_parallel(corpus,kwLimit,subCorpusSize,bootstrapSize)
    utils.export_dico_csv(relevant_dico,'res/bootstrapParallel_relevantDico_kwLimit'+str(kwLimit)+'_subCorpusSize'+str(subCorpusSize)+'_bootstrapSize'+str(bootstrapSize),True)
    utils.export_list(relevantkw,'res/bootstrapParallel_relevantkw_kwLimit'+str(kwLimit)+'_subCorpusSize'+str(subCorpusSize)+'_bootstrapSize'+str(bootstrapSize),True)





def bootstrap_subcorpuses(corpus,kwLimit,subCorpusSize,bootstrapSize):
    N = len(corpus)

    print('Bootstrapping on corpus of size '+str(N))

    occurence_dicos = utils.import_kw_dico('../../Data/dumps/20160125_cybergeo.sqlite3')

    # generate bSize extractions
    #   -> random subset of 1:N of size subCorpusSize
    extractions = [numpy.random.random_integers(0,(N-1),subCorpusSize) for b in range(bootstrapSize)]

    mean_termhoods = dict() # mean termhoods progressively updated
    ref_kw_dico = dict() # ref -> kw dico : cumulated on repetitions. if a kw is relevant a few time, counted as 0 in mean.

    allkw = []

    for eind in range(len(extractions)) :
        print("bootstrap : run "+str(eind))
        extraction = extractions[eind]
        subcorpus = [corpus[i] for i in extraction]
        [keywords,ref_kw_local_dico] = kwFunctions.extract_relevant_keywords(subcorpus,kwLimit,occurence_dicos)

	allkw.append(keywords.keys())

        # add termhoods
        for kw in keywords.keys() :
            if kw not in mean_termhoods : mean_termhoods[kw] = 0
            mean_termhoods[kw] = mean_termhoods[kw] + keywords[kw]

        # update p->kw dico
        for ref in ref_kw_local_dico.keys() :
            if ref not in ref_kw_dico : ref_kw_dico[ref] = set()
            for kw in ref_kw_local_dico[ref] :
		       ref_kw_dico[ref].add(kw)

    # sort on termhoods (no need to normalize) adn returns
    res = kwFunctions.extract_from_termhood(mean_termhoods,ref_kw_dico,kwLimit)
    print(res)
    print(allkw)
    res.append(allkw)
    return(res)


def bootrun(extraction,corpus,kwLimit,occurence_dicos):
    subcorpus = [corpus[i] for i in extraction]
    return(kwFunctions.extract_relevant_keywords(subcorpus,kwLimit,occurence_dicos))



##
# with parallel processing
def bootstrap_subcorpuses_parallel(corpus,kwLimit,subCorpusSize,bootstrapSize):
    N = len(corpus)

    print('Parallel bootstrapping on corpus of size '+str(N))

    occurence_dicos = utils.import_kw_dico('../../Data/dumps/20160125_cybergeo.sqlite3')

    # generate bSize extractions
    #   -> random subset of 1:N of size subCorpusSize
    extractions = [[numpy.random.random_integers(0,(N-1),subCorpusSize),corpus,kwLimit,occurence_dicos] for b in range(bootstrapSize)]

    mean_termhoods = dict() # mean termhoods progressively updated
    ref_kw_dico = dict() # ref -> kw dico : cumulated on repetitions. if a kw is relevant a few time, counted as 0 in mean.

    #for eind in range(len(extractions)) :
    #    print("bootstrap : run "+str(eind))
    #    extraction = extractions[eind]
    #    subcorpus = [corpus[i] for i in extraction]
    #    [keywords,ref_kw_local_dico] = kwFunctions.extract_relevant_keywords(subcorpus,kwLimit,occurence_dicos)

    p = Pool(15)
    res = p.map(bootrun,extractions)

    for singleres in res :
	keywords = singleres[0]
	ref_kw_local_dico = singleres[1]

        # add termhoods
        for kw in keywords.keys() :
            if kw not in mean_termhoods : mean_termhoods[kw] = 0
            mean_termhoods[kw] = mean_termhoods[kw] + keywords[kw]

        # update p->kw dico
        for ref in ref_kw_local_dico.keys() :
            if ref not in ref_kw_dico : ref_kw_dico[ref] = set()
            for kw in ref_kw_local_dico[ref] :
                       ref_kw_dico[ref].add(kw)

    # sort on termhoods (no need to normalize) adn returns
    return(kwFunctions.extract_from_termhood(mean_termhoods,ref_kw_dico,kwLimit))



