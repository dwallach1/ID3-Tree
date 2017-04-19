# ID3-Tree

For this project, I implemented a decision tree that parses data in the format of an example where each example is
a dictionary, with attributes stored as key:value pairs. The target output is stored as an attribute with the key "Class". 

This program takes in a file of entries (look at house_votes_84.data) in this format and builds a decision tree. It then can be pruned for improvements in accuracy by accounting for the factor of overfitting. 

Each node of the tree is represented by the class in node.py, the ID3 and prune algorithms are found in ID3.py along with the helper functions. 


# Custom Use 
You can refer to unit_tests.py to see how to build, train and evaluate an ID3 tree built by this program and then build a porgram that uses this ID3 tree for your specific needs


# Pruning & Overfitting 
The improvement by using pruneing can be shown by this picture: 
![alt tag](https://github.com/dwallach1/ID3-Tree/blob/master/Screen%20Shot%202017-04-13%20at%205.50.08%20PM.png)

