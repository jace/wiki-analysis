aux_en = dict(
    actQualia = set([
        'easily', 'quietly', 'earlier', 'strictly', 'constantly', 'loosely',
        'quickly', 'early', 'difficulty', 'loudly', 'slowly', 'closely',
        'continually', 'clearly',
        ]),
    adjectives = set([
        'gone', 'unusual', 'full', 'false', 'like', 'unlike', 'far', 'indeed',
        'sole', 'able', 'given', 'simple', 'near', 'done', 'obvious', 'seen',
        'apparent', 'true', 'final', 'empty', 'usual',
        ]),
    adverbs = set([
        'likely', 'simply', 'unlikely', 'incidentally', 'actually',
        'apparently', 'rarely', 'wholly', 'ably', 'till', 'finally', 'falsely',
        'differently', 'until', 'too', 'partly', 'truly', 'extremely', 'fully',
        'obviously', 'usually', 'unusually', 'solely', 'familiarly',
        'unfamiliarly',
        ]),
    appendages = set([
        'em', 'eaux', 'non', 'en', 'd', 'pre', 'ed', 'ies', 'al', 's', 'un',
        'ent', 'eing', 'aux', 'post', 'ing', 'ied', 'es',
        ]),
    articles = set([
        'a', 'the', 'an',
        ]),
    connectives = set([
        'and', 'because', 'thus', 'if', 'even', 'nonetheless', 'whereas',
        'also', 'therefore', 'neither', 'then', 'unless', 'thereby', 'though',
        'however', 'but', 'not', 'nor', 'whereby', 'nevertheless', 'no', 'so',
        'either', 'or', 'otherwise',
        ]),
    copulas = set([
        'be', 'would', 'shall', 'may', 'was', 'is', 'am', 'been', 'should',
        'will', 'can', 'cannot', 'are', 'were', 'might', 'could', 'must',
        ]),
    indexicals = set([
        'somehow', 'whatever', 'these', 'what', 'somewhere', 'there', 'when',
        'how', 'which', 'that', 'who', 'overall', 'here', 'whichever',
        'somewhat', 'such', 'why', 'those', 'this', 'wherever', 'whenever',
        'while', 'where',
        ]),
    locatives = set([
        'right', 'just', 'over', 'down', 'middle', 'before', 'outsides',
        'next', 'insides', 'outside', 'above', 'under', 'out', 'into',
        'after', 'sides', 'inside', 'up', 'against', 'below', 'side', 'left',
        ]),
    nouns = set([
        'saying', 'serving', 'seeming', 'seeing', 'being', 'existing',
        'obliging', 'existence', 'living', 'tending', 'depending', 'ways',
        'removing', 'intending', 'detailing', 'same', 'doing', 'going',
        'asking', 'way', 'remaining', 'indicating', 'opening', 'different',
        'part', 'varying', 'trying', 'regarding', 'places', 'getting',
        'enabling', 'involving', 'place', 'closing', 'whole', 'having',
        ]),
    personalQualia = set([
        'own', 'her', 'theirs', 'mine', 'singly', 'yours', 'their', 'single',
        'his', 'together', 'my', 'our', 'alone', 'ours', 'hers', 'your',
        ]),
    personalQuanta = set([
        'me', 'we', 'himself', 'they', 'i', 'he', 'them', 'us', 'ourselves',
        'anothers', 'sakes', 'other', 'she', 'another', 'others', 'you',
        'themselves', 'herself', 'him', 'sake',
        ]),
    prepositions = set([
        'among', 'within', 'as', 'through', 'at', 'in', 'throughout', 'from',
        'for', 'perhaps', 'fro', 'than', 'to', 'between', 'upon', 'quite',
        'with', 'by', 'on', 'about', 'off', 'whether', 'of', 'without',
        ]),
    quantifiers = set([
        'oftentimes', 'all', 'never', 'often', 'always', 'sometimes', 'some',
        'one', 'each', 'few', 'only', 'much', 'every', 'many', 'more', 'ever',
        'any', 'once',
        ]),
    temporals = set([
        'begins', 'again', 'begin', 'finish', 'end', 'finishes', 'ended',
        'started', 'starts', 'began', 'still', 'ends', 'start', 'finished',
        'became', 'becomes', 'become', 'now', 'once', 'yet', 'ago',
        ]),
    thingQualia = set([
        'constant', 'less', 'highly', 'high', 'close', 'seem', 'best',
        'seemed', 'slow', 'seems', 'least', 'better', 'strict', 'low', 'easy',
        'higher', 'lowest', 'badly', 'good', 'worse', 'loose', 'seemingly',
        'most', 'worst', 'difficult', 'continual', 'highest', 'seemly',
        'lower', 'clear', 'quiet', 'bad', 'quick', 'more', 'loud',
        ]),
    thingQuanta = set([
        'thing', 'things', 'it', 'everything', 'itself', 'something', 'item',
        'items', 'nothing', 'its',
        ]),
    verbs = set([
        'vary', 'results', 'bring', 'go', 'seemed', 'depend', 'depended',
        'regarded', 'had', 'intends', 'has', 'happened', 'do', 'closed', 'get',
        'continues', 'feels', 'continued', 'like', 'did', 'serves', 'leave',
        'continue', 'served', 'went', 'says', 'exists', 'obliged', 'tended',
        'see', 'result', 'close', 'happen', 'obliges', 'happens', 'closes',
        'said', 'opened', 'tend', 'does', 'goes', 'tends', 'got', 'intending',
        'put', 'come', 'puts', 'involved', 'leaves', 'allows', 'makes',
        'asked', 'involves', 'liked', 'hears', 'feel', 'seems', 'brought',
        'ask', 'likes', 'gave', 'open', 'existed', 'takes', 'asks', 'remains',
        'give', 'indicate', 'live', 'call', 'taken', 'opens', 'gives', 'lived',
        'brings', 'regard', 'serve', 'took', 'resulted', 'regards', 'lives',
        'removed', 'made', 'heard', 'enabled', 'depends', 'remain', 'enables',
        'called', 'detailed', 'sees', 'indicated', 'remained', 'remove',
        'involve', 'indicates', 'say', 'enable', 'exist', 'have', 'allowed',
        'take', 'seem', 'saw', 'varied', 'make', 'detail', 'varies',
        'details', 'gets', 'intend', 'tried', 'oblige', 'removes', 'felt',
        'tries', 'calls', 'try', 'comes', 'allow', 'hear', 'came'
        ]),
    )
