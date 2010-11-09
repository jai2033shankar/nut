#!/usr/bin/python
#
# Author: Peter Prettenhofer <peter.prettenhofer@gmail.com>
#
# License: BSD Style
"""
conll
=====

This package contains corpus reader for a number
of CoNLL shared tasks. 


"""

import codecs
import os
from itertools import izip, count

class Conll03Reader(object):
    """Corpus reader for CoNLL 2003 shared task on
    Named Entity Recognition.

    Parameters
    ----------
    path : str
        The path to the iob file.
    iob : int, 1 or 2 or 3
        The iob encoding to be used. 
    """
    def __init__(self, path, iob=1):
	self._path = os.path.normpath(path)
	fname = os.path.split(self._path)[-1]
	self._select = [0,1,2]
	if fname.startswith("de"):
	    self._select = [0,2,3,1]
	if iob not in [0,1,2]:
	    raise ValueError, "iob must be either 0, 1, or 2."
	self.iob = iob
	self.raw = False
	if fname.endswith("raw"):
	    self.raw = True
	
    def __iter__(self):
        """Iterate over the corpus; i.e. tokens. 
        """
        fd = codecs.open(self._path, mode="rt", encoding="latin1")
	begin = True
        try:
	    for line in fd:
                line = line.encode("utf8")
		line = line.rstrip()
		if line.startswith("-DOCSTART-"):
		    yield "</doc>"
		    yield "<doc>"
		    begin = True
		elif line == "":
		    # new sentence - emit sentence end and begin
		    yield "</s>"
		    yield "<s>"
		    begin = True
		else:
		    fields = line.split()
		    if self.raw:
			fields.append("Unk")
		    # emit (token, tag) tuple
		    tag = fields[-1]
		    token = fields[:-1]
                    token = [token[i] for i in self._select]
                    
		    if self.iob == 2 and tag.startswith("I") and begin == True:
			tag = "B"+tag[1:]
			begin = False
		    if tag == "O":
			begin = True
                    if self.iob == 0 and tag != "O":
                        tag = tag.split("-")[1]
		    yield (token, tag)
	    yield "</doc>"
	    yield "<doc>"
        finally:
            fd.close()
	    
    def sents(self):
        """Iterate over sentences.

        Yields
        ------
        tuple (token, tag) where token is a tuple (term, lemma?, pos, chunk). 
        """
	buf = []
	for token in self:
	    if token == "</s>":
		if len(buf) > 0:
		    yield buf
	    elif token == "<s>":
		buf = []
	    else:
		if token != "<doc>" and token != "</doc>":
		    buf.append(token)

    def docs(self):
        """Iterate over documents.

        Yields
        ------
        list of tuples (token, tag)
        where token is a tuple (term, lemma?, pos, chunk). 
        """
	buf = []
	for token in self:
	    if token == "</doc>":
		if len(buf) != 0:
		    yield buf[1:-1] # trim leading and trailing sent boundaries.
	    elif token == "<doc>":
		buf = []
	    else:
		buf.append(token)

    def write_sent_predictions(self, tagger, fd, raw=False):
        """Write predictions of `tagger` to file `fd` in a format
        suited for conlleval.
        
        Parameters
        ----------
        tagger : Tagger
            The tagger used for prediction.
        fd : file
            A file descriptor to which the predictions shold be written.
        raw : bool
            Raw predictions or iob encoding (see conlleval).
        """
        for i, sent, pred in izip(count(), self.sents(),
                                  tagger.batch_tag(reader.sents())):
            fd.write("\n")
            for (token, tag), ptag in izip(sent, pred):
                if raw:
                    tag = tag.split("-")[-1]
                    ptag = ptag.split("-")[-1]
                fd.write("%s %s %s\n" % (" ".join(token), tag, ptag))
        print "%d sentences tagged. " % i


def entities(doc):
    entities = []
    buf = []
    notentity = set(["O","<s>","</s>"])
    for i,token in enumerate(doc):
	tag = token[-1] if isinstance(token, tuple) else token
	print i,tag
	if tag in notentity:
	    if len(buf) > 0:
		entities.append(" ".join(buf))
		buf = []
	else:
	    if tag.startswith("B"):
		if len(buf) > 0:
		    entities.append(" ".join(buf))
		    buf = []
	    print "appending ", token[0][0]
	    buf.append(token[0][0])
    return entities

