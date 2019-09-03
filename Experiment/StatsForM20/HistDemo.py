import numpy as np
import matplotlib.pyplot as plt

mu = 5
sigma = 1

s = np.random.normal(mu, sigma, 1000)

count, bins = np.histogram(s, 100, normed=True)
pdf = 1/(sigma * np.sqrt(2 * np.pi)) * np.exp(- (bins - mu)**2 / (2 * sigma**2))

mu_ = 10
sigma_ = 1
s = np.random.normal(mu_, sigma_, 1000)

count_, bins_ = np.histogram(s, 100, normed=True)
pdf_ = 1/(sigma_ * np.sqrt(2 * np.pi)) * np.exp(- (bins_ - mu_)**2 / (2 * sigma_**2))

plt.plot(bins, pdf, linewidth=2, color='g')
plt.plot(bins_, pdf_, linewidth=2, color='r')

plt.show()

end=0