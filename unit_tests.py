import ID3, parse, random

def testID3AndEvaluate():
  data = [dict(a=1, b=0, Class=1), dict(a=1, b=1, Class=1)]
  tree = ID3.ID3(data, 0)
  if tree != None:
    ans = ID3.evaluate(tree, dict(a=1, b=0))
    if ans != 1:
      print "ID3 test failed."
    else:
      print "ID3 test succeeded."
  else:
    print "ID3 test failed -- no tree returned"

def testPruning():
  data = [dict(a=1, b=0, Class=0), dict(a=1, b=1, Class=0), dict(a=0, b=1, Class=1)]
  validationData = [dict(a=1, b=0, Class=0), dict(a=1, b=1, Class=0), dict(a=0, b=0, Class=0), dict(a=0, b=0, Class=0)]
  tree = ID3.ID3(data, 0)
  ID3.prune(tree, validationData)
  if tree != None:
    ans = ID3.evaluate(tree, dict(a=0, b=0))
    if ans != 0:
      print "pruning test failed."
    else:
      print "pruning test succeeded."
  else:
    print "pruning test failed -- no tree returned."

def testPruning_2():
  data = [dict(a=1, b=0, Class=0), dict(a=1, b=1, Class=0), dict(a=0, b=1, Class=1)]
  validationData = [dict(a=1, b=0, Class=0), dict(a=1, b=1, Class=0), dict(a=0, b=0, Class=0), dict(a=0, b=0, Class=0)]
  tree = ID3.ID3(data, 0)
  ID3.prune(tree, validationData)
  if tree != None:
    ans = ID3.evaluate(tree, dict(a=0, b=0))
    if ans != 0:
      print "pruning test failed."
    else:
      print "pruning test succeeded."
  else:
    print "pruning test failed -- no tree returned."


def testID3AndTest():
  trainData = [dict(a=1, b=0, c=0, Class=1), dict(a=1, b=1, c=0, Class=1), 
  dict(a=0, b=0, c=0, Class=0), dict(a=0, b=1, c=0, Class=1)]
  testData = [dict(a=1, b=0, c=1, Class=1), dict(a=1, b=1, c=1, Class=1), 
  dict(a=0, b=0, c=1, Class=0), dict(a=0, b=1, c=1, Class=0)]
  tree = ID3.ID3(trainData, 0)
  fails = 0
  if tree != None:
    acc = ID3.test(tree, trainData)
    if acc == 1.0:
      print "testing on train data succeeded."
    else:
      print "testing on train data failed."
      fails = fails + 1
    acc = ID3.test(tree, testData)
    if acc == 0.75:
      print "testing on test data succeeded."
    else:
      print "testing on test data failed."
      fails = fails + 1
    if fails > 0:
      print "Failures: ", fails
    else:
      print "testID3AndTest succeeded."
  else:
    print "testID3andTest failed -- no tree returned."

# inFile - string location of the house data file
def testPruningOnHouseData(inFile):
  withPruning = []
  withoutPruning = []
  data = parse.parse(inFile)
  for i in range(100):
    random.shuffle(data)
    train = data[:len(data)/2]
    valid = data[len(data)/2:3*len(data)/4]
    test = data[3*len(data)/4:]
  
    tree = ID3.ID3(train, 'democrat')
    acc = ID3.test(tree, train)
    print "training accuracy: ",acc
    acc = ID3.test(tree, valid)
    print "validation accuracy: ",acc
    acc = ID3.test(tree, test)
    print "test accuracy: ",acc
  
    ID3.prune(tree, valid)
    acc = ID3.test(tree, train)
    print "pruned tree train accuracy: ",acc
    acc = ID3.test(tree, valid)
    print "pruned tree validation accuracy: ",acc
    acc = ID3.test(tree, test)
    print "pruned tree test accuracy: ",acc
    withPruning.append(acc)
    tree = ID3.ID3(train+valid, 'democrat')
    acc = ID3.test(tree, test)
    print "no pruning test accuracy: ",acc
    withoutPruning.append(acc)
  print withPruning
  print withoutPruning
  print "average with pruning",sum(withPruning)/len(withPruning)," without: ",sum(withoutPruning)/len(withoutPruning)


def plotter(inFile):
  import matplotlib.pyplot as plt
  x_values = []
  y_values = []
  y_values_prune =[]

  training_set_sizes = [10+14*i for i in range(21)]

  data = parse.parse(inFile)
  for training_set in training_set_sizes:
    x = []
    y = []
    y_prune = []
    print "PRINTING TS,", training_set
    for i in range(100):
      random.shuffle(data)
      train = data[:training_set]
      valid = data[training_set:training_set  + training_set / 4]
      test = data[training_set  + training_set/ 4:]

      tree = ID3.ID3(train, 'democrat')
      acc = ID3.test(tree, test)
      x.append(training_set)
      y.append(acc)

      ID3.prune(tree, valid)
      acc_prune = ID3.test(tree, train) 
      y_prune.append(acc_prune)


    x_values.append(sum(x)/len(x))
    y_values.append(sum(y)/len(y))
    y_values_prune.append(sum(y_prune)/len(y_prune))

  plt.plot(x_values, y_values, 'r--', x_values, y_values_prune, 'b--')
  plt.show()





# testID3AndTest()
# testID3AndEvaluate()
testPruning()
# testPruningOnHouseData('house_votes_84.data')
# testPruning_2()

# plotter('house_votes_84.data')


  