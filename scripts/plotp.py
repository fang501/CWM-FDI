# !/usr/bin/python3
import numpy as np
import matplotlib.pyplot as plt


# parameters to modify 
filename="time_py.txt"
label='p'
xlabel = 'x'
ylabel = 'y'
title='p'
fig_name='p.png'
bins=100 #adjust the number of bins to your plot

## load data from input file
t = np.loadtxt(filename, delimiter=" ", dtype="float")

## if your data is "X Y" (2 cols), use the following line
#plt.plot(t[:,0], t[:,1], label=label)  # Plot some data on the (implicit) axes.

## if your data is "X" (1 col), use the following line
plt.plot(t, label=label)  # Plot some data on the (implicit) axes.

## comment the lines above and uncomment the line below to plot a simple CDF
#plt.hist(t[:], bins, density=True, histtype='step', cumulative=True, label=label)

## comment the lines above and uncomment the 4 lines below for a nicer CDF
#n = np.arange(1,len(t)+1) / float(len(t))
#ts = np.sort(t)
#fig, ax = plt.subplots()
#ax.step(ts,n)

plt.xlabel(xlabel)
plt.ylabel(ylabel)
plt.title(title)
plt.legend()
plt.savefig(fig_name)
plt.show()

## statistics 

# Calculate minimum value
pmin = np.min(t)
# Output:
print(pmin)  

# Calculate mean
pmean = np.mean(t)
# Output:
print(pmean)  

# Calculate median
pmedian = np.median(t)
# Output: 91.0
print(pmedian)  

# Calculate 90th percentile
p90 = np.percentile(t, 90)
# Output
print(p90)  

# Calculate 99th percentile
p99 = np.percentile(t, 99)
# Output
print(p99)  

# Calculate maximum
pmax = np.max(t)
# Output:
print(pmax)  
