class Node:
    def __init__(self):
    	self.branches = [] 
        self.label = None
        self.children = {}
       	self.classifiers = None


    def is_leaf(self):
    	return self.label in self.classifiers
