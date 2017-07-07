"""
# Implementing (parts of) TensorFlow (almost) from Scratch
## A Walkthrough of Symbolic Differentiation
### Jim Fleming ([@jimmfleming](https://twitter.com/jimmfleming))

[main.py](main.html) |
[graph.py](graph.html) |
[tensor.py](tensor.html) |
[ops.py](ops.html) |
[session.py](session.html)

[Next: The Graph](graph.html)

This [literate programming](https://en.wikipedia.org/wiki/Literate_programming)
exercise will construct a simple 2-layer feed-forward neural network to compute
the [exclusive or](https://en.wikipedia.org/wiki/Exclusive_or), using [symbolic
differentiation](https://en.wikipedia.org/wiki/Automatic_differentiation) to
compute the gradients automatically. In total, about 500 lines of code,
including comments. The only functional dependency is numpy. I highly recommend
reading Chris Olah's [Calculus on Computational Graphs:
Backpropagation](http://colah.github.io/posts/2015-08-Backprop/) for more
background on what this code is doing.

The XOR task is convenient for a number of reasons: it's very fast to compute;
it is not linearly separable thus requiring at least two layers and making the
gradient calculation more interesting; it doesn't require more complicated
matrix-matrix features such as broadcasting.

> (I'm also working on a more involved example for MNIST but as soon as I added
support for matrix shapes and broadcasting the code ballooned by 5x and it was
no longer a simple example.)

Let's start by going over the architecture. We're going to use four main
components:

  - [`Graph`](graph.html), composed of `Tensor` nodes and `Op` nodes that
    together represent the computation we want to differentiate.
  - [`Tensor`](tensor.html) represents a value in the graph. Tensors keep a
    reference to the operation that produced it, if any.
  - [`BaseOp`](ops.html) represents a computation to perform and its
    differentiable components. Operations hold references to their input
    tensors and an output tensor.
  - [`Session`](session.html) is used to evaluate tensors in the graph.

**Note** the return from a graph operation is actually a tensor, representing
the output of the operation.
"""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import numpy as np
np.random.seed(67)

from tqdm import trange

from graph import Graph
from session import Session

def main():
    """
    The main method performs some setup then trains the model, displaying the
    current loss along the way.
    """

    # Define a new graph
    graph = Graph()

    # Initialize the training data (XOR truth table)
    X = graph.tensor(np.array([[0, 0], [0, 1], [1, 0], [1, 1]]))
    y = graph.tensor(np.array([[0, 1, 1, 0]]))

    # Initialize the model's parameters (weights for each layer)
    weights0 = graph.tensor(np.random.normal(size=(2, 4)))
    weights1 = graph.tensor(np.random.normal(size=(4, 1)))

    # Define the model's activations
    activations0 = graph.sigmoid(graph.dot(X, weights0))
    activations1 = graph.sigmoid(graph.dot(activations0, weights1))

    # Define operation for computing the loss
    # ([mean squared error](https://en.wikipedia.org/wiki/Mean_squared_error))
    loss_op = graph.mean(graph.square(graph.transpose(y) - activations1))

    # Define operations for the gradients w.r.t. the loss and an update
    # operation to apply the gradients to the model's parameters.
    parameters = [weights0, weights1]
    gradients = graph.gradients(loss_op, parameters)

    update_op = graph.group([
        graph.assign(param, param - grad) \
            for param, grad in zip(parameters, gradients)
    ])

    # Begin training... We iterate for a number of epochs, calling the session
    # run method each time to compute the update operation and the current
    # loss. The progress bar's description is updated to display the loss.
    sess = Session(graph)
    with trange(10000) as pbar_epoch:
        for _ in pbar_epoch:
            _, loss = sess.run([update_op, loss_op])
            pbar_epoch.set_description('loss: {:.8f}'.format(loss))

if __name__ == '__main__':
    main()
