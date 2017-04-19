from node import Node
import math
import copy

debug = False
printer = False

def mode(examples):
  values = list(set([example['Class'] for example in examples]))
  counts = [0] * len(values)

  for example in examples:
    for i in range(0, len(values)):
      if example['Class'] == values[i]:
        counts[i] += 1
  index = counts.index(max(counts))
  return values[index]


def clean(examples):
  clean_examples = list()
  attributes_unique_values = {}
  # grab all the unique values for each attribute 
  for attribute in examples[0].keys():
      values = [example[attribute] for example in examples]
      unique_values = list(set(values))
      if '?' in unique_values:
        unique_values.remove('?')
        attributes_unique_values[attribute] = attributes_unique_values

  # Scan over all the data, and correct missing values 
  for example in examples:
    for attribute, value in example.iteritems():
      if value == '?':
        example[attribute] = find_value(examples, attribute, example['Class'], attributes_unique_values[attribute])

  return examples

def find_value(examples, attribute, classification, values):
  data = {}
  max_count = -1
  max_attribute_value = None

  for example in examples:
    if example['Class'] == classification:
      curr_value = example.get(attribute)
      if curr_value != '?':
        if curr_value in data.keys():
          data[curr_value] += 1
        else:
          data[curr_value] = 1

  for attribute_value, count in data.iteritems():
    if count > max_count:
      max_count = count
      max_attribute_value = attribute_value

  return max_attribute_value

def get_branches(examples, best_attribute):

  values = [example[best_attribute] for example in examples]
  unique_values = list(set(values))

  branches = [[] for i in range(0, len(unique_values))]

  for example in examples:
    value = example[best_attribute]
    
    for i in range(0, len(unique_values)):
      if value == unique_values[i]:
        branches[i].append(example)
  return branches

# classification_data - list of republicans and democrats
# return entropy on the data
def find_entropy(classification_data):
  total = len(classification_data)
  pos = len([i for i, x in enumerate(classification_data) if x == classification_data[0]])
  neg = total - pos
  try: 
    return -(float(pos)/float(total))*math.log((float(pos)/float(total)),2) - (float(neg)/float(total))*math.log((float(neg)/float(total)),2)
  except ValueError as e:
    # if we get here all the values are either all positive or all negative and the equation equates to 0
    if printer:
      print "No variation -- setting entropy to zero for pure data set"
    return 0 #set is pure 


# given an attribute, compute its gain
def find_information_gain(attribute, examples, total_entropy):
  # will either be 'y' or 'n' with our data set
  
  values = [example[attribute] for example in examples]
  unique_values = list(set(values))
  
  classification_data_sets = [[] for i in range(0, len(unique_values))]

  for example in examples:
    attribute_value = example[attribute]

    for i in range(0, len(unique_values)):
      if attribute_value == unique_values[i]:
        classification_data_sets[i].append(example['Class'])

  weights = [float(len(classification_data_sets[i]))/float((len(examples))) for i in range(0, len(classification_data_sets))]

  for data_set in classification_data_sets:
    if len(data_set) == 0:
      return 0 #we have noise

  entropies = [find_entropy(classification_data_sets[i]) for i in range(0, len(classification_data_sets))]    

  return_entropy = total_entropy
  for i, val in enumerate(entropies):
    return_entropy -= weights[i]*val

  return return_entropy


# loop through attributes, find attribute with highest information gain and return it
def find_best_attribute(examples):
  attributes = examples[0].keys()
  # removes key: Class as it is not an attribute
  attributes.remove('Class')

  best_attribute = None
  max_gain = 0
  classification_data = [example['Class'] for example in examples]
  total_entropy = find_entropy(classification_data)

  for attribute in attributes:
    gain = find_information_gain(attribute, examples, total_entropy)
    if gain > max_gain:
      max_gain = gain
      best_attribute = attribute
  return best_attribute


# return False if not homogenous
# else return True
def is_homogenous(examples):
  base_class = examples[0]['Class']
  for example in examples:
    if example['Class'] != base_class:
      return False
  return True


def find_classifiers(examples):
  return list(set([example['Class'] for example in examples]))


def ID3(examples, default):
  examples_clean = clean(examples)
  return _ID3(examples, default)

def _ID3(examples, default):
  '''
  Takes in an array of examples, and returns a tree (an instance of Node) 
  trained on the examples.  Each example is a dictionary of attribute:value pairs,
  and the target class variable is a special attribute with the name "Class".
  Any missing attributes are denoted with a value of "?"
  '''

  # create root node
  root_node = Node()
  root_node.classifiers = find_classifiers(examples) 


  # check if all classications are the same
  if is_homogenous(examples):
    root_node.label = examples[0]['Class']
    return root_node
  # if no more attributes to split on, set the label or root_node to default
  elif len(examples[0]) == 1:

    root_node.label = default
    return root_node
  else:
    best_attribute = find_best_attribute(examples)
    if best_attribute is None:
      root_node.label = default
      return root_node
    root_node.label = best_attribute

    root_node.branches = get_branches(examples, best_attribute)

    for branch in root_node.branches:
      mode_branch = mode(branch)
      if len(branch) == 0:
        leaf_node = Node()
        leaf_node.label = mode_branch

        if len(root_node.children) == 0:
          root_node.children[0] = leaf_node
        else:
          keys = root_node.children.keys()
          num_keys = len(root_node.children) - 1
          index = keys[num_keys]+1

          root_node.children[index] = leaf_node
      else:

        if len(root_node.children) == 0: 
          root_node.children[0] = _ID3(branch, mode_branch)
        else:
          keys = root_node.children.keys()
          num_keys = len(root_node.children) - 1
          index = keys[num_keys]+1

          root_node.children[index] = _ID3(branch, mode_branch)
    
    return root_node


def _prune(node, prune_label, examples):
  node_list = [node]
  root_node = node

  while len(node_list) > 0:
    curr_node = node_list[0]
    if curr_node.label == prune_label:
      total_examples = []
      for branch in curr_node.branches:
        for example in branch:
          total_examples.append(example['Class'])

      values = list(set(total_examples))
      max_count = total_examples.count(values[0])
      mode_class = values[0]

      for value in values:
        if total_examples.count(value) > max_count:
          max_count = total_examples.count(value)
          mode_class = value
      curr_node.label = mode_class
      curr_node.children = {}
      return root_node 

    for key in curr_node.children.keys():
      if key in curr_node.children:
        node_list.append(curr_node.children[key])

    node_list.pop(0)

  return root_node


def find_max_prune_gain(pruning_scores_dict):
  keys = pruning_scores_dict.keys()
  max_gain = pruning_scores_dict[keys[0]]
  return_key = keys[0]

  for key in keys:
    if pruning_scores_dict[key] > max_gain:
      max_gain = pruning_scores_dict[key]
      return_key = key

  return return_key, max_gain


def get_prune_scores(node, examples):
  scores = {}
  node_list = [node]
  root_node = node
  while len(node_list) > 0:
    prune_node = node_list[0]
    if prune_node.is_leaf():
      node_list.pop(0)
      continue
    scores[prune_node.label] = test(_prune(copy.deepcopy(root_node), prune_node.label, examples), examples)
    
    for key in prune_node.children.keys():
      if key in prune_node.children:
        node_list.append(prune_node.children[key])
    node_list.pop(0)

  return scores



# dictionary of {node.label: pruning score }
# 1. we get the pruning scores of each node
# 2. real tree --> prune node with max(prune_score) given prune_score > base_score
# 3. update all scores
# 4. stop when max(prune_scores) < base_score 
##
# You need a validation set. The basic idea is: try to prune each node 
# (by setting the pruned node to the mode of all examples under that node). 
# After pruning, if the validation accuracy increase, keep the pruning, otherwise undo the pruning.
def prune(node, examples):
  '''
  Takes in a trained tree and a validation set of examples.  Prunes nodes in order
  to improve accuracy on the validation data; the precise pruning strategy is up to you.
  '''
  prune = True
  node_list = [node]
  visited = []
  root_node = node
  while prune and len(node_list) > 0:
    curr_node = node_list[0]    
    base_acc = test(root_node, examples)

    if curr_node.is_leaf() or curr_node.label in visited:
      if curr_node in visited:
         for key in curr_node.children.keys():
          if key in curr_node.children and not curr_node.children[key].label in visited:
            node_list.append(curr_node.children[key])

      node_list.pop(0)
      continue

    visited.append(curr_node.label)
    scores = get_prune_scores(curr_node, examples)
    max_score_label, max_score = find_max_prune_gain(scores)

    if max_score < base_acc:
      prune = False
      break

    root_node = _prune(node, max_score_label, examples)
    
    print_list = [node]
    while len(print_list) > 0:
      curr_node = print_list[0]
      for key in curr_node.children.keys():
        if key in curr_node.children:
          print_list.append(curr_node.children[key])
      print_list.pop(0)

    node_list = [root_node]

  return root_node


def test(node, examples):
  '''
  Takes in a trained tree and a test set of examples.  Returns the accuracy (fraction
  of examples the tree classifies correctly).
  '''
  count = 0
  for example in examples:
    if example['Class'] == evaluate(node, example):
      count += 1

  return float(count)/float(len(examples))


def evaluate(node, example):
  '''
  Takes in a tree and one example.  Returns the Class value that the tree
  assigns to the example.
  '''
  while node.children:
    attribute = node.label
    if example[attribute] == node.branches[0][0][attribute]:
      node = node.children[0]
    else:
      node = node.children[1]
  return node.label



#
#
# TEST CASES 
#
#
def ID3_test():
  from parse import parse
  data = parse('house_votes_84.data')
  tree = ID3(data, 'Republican')
  print tree.label
  print "Passed test: ID3_test()\n"

def find_entropy_test():
  data = ['Republican', 'Democrat', 'Democrat', 'Democrat', 'Democrat', 'Democrat', 'Republican', 'Republican']
  val = -(float(3)/float(8))*(math.log((float(3)/float(8)),2)) - (float(5)/float(8))*(math.log((float(5)/float(8)),2))
  assert_val = find_entropy(data)
  assert(assert_val== val)
  print "Passed test: test_find_entropy()\n"

def find_best_attribute_test():
  attributes = [{'handicapped-infants': 'n', 'export-administration-act-south-africa': 'y', 'superfund-right-to-sue': 'y', 'education-spending': 'y', 'duty-free-exports': 'n', 'aid-to-nicaraguan-contras': 'n', 'immigration': 'y', 'physician-fee-freeze': 'y', 'el-salvador-aid': 'y', 'religious-groups-in-schools': 'y', 'mx-missile': 'n', 'synfuels-corporation-cutback': '?', 'anti-satellite-test-ban': 'n', 'water-project-cost-sharing': 'y', 'crime': 'y', 'adoption-of-the-budget-resolution': 'n', 'Class': 'republican'}, 
                {'handicapped-infants': 'n', 'export-administration-act-south-africa': '?', 'superfund-right-to-sue': 'y', 'education-spending': 'y', 'duty-free-exports': 'n', 'aid-to-nicaraguan-contras': 'n', 'immigration': 'n', 'physician-fee-freeze': 'y', 'el-salvador-aid': 'y', 'religious-groups-in-schools': 'y', 'mx-missile': 'n', 'synfuels-corporation-cutback': 'n', 'anti-satellite-test-ban': 'n', 'water-project-cost-sharing': 'y', 'crime': 'y', 'adoption-of-the-budget-resolution': 'n', 'Class': 'republican'}, 
                {'handicapped-infants': '?', 'export-administration-act-south-africa': 'n', 'superfund-right-to-sue': 'y', 'education-spending': 'n', 'duty-free-exports': 'n', 'aid-to-nicaraguan-contras': 'n', 'immigration': 'n', 'physician-fee-freeze': '?', 'el-salvador-aid': 'y', 'religious-groups-in-schools': 'y', 'mx-missile': 'n', 'synfuels-corporation-cutback': 'y', 'anti-satellite-test-ban': 'n', 'water-project-cost-sharing': 'y', 'crime': 'y', 'adoption-of-the-budget-resolution': 'y', 'Class': 'democrat'}, 
                {'handicapped-infants': 'n', 'export-administration-act-south-africa': 'y', 'superfund-right-to-sue': 'y', 'education-spending': 'n', 'duty-free-exports': 'n', 'aid-to-nicaraguan-contras': 'n', 'immigration': 'n', 'physician-fee-freeze': 'n', 'el-salvador-aid': '?', 'religious-groups-in-schools': 'y', 'mx-missile': 'n', 'synfuels-corporation-cutback': 'y', 'anti-satellite-test-ban': 'n', 'water-project-cost-sharing': 'y', 'crime': 'n', 'adoption-of-the-budget-resolution': 'y', 'Class': 'democrat'}, 
                {'handicapped-infants': 'y', 'export-administration-act-south-africa': 'y', 'superfund-right-to-sue': 'y', 'education-spending': '?', 'duty-free-exports': 'y', 'aid-to-nicaraguan-contras': 'n', 'immigration': 'n', 'physician-fee-freeze': 'n', 'el-salvador-aid': 'y', 'religious-groups-in-schools': 'y', 'mx-missile': 'n', 'synfuels-corporation-cutback': 'y', 'anti-satellite-test-ban': 'n', 'water-project-cost-sharing': 'y', 'crime': 'y', 'adoption-of-the-budget-resolution': 'y', 'Class': 'democrat'}, 
                {'handicapped-infants': 'n', 'export-administration-act-south-africa': 'y', 'superfund-right-to-sue': 'y', 'education-spending': 'n', 'duty-free-exports': 'y', 'aid-to-nicaraguan-contras': 'n', 'immigration': 'n', 'physician-fee-freeze': 'n', 'el-salvador-aid': 'y', 'religious-groups-in-schools': 'y', 'mx-missile': 'n', 'synfuels-corporation-cutback': 'n', 'anti-satellite-test-ban': 'n', 'water-project-cost-sharing': 'y', 'crime': 'y', 'adoption-of-the-budget-resolution': 'y', 'Class': 'democrat'}, 
                {'handicapped-infants': 'n', 'export-administration-act-south-africa': 'y', 'superfund-right-to-sue': '?', 'education-spending': 'n', 'duty-free-exports': 'y', 'aid-to-nicaraguan-contras': 'n', 'immigration': 'n', 'physician-fee-freeze': 'y', 'el-salvador-aid': 'y', 'religious-groups-in-schools': 'y', 'mx-missile': 'n', 'synfuels-corporation-cutback': 'n', 'anti-satellite-test-ban': 'n', 'water-project-cost-sharing': 'y', 'crime': 'y', 'adoption-of-the-budget-resolution': 'y', 'Class': 'democrat'}, 
                {'handicapped-infants': 'n', 'export-administration-act-south-africa': 'y', 'superfund-right-to-sue': 'y', 'education-spending': 'n', 'duty-free-exports': '?', 'aid-to-nicaraguan-contras': 'n', 'immigration': 'n', 'physician-fee-freeze': 'y', 'el-salvador-aid': 'y', 'religious-groups-in-schools': 'y', 'mx-missile': 'n', 'synfuels-corporation-cutback': 'n', 'anti-satellite-test-ban': 'n', 'water-project-cost-sharing': 'y', 'crime': 'y', 'adoption-of-the-budget-resolution': 'n', 'Class': 'republican'}, 
                {'handicapped-infants': 'n', 'export-administration-act-south-africa': 'y', 'superfund-right-to-sue': 'y', 'education-spending': 'y', 'duty-free-exports': 'n', 'aid-to-nicaraguan-contras': 'n', 'immigration': 'n', 'physician-fee-freeze': 'y', 'el-salvador-aid': 'y', 'religious-groups-in-schools': 'y', 'mx-missile': 'n', 'synfuels-corporation-cutback': 'n', 'anti-satellite-test-ban': 'n', 'water-project-cost-sharing': 'y', 'crime': 'y', 'adoption-of-the-budget-resolution': 'n', 'Class': 'republican'}, 
                {'handicapped-infants': 'y', 'export-administration-act-south-africa': '?', 'superfund-right-to-sue': 'n', 'education-spending': 'n', 'duty-free-exports': '?', 'aid-to-nicaraguan-contras': 'n', 'immigration': 'n', 'physician-fee-freeze': 'n', 'el-salvador-aid': 'n', 'religious-groups-in-schools': 'n', 'mx-missile': 'y', 'synfuels-corporation-cutback': 'n', 'anti-satellite-test-ban': 'y', 'water-project-cost-sharing': 'y', 'crime': 'n', 'adoption-of-the-budget-resolution': 'y', 'Class': 'democrat'}, 
                {'handicapped-infants': 'n', 'export-administration-act-south-africa': 'n', 'superfund-right-to-sue': 'y', 'education-spending': '?', 'duty-free-exports': 'n', 'aid-to-nicaraguan-contras': 'n', 'immigration': 'n', 'physician-fee-freeze': 'y', 'el-salvador-aid': 'y', 'religious-groups-in-schools': 'n', 'mx-missile': 'n', 'synfuels-corporation-cutback': '?', 'anti-satellite-test-ban': 'n', 'water-project-cost-sharing': 'y', 'crime': 'y', 'adoption-of-the-budget-resolution': 'n', 'Class': 'republican'}, 
                {'handicapped-infants': 'n', 'export-administration-act-south-africa': '?', 'superfund-right-to-sue': 'y', 'education-spending': '?', 'duty-free-exports': '?', 'aid-to-nicaraguan-contras': 'n', 'immigration': 'n', 'physician-fee-freeze': 'y', 'el-salvador-aid': 'y', 'religious-groups-in-schools': 'y', 'mx-missile': 'n', 'synfuels-corporation-cutback': 'y', 'anti-satellite-test-ban': 'n', 'water-project-cost-sharing': 'y', 'crime': 'y', 'adoption-of-the-budget-resolution': 'n', 'Class': 'republican'}, 
                {'handicapped-infants': 'n', 'export-administration-act-south-africa': '?', 'superfund-right-to-sue': 'y', 'education-spending': 'n', 'duty-free-exports': '?', 'aid-to-nicaraguan-contras': 'n', 'immigration': 'n', 'physician-fee-freeze': 'n', 'el-salvador-aid': 'n', 'religious-groups-in-schools': 'n', 'mx-missile': 'y', 'synfuels-corporation-cutback': 'n', 'anti-satellite-test-ban': 'y', 'water-project-cost-sharing': 'y', 'crime': 'n', 'adoption-of-the-budget-resolution': 'y', 'Class': 'democrat'}, 
                {'handicapped-infants': 'y', 'export-administration-act-south-africa': '?', 'superfund-right-to-sue': 'n', 'education-spending': '?', 'duty-free-exports': 'y', 'aid-to-nicaraguan-contras': 'n', 'immigration': 'y', 'physician-fee-freeze': 'n', 'el-salvador-aid': 'n', 'religious-groups-in-schools': 'y', 'mx-missile': '?', 'synfuels-corporation-cutback': 'y', 'anti-satellite-test-ban': 'y', 'water-project-cost-sharing': 'y', 'crime': 'n', 'adoption-of-the-budget-resolution': 'y', 'Class': 'democrat'}]
  assert(find_best_attribute(attributes) == 'adoption-of-the-budget-resolution')
  print "Passed test: find_best_attribute_test()\n"

# def return_default_test():


if debug:
  find_entropy_test()
  find_best_attribute_test()
  ID3_test()
