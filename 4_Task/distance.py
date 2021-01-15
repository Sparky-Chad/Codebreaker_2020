#!/usr/bin/env python3
acceleration = open('./stepinator.json').read().strip()[1:-1]
acceleration = [float(x) for x in acceleration.split(', ')]

# Getting values of velocity from this
velocity = []
for index in range(len(acceleration)):
    velocity.append(sum(acceleration[:index]))

# Find the distance values for each of the intervals
distance = []
for index in range(len(velocity)):
    distance.append(sum(velocity[:index]))

# because each block is a standard distance from each other of 100 we can
# predicte the distance of the blocks

blocks = []
minus_30= 0
for index in range(len(distance)):

    blocks.append((distance[index]+10)//100-minus_30)
    if index % 30 == 0: 
        minus_30 = (distance[index]+10)//100
 

data = list(zip(range(len(acceleration)), acceleration, velocity, distance, blocks))
print(data)
