'''
    Code to calculate chrF score. Adapted from the implementation by Maja Popovic
    available at https://github.com/m-popovic/chrF

    Citation:
    # Maja Popović (2015).
    # "chrF: character n-gram F-score for automatic MT evaluation".
    # In Proceedings of the Tenth Workshop on Statistical Machine Translation (WMT15), pages 392–395
    # Lisbon, Portugal, September 2015.
'''

import sys
import math
import unicodedata
import argparse
from collections import defaultdict
import time
import string
    
def ngram_counts(wordList, order):
    counts = defaultdict(lambda: defaultdict(float))
    nWords = len(wordList)
    for i in range(nWords):
        for j in range(1, order+1):
            if i+j <= nWords:
                ngram = tuple(wordList[i:i+j])
                counts[j-1][ngram]+=1
   
    return counts

def ngram_matches(ref_ngrams, hyp_ngrams):
    matchingNgramCount = defaultdict(float)
    totalRefNgramCount = defaultdict(float)
    totalHypNgramCount = defaultdict(float)
 
    for order in ref_ngrams:
        for ngram in hyp_ngrams[order]:
            totalHypNgramCount[order] += hyp_ngrams[order][ngram]
        for ngram in ref_ngrams[order]:
            totalRefNgramCount[order] += ref_ngrams[order][ngram]
            if ngram in hyp_ngrams[order]:
                matchingNgramCount[order] += min(ref_ngrams[order][ngram], hyp_ngrams[order][ngram])


    return matchingNgramCount, totalRefNgramCount, totalHypNgramCount


def ngram_precrecf(matching, reflen, hyplen, beta):
    ngramPrec = defaultdict(float)
    ngramRec = defaultdict(float)
    ngramF = defaultdict(float)
    
    factor = beta**2
    
    for order in matching:
        if hyplen[order] > 0:
            ngramPrec[order] = matching[order]/hyplen[order]
        else:
            ngramPrec[order] = 1e-16
        if reflen[order] > 0:
            ngramRec[order] = matching[order]/reflen[order]
        else:
            ngramRec[order] = 1e-16
        denom = factor*ngramPrec[order] + ngramRec[order]
        if denom > 0:
            ngramF[order] = (1+factor)*ngramPrec[order]*ngramRec[order] / denom
        else:
            ngramF[order] = 1e-16
            
    return ngramF, ngramRec, ngramPrec

def computeChrF(refWords, hypWords, nworder, beta):
    norder = nworder

    # initialisation of document level scores
    totalMatchingCount = defaultdict(float)
    totalRefCount = defaultdict(float)
    totalHypCount = defaultdict(float)
    averageTotalF = 0.0

    word_metrics = list()
    nsent = 0
    for hline, rline in zip(hypWords, refWords):
        nsent += 1
        
        # preparation for multiple references
        maxF = 0.0
        bestWordMatchingCount = None
        
        hypNgramCounts = ngram_counts(hline.split(" "), nworder)

        refNgramCounts = ngram_counts(rline.split(" "), nworder)

        # number of overlapping n-grams, total number of ref n-grams, total number of hyp n-grams
        matchingNgramCounts, totalRefNgramCount, totalHypNgramCount = ngram_matches(refNgramCounts, hypNgramCounts)
                
        # n-gram f-scores, recalls and precisions
        ngramF, ngramRec, ngramPrec = ngram_precrecf(matchingNgramCounts, totalRefNgramCount, totalHypNgramCount, beta)

        sentRec  = sum(ngramRec.values())  / norder
        sentPrec = sum(ngramPrec.values()) / norder
        sentF    = sum(ngramF.values())    / norder

        maxF = sentF
        bestMatchingCount = matchingNgramCounts
        bestRefCount = totalRefNgramCount
        bestHypCount = totalHypNgramCount
        
        word_metrics.append({
            "precision": sentPrec,
            "recall": sentRec,
            "f": sentF
        })


        # collect document level ngram counts
        for order in range(nworder):
            totalMatchingCount[order] += bestMatchingCount[order]
            totalRefCount[order] += bestRefCount[order]
            totalHypCount[order] += bestHypCount[order]

        averageTotalF += maxF
     
    # total precision, recall and F (aritmetic mean of all ngrams)
    totalNgramF, totalNgramRec, totalNgramPrec = ngram_precrecf(totalMatchingCount, totalRefCount, totalHypCount, beta)

    totalF    = sum(totalNgramF.values())    / norder
    averageTotalF = averageTotalF / nsent
    totalRec  = sum(totalNgramRec.values())  / norder
    totalPrec = sum(totalNgramPrec.values()) / norder

    return word_metrics, {
        'total F': totalF, 
        'average total F': averageTotalF, 
        'total precision': totalPrec, 
        'total recall': totalRec
    }
