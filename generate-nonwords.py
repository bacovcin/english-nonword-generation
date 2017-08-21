import sys
import re
import pickle
import random

def init(vowel_list):
    # Load the SUBTLEX US frequency data as a list of dictionaries
    freqs = []
    with open('SUBTLEXus74286wordstextversion.txt') as subfile:
        names = subfile.readline().rstrip().split('\t')
        for line in subfile:
            freqs.append({})
            s = line.rstrip().split('\t')
            for i in range(len(s)):
                if names[i] == 'FREQcount':
                    freqs[-1][names[i]] = int(s[i])
                else:
                    freqs[-1][names[i]] = s[i]

    # Load the CMUDict data as a dictionary (word -> list of phonemes)
    cmudict = {}
    cmudict_bkwd = []
    with open('cmudict/cmudict.dict') as cmufile:
        for line in cmufile:
            s = line.rstrip().split(' ')
            cmudict[s[0]] = s[1:]
            cmudict_bkwd.append(''.join(s[1:]))

    # Get the intersection of SUBTLEX and CMUDict
    pron_freqs = [x for x in freqs if x['Word'] in cmudict.keys()]

    # Add the pronunciations into the intersection list
    # (Use # for word beginning and end)
    for i in range(len(pron_freqs)):
        pron_freqs[i]['pron'] = cmudict[pron_freqs[i]['Word']]

    # Store information for frequency weighted onsets, vowels, and codas
    onsets = {}
    for freq in pron_freqs:
        curonset = ''
        for phone in freq['pron']:
            if phone not in vowel_list:
                curonset += phone
            else:
                break
        try:
            onsets[curonset] += freq['FREQcount']
        except KeyError:
            onsets[curonset] = freq['FREQcount']

    vowels = {}
    codas = {}
    curcoda = []
    curonset = ''
    for freq in pron_freqs:
        found_vowel = 0
        for phone in freq['pron']:
            if phone in vowel_list:
                try:
                    vowels[phone] += freq['FREQcount']
                except KeyError:
                    vowels[phone] = freq['FREQcount']
                if found_vowel != 0:
                    if len(curcoda) > 0:
                        for i in range(-1,-len(curcoda)-1,-1):
                            if ''.join(curcoda[i:]) not in onsets.keys():
                                break
                        else:
                            curonset = ''.join(curcoda)
                            curcoda = ''
                        if i != -1:
                            curonset = ''.join(curcoda[i+1:])
                            curcoda = curcoda[:i+1]
                    try:
                        codas[''.join(curcoda)] += freq['FREQcount']
                    except KeyError:
                        codas[''.join(curcoda)] = freq['FREQcount']
                    onsets[curonset] += freq['FREQcount']
                found_vowel += 1
                curcoda = []
                curonset = ''
            elif found_vowel != 0:
                curcoda.append(phone)
        else:
            curcoda = ''.join(curcoda)+curonset
            try:
                codas[curcoda] += freq['FREQcount']
            except KeyError:
                codas[curcoda] = freq['FREQcount']

    pickle.dump((onsets, vowels, codas, cmudict_bkwd),
                open('mypickle.pkl','wb'))
    # Return the onset, vowel, and coda frequencies for future processing
    return onsets, vowels, codas, cmudict_bkwd

def get_vowel_list():
    vowel_list = []
    with open('cmudict/cmudict.phones') as cmuphons:
        for line in cmuphons:
            s = line.rstrip().split('\t')
            if s[1] == 'vowel':
                vowel_list.append(s[0]+'0')
                vowel_list.append(s[0]+'1')
                vowel_list.append(s[0]+'2')
    return vowel_list

def select_element(seq):
    totalcount = sum([x[1] for x in seq])
    myint = random.randint(0,totalcount)
    mybase = 0
    for i in range(len(seq)):
        myciel = mybase + seq[i][1]
        if myint >= mybase and myint < myciel:
            return seq[i][0]
        mybase = myciel
    else:
        return seq[-1][0]

def generate_list(onsets, vowels, codas, cmudict, 
                  numsyl, numwords, first_syl_stress,
                  onsetre, vowelre, codare,
                  includesylbreaks,norhyme,stressrhyme):
    wordcount = 0
    nonwords = []
    if norhyme:
        rhymes = []
    curonsets = [(x,onsets[x]) for x in onsets]
    curcodas = [(x,codas[x]) for x in codas]
    while wordcount < numwords:
        sylcount = 0
        curword = ''
        hadstress = 0
        while sylcount < numsyl:
            if sylcount == 0 and first_syl_stress:
                curvowels = [(x,vowels[x]) for x in vowels
                             if x[-1] not in ('0','2')]
            elif hadstress == 0:
                curvowels = [(x,vowels[x]) for x in vowels]
            else:
                curvowels = [(x,vowels[x]) for x in vowels
                             if x[-1] != '1']
            myonset = select_element(curonsets)
            myvowel = select_element(curvowels)
            mycoda = select_element(curcodas)
            if norhyme:
                if ((stressrhyme and myvowel[-1] == '1') or
                    (not stressrhyme and sylcount == numsyl - 1)):
                    while myvowel + mycoda in rhymes:
                        myvowel = select_element(curvowels)
                        mycoda = select_element(curcodas)
                        if stressrhyme and myvowel[-1] != '1':
                            break
            if (onsetre.match(myonset) is not None and
                vowelre.match(myvowel) is not None and
                codare.match(mycoda) is not None):
                if myvowel[-1] == '1':
                    hadstress = 1
                if includesylbreaks:
                    curword += myonset + myvowel + mycoda + '-'
                else:
                    curword += myonset + myvowel + mycoda
                if norhyme:
                    rhymes.append(myvowel + mycoda)
                sylcount += 1
        if includesylbreaks:
            curword = curword[:-1]
        if curword not in cmudict and curword not in nonwords:
            wordcount += 1
            nonwords.append(curword)
    return(nonwords)

if __name__ == '__main__':
    numsyl = 1
    numwords = 10
    firststress = True
    includesylbreaks = True
    outfilename = ''
    onsetre = re.compile('.*')
    vowelre = re.compile('.*')
    codare = re.compile('.*')
    norhyme = False
    stressrhyme = True
    for arg in sys.argv:
        s = arg.split('=')
        if s[0] == 'numsyl':
            try:
                numsyl = int(s[1])
            except TypeError:
                print('Your numsyl flag must be an integer')
        elif s[0] == 'numwords':
            try:
                numwords = int(s[1])
            except TypeError:
                print('Your numsyl flag must be an integer')
        elif s[0] == 'nostress':
            firststress = False
        elif s[0] == 'file':
            outfilename = s[1]
        elif s[0] == 'nobreaks':
            includesylbreaks = False
        elif s[0] == 'norhyme':
            norhyme = True
        elif s[0] == 'nostressrhyme':
            stressrhyme = False
        elif s[0] == 'onset':
            try:
                onsetre = re.compile(s[1])
            except:
                print('Your onset flag must be a valid regular expression.')
        elif s[0] == 'vowel':
            try:
                vowelre = re.compile(s[1])
            except:
                print('Your vowel flag must be a valid regular expression.')
        elif s[0] == 'coda':
            try:
                codare = re.compile(s[1])
            except:
                print('Your coda flag must be a valid regular expression.')
    vowel_list = get_vowel_list()
    vowel_list = get_vowel_list()
    try:
        onsets, vowels, codas, cmudict_bkwd = pickle.load(open('mypickle.pkl',
                                                               'rb'))
    except Exception as e:
        print(e)
        onsets, vowels, codas, cmudict_bkwd = init(vowel_list)
    mylist = generate_list(onsets, vowels, codas, cmudict_bkwd,
                           numsyl, numwords, firststress,
                           onsetre, vowelre, codare,
                           includesylbreaks, norhyme, stressrhyme)
    if outfilename != '':
        with open(outfilename, 'w') as outfile:
            for nonword in mylist:
                outfile.write(nonword+'\n')
    else:
        for nonword in mylist:
            print(''.join(nonword))
