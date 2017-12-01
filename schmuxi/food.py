import yaml
import random

with open("food.yml", "r") as foodfile:
    foodlist = yaml.load(foodfile)

one = 0
for key, value in foodlist["places"]:
    one += value

selected == False
result = ''

while selected == False:
    choice = random.choice(list(foodlist["places"]))
    random_value = random.random()
    if random_value > foodlist["places"][choice]/one:
        result = choice
        selected = True

print(result)

