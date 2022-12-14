#!/usr/bin/env python
import collections
import json
import math
import os
import re
import sys

from PorterStemmer import PorterStemmer

class IRSystem:

    def __init__(self):
        # For holding the data - initialized in read_data()
        self.titles = []
        self.docs = []
        self.vocab = []
        # For the text pre-processing.
        self.alphanum = re.compile('[^a-zA-Z0-9]')
        self.p = PorterStemmer()


    def get_uniq_words(self):
        uniq = set()
        for doc in self.docs:
            for word in doc:
                uniq.add(word)
        return uniq


    def __read_raw_data(self, dirname):
        print("Stemming Documents...")

        titles = []
        docs = []
        os.mkdir(f'{dirname}/stemmed')
        title_pattern = re.compile('(.*) \d+\.txt')

        # make sure we're only getting the files we actually want
        filenames = []
        for filename in os.listdir(f'{dirname}/raw'):
            if filename.endswith(".txt") and not filename.startswith("."):
                filenames.append(filename)

        for i, filename in enumerate(filenames):
            title = title_pattern.search(filename).group(1)
            print (f"    Doc {i+1} of {len(filenames)}: {title}")
            titles.append(title)
            contents = []
            f = open(f'{dirname}/raw/{filename}', 'r')
            of = open(f'{dirname}/stemmed/{title}.txt', 'w')
            for line in f:
                # make sure everything is lower case
                line = line.lower()
                # split on whitespace
                line = [xx.strip() for xx in line.split()]
                # remove non alphanumeric characters
                line = [self.alphanum.sub('', xx) for xx in line]
                # remove any words that are now empty
                line = [xx for xx in line if xx != '']
                # stem words
                line = [self.p.stem(xx) for xx in line]
                # add to the document's conents
                contents.extend(line)
                if len(line) > 0:
                    of.write(" ".join(line))
                    of.write('\n')
            f.close()
            of.close()
            docs.append(contents)
        return titles, docs


    def __read_stemmed_data(self, dirname):
        print("Already stemmed!")
        titles = []
        docs = []

        # make sure we're only getting the files we actually want
        filenames = []
        for filename in os.listdir(f'{dirname}/stemmed'):
            if filename.endswith(".txt") and not filename.startswith("."):
                filenames.append(filename)

        if len(filenames) != 60:
            msg = "There are not 60 documents in ./data/RiderHaggard/stemmed/\n"
            msg += "Remove ./data/RiderHaggard/stemmed/ directory and re-run."
            raise Exception(msg)

        for i, filename in enumerate(filenames):
            title = filename.split('.')[0]
            titles.append(title)
            contents = []
            f = open(f'{dirname}/stemmed/{filename}', 'r')
            for line in f:
                # split on whitespace
                line = [xx.strip() for xx in line.split()]
                # add to the document's conents
                contents.extend(line)
            f.close()
            docs.append(contents)

        return titles, docs


    def read_data(self, dirname):
        """
        Given the location of the 'data' directory, reads in the documents to
        be indexed.
        """
        # NOTE: We cache stemmed documents for speed
        #       (i.e. write to files in new 'stemmed/' dir).

        print("Reading in documents...")
        # dict mapping file names to list of "words" (tokens)
        filenames = os.listdir(dirname)
        subdirs = os.listdir(dirname)
        if 'stemmed' in subdirs:
            titles, docs = self.__read_stemmed_data(dirname)
        else:
            titles, docs = self.__read_raw_data(dirname)

        # Sort document alphabetically by title to ensure we have the proper
        # document indices when referring to them.
        ordering = [idx for idx, title in sorted(enumerate(titles),
            key = lambda xx : xx[1])]

        self.titles = []
        self.docs = []
        numdocs = len(docs)
        for d in range(numdocs):
            self.titles.append(titles[ordering[d]])
            self.docs.append(docs[ordering[d]])

        # Get the vocabulary.
        self.vocab = [xx for xx in self.get_uniq_words()]


    def compute_tfidf(self):
        print("Calculating tf-idf...")

        self.tfidf = {}
        # -------------------------------------------------------------------
        # TODO: Compute and store TF-IDF values for words and documents.
        #       Right Now it just assigns 0 TF-IDF value for all words and documents.
        #       Recall that you can make use of:
        #         * self.vocab: a list of all distinct (stemmed) words
        #         * self.docs: a list of lists, where the i-th document is
        #                   self.docs[i] => ['word1', 'word2', ..., 'wordN']
        #       NOTE that you probably do *not* want to store a value for every
        #       word-document pair, but rather just for those pairs where a
        #       word actually occurs in the document.
        for word in self.vocab:
            for d in range(len(self.docs)):
                if word not in self.tfidf:
                    self.tfidf[word] = collections.defaultdict(lambda: 0.0)
            
        count = len(self.docs)
        
        for id in range(len(self.docs)):
            for w in self.docs[id]:
                self.tfidf[w][id] += 1.0
            count -= 1
            
        NumOfDocu = float(len(self.docs))
        
        for word in self.tfidf:
            df = float(len(self.tfidf[word]))
            for doc in self.tfidf[word]:
                d = self.tfidf[word][doc]
                idf = math.log(NumOfDocu / df, 10)
                if d>0:
                    self.tfidf[word][doc] = (1.0 + math.log(d,10)) * idf
        # ------------------------------------------------------------------


    def get_tfidf(self, word, document):
        # ------------------------------------------------------------------
        # TODO: Return the tf-idf weigthing for the given word (string) and
        #       document index.
        tfidf = 0.0
        tfidf = self.tfidf[word][document]
        # ------------------------------------------------------------------
        return tfidf


    def get_tfidf_unstemmed(self, word, document):
        """
        This function gets the TF-IDF of an *unstemmed* word in a document.
        Stems the word and then calls get_tfidf. You should *not* need to
        change this interface, but it is necessary for submission.
        """
        word = self.p.stem(word)
        return self.get_tfidf(word, document)


    def index(self):
        """
        Build an index of the documents.
        """
        print("Indexing...")

        # ------------------------------------------------------------------
        # TODO: Create an inverted index. Right Now it just returns empty dictionary.
        #       Granted this may not be a linked list as in a proper
        #       implementation.
        #       Some helpful instance variables:
        #         * self.docs = List of documents
        #         * self.titles = List of titles
        inv_index = {}
        
        for word in self.vocab:
            inv_index[word] = []
        
        for doc_idx in range(0, len(self.docs)):
            title = self.titles[doc_idx]
            for word in self.docs[doc_idx]:
                inv_index[word].append(title)
                
        self.inv_index = inv_index

        # ------------------------------------------------------------------


    def get_posting(self, word):
        """
        Given a word, this returns the list of document indices (sorted) in
        which the word occurs.
        """

        # ------------------------------------------------------------------
        # TODO: return the list of postings for a word. Right Now it just returns empty list.
        posting = set([])
        
        indices = self.inv_index[word]
        
        for doc in indices:
            posting.add(self.titles.index(doc))

        return posting
        # ------------------------------------------------------------------


    def get_posting_unstemmed(self, word):
        """
        Given a word, this *stems* the word and then calls get_posting on the
        stemmed word to get its postings list. You should *not* need to change
        this function. It is needed for submission.
        """
        word = self.p.stem(word)
        return self.get_posting(word)


    def boolean_retrieve(self, query):
        """
        Given a query in the form of a list of *stemmed* words, this returns
        the list of documents in which *all* of those words occur (ie an AND
        query).
        Return an empty list if the query does not return any documents.
        """
        # ------------------------------------------------------------------
        # TODO: Implement Boolean retrieval. You will want to use your
        #       inverted index that you created in index().
        # Right now this just returns all the possible documents!
        title_lst = []
        
        for d in self.titles:
            title_lst.append(d)
        docs_set = set(title_lst)
        
        for stemmed in query:
            inv_index = self.inv_index[stemmed]
            docs_set = docs_set.intersection(set(inv_index))
            
        docs = []
        for t in docs_set:
            docs.append(self.titles.index(t))
            

        # ------------------------------------------------------------------

        return sorted(docs)   # sorted doesn't actually matter


    def rank_retrieve(self, query):
        """
        Given a query (a list of words), return a rank-ordered list of
        documents (by ID) and score for the query.
        Note that the reference solutions use ltc.lnn weighting scheme for computing 
        cosine scores (See lecture slide)
        """
        scores = [0.0 for xx in range(len(self.docs))]
        # ------------------------------------------------------------------
        # TODO: Implement cosine similarity between a document and a list of
        #       query words.

        # Right now, this code simply gets the score by taking the Jaccard
        # similarity between the query and every document.
        wtq_cnt = collections.Counter(query)

        all_doc_counters = {}

        lendocs = {}
        for d, doc in enumerate(self.docs):
            doc_counters = collections.Counter(doc)
            all_doc_counters[d] = doc_counters
            
            lendoc = 0.0
            for w in doc_counters:
                wtdt = self.get_tfidf(w, d)
                lendoc += wtdt * wtdt
            lendocs[d] = lendoc

        for t in wtq_cnt:
            cnt = wtq_cnt[t]

            wtqt = 1.0 + math.log(float(cnt), 10)

            postings = self.get_posting(t) # list of document indices for the word
            for d in postings:
                doc = self.docs[d]

                doccount = all_doc_counters[d][t]
                wtdt = self.get_tfidf(t, d)
                scores[d] += wtdt * wtqt

        for d, doc in enumerate(self.docs):
            lendoc = lendocs[d]
            if lendoc > 0:
                scores[d] = scores[d] / math.sqrt(lendoc)
       

        # ------------------------------------------------------------------

        ranking = [idx for idx, sim in sorted(enumerate(scores),
            key = lambda xx : xx[1], reverse = True)]
        results = []
        for i in range(10):
            results.append((ranking[i], scores[ranking[i]]))
        return results

#--------------------------------------------------------------------------#
# CODE TO UPDATE ENDS HERE                                                 #
#--------------------------------------------------------------------------#


    def process_query(self, query_str):
        """
        Given a query string, process it and return the list of lowercase,
        alphanumeric, stemmed words in the string.
        """
        # make sure everything is lower case
        query = query_str.lower()
        # split on whitespace
        query = query.split()
        # remove non alphanumeric characters
        query = [self.alphanum.sub('', xx) for xx in query]
        # stem words
        query = [self.p.stem(xx) for xx in query]
        return query


    def query_retrieve(self, query_str):
        """
        Given a string, process and then return the list of matching documents
        found by boolean_retrieve().
        """
        query = self.process_query(query_str)
        return self.boolean_retrieve(query)


    def query_rank(self, query_str):
        """
        Given a string, process and then return the list of the top matching
        documents, rank-ordered.
        """
        query = self.process_query(query_str)
        return self.rank_retrieve(query)


def run_tests(irsys):
    print("===== Running tests =====")

    ff = open('./data/queries.txt')
    questions = [xx.strip() for xx in ff.readlines()]
    ff.close()
    ff = open('./data/solutions.txt')
    solutions = [xx.strip() for xx in ff.readlines()]
    ff.close()

    epsilon = 1e-4
    total_points = 0
    score_weight = [0.5, 0.5, 1, 2]
    max_point_in_part = [2.5, 2.5, 5, 10]
    for part in range(4):
        points = 0
        num_correct = 0
        num_total = 0

        prob = questions[part]
        soln = json.loads(solutions[part])

        if part == 0:     # inverted index test
            print("1. Inverted Index Test")
            words = prob.split(", ")
            for i, word in enumerate(words):
                num_total += 1
                posting = irsys.get_posting_unstemmed(word)
                if set(posting) == set(soln[i]):
                    num_correct += 1

        elif part == 1:   # boolean retrieval test
            print("2. Boolean Retrieval Test")
            queries = prob.split(", ")
            for i, query in enumerate(queries):
                num_total += 1
                guess = irsys.query_retrieve(query)
                if set(guess) == set(soln[i]):
                    num_correct += 1

        elif part == 2:   # tfidf test
            print("3. TF-IDF Test")
            queries = prob.split("; ")
            queries = [xx.split(", ") for xx in queries]
            queries = [(xx[0], int(xx[1])) for xx in queries]
            for i, (word, doc) in enumerate(queries):
                num_total += 1
                guess = irsys.get_tfidf_unstemmed(word, doc)
                if guess >= float(soln[i]) - epsilon and \
                        guess <= float(soln[i]) + epsilon:
                    num_correct += 1

        elif part == 3:   # cosine similarity test
            print("4. Cosine Similarity Test")
            queries = prob.split(", ")
            for i, query in enumerate(queries):
                num_total += 1
                ranked = irsys.query_rank(query)
                top_rank = ranked[0]
                if top_rank[0] == soln[i][0]:
                    if top_rank[1] >= float(soln[i][1]) - epsilon and \
                            top_rank[1] <= float(soln[i][1]) + epsilon:
                        num_correct += 1

        feedback = f"{num_correct}/{num_total} Correct. Accuracy: {float(num_correct)/num_total}"
        points = score_weight[part] * num_correct
        max_points = max_point_in_part[part]
        total_points +=points
        print(f"    Score: {points}/{max_points} Feedback: {feedback}")
    print("======= Tests finished =======")
    print(f"    Part 2 Score: {total_points}/{20}")


def main(args):
    irsys = IRSystem()
    irsys.read_data('./data/RiderHaggard')
    irsys.index()
    irsys.compute_tfidf()

    if len(args) == 0:
        run_tests(irsys)
    else:
        query = " ".join(args)
        print(f"Best matching documents to '{query}':")
        results = irsys.query_rank(query)
        for docId, score in results:
            print (f"{irsys.titles[docId]}: {score}")


if __name__ == '__main__':
    args = sys.argv[1:]
    main(args)
