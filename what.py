import numpy as np

def softmax(values):
    exp_values = np.exp(values - np.max(values))  # Subtracting the maximum value for numerical stability
    probabilities = exp_values / np.sum(exp_values)
    return probabilities

values = [-2.0, -1.0, -0.1, 1, 1.2, 1.5]
probabilities = softmax(values)

print("Original Values:", values)
print("Softmax Probabilities:", probabilities)