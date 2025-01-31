## Self-Organizing Map

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Dataset taken from the UCI Machine Learning Repository
# Statlog (Australian Credit Approval) Data Set
dataset = pd.read_csv("Credit_Card_Applications.csv")

# Split the dataset
#
# Note that we're not doing this in order to create a supervised learning model
# (we're not trying to predict 0 or 1). We're only doing it so we can
# distinguish between the customers whose application was approved and those
# who weren't.
X = dataset.iloc[:, :-1].values
y = dataset.iloc[:, -1].values

# Feature scaling (normalization, i.e. get all features between 0 and 1)
#
# fit() only stores the normalized values in memory without modifying X
# transform() will actually modify X to be the normalized values.
# fit_transform() does both of these things
from sklearn.preprocessing import MinMaxScaler
sc = MinMaxScaler(feature_range = (0, 1))
X = sc.fit_transform(X)

# Train the SOM
# A sklearn implementation of a SOM doesn't currently exist, so we need an
# implementation from another developer
from minisom import MiniSom

# The MiniSom object is the self-organizing map itself.
#
# x, y : The dimensions of the map/grid.
# input_len : The # of features in X.
# sigma : The radius of the different neighborhoods in the grid.
# learning_rate : Decides by how much the weights are updated during each
#                 iteration.
# decay_function : This can be used to improve the model's convergence.
som = MiniSom(x = 10, y = 10, input_len = 15, sigma = 1.0, learning_rate = 0.5)

# We need to initialize the weights before training the SOM on X
som.random_weights_init(X)

# Train the SOM on X (not X and y) because we're doing unsupervised learning
# (the dependent variable is not considered).
# This is step 4 of 9
#
# num_iteration : The number of times we want to repeat steps 4 to 9.
som.train_random(data = X, num_iteration = 100)

# Visualize the results
# We will color the winning nodes in such a way that the larger the MID is, the
# closer to white the color will be. We will need to plot the self-organizing
# map somewhat from scratch (we can't use matplotlib since this is a very
# specific type of plot).
from pylab import bone, pcolor, colorbar, plot, show

# Initialize the figure (the window that will contain the map)
bone()

# Put the various winning nodes on the map
#
# We'll do this by putting on the map the information of the MID (Mean
# Interneuron Distance) for all the winning nodes that the SOM identified. We
# will not add the values of all these MIDs, but instead we will use colors
# (different colors will correspond to different range values of the MIDs). The
# distance_map() method of the SOM object will return all of the MIDs in one
# matrix.
pcolor(som.distance_map().T)

# We want to add a legend so that we can see what the different colors on the
# map represent. The white colors on the map correspond to the fraudulent cases
# (because this color represents high MID values).
colorbar()

# Red circles = customers who didn't get approval
# Green squares = customers who got approval
#
# We create a vector of two elements, which corresponds to the two markers we
# want.
markers = ['o', 's']
colors = ['r', 'g']

# Loop over all customers, and for each customer, we will get the winning node,
# and depending on whether or not the customer got approval, we will color this
# winning node by a red circle or a green square.
#
# i = different values of all the indexes of our customer database
# x = different vectors of customers (i.e. rows in the dataset)
for i, x in enumerate(X):
    # Get the winning node for the current customer x
    w = som.winner(x)
    
    # On this winning node, we will plot the marker.
    #
    # w[0] and w[1] are the x- and y-coordinates of the winning node,
    # respectively. More specifically, these are the coordinate of the lower
    # left corner of the square. We want to put these coordinates at the center
    # of the square, so we need to add 0.5 to each coordinate to put it in the
    # middle of the horizontal and vertical base of the square.
    #
    # We also need to know whether to put a red circle or green square.
    plot(w[0] + 0.5,
         w[1] + 0.5,
         markers[y[i]],
         markeredgecolor = colors[y[i]],
         markerfacecolor = 'None',
         markersize = 10,
         markeredgewidth = 2)
    
show()

# Finding the frauds
#
# Unfortunately, minisom.py doesn't contain an inverse mapping function we can
# use to directly get the list of customers from the coordinates of winning
# nodes. But we can retrieve a dictionary, that contains all of the mappings
# from the winning nodes to the customers.
#
# Each key in the dictionary is the coordinates of a particular winning node.
# The value mapped to each key is a list containing the customers corresponding
# to the associated winning node. Each element in the list is a NumPy array
# containing the attributes of a particular customer. The first element in each
# NumPy array is the SCALED value of the customer ID, but we can use the
# inverse_transform() method to get the original customer ID.
mappings = som.win_map(X)

# Matrix of MID values
dist = som.distance_map().T

# Retrieve the winning nodes
winning_nodes = []
frauds = []
for i in range(10):
    for j in range(10):
        # If the MID of a node is very close to 1, it's a winning node, so add
        # it to the list
        if dist[i][j] > 0.95:
            winning_nodes.append((j, i))
            node_map = mappings[(j, i)]
            customers = sc.inverse_transform(node_map)
            print(j, i, customers)
            frauds.append(customers)

# frauds now contains the table of customers (with their attributes) who
# possibly cheated
frauds = np.concatenate(tuple(frauds))