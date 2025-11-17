html = open("index.html", "r+", encoding='UTF-8')
text = html.read()


# first level processing; weeds out everything but what's in the tags
substring = "<!--xxx-->"
indices = []
start = 0
while True:
    index = text.find(substring, start)
    if index == -1:
        break
    indices.append(index)
    start = index + 1 # Start searching from the next position
print(indices) # Output: [0, 2, 4]


# second level processing: finds only the paths

temp_index = indices[0]
indices_2 = []

while temp_index < indices[1]:
    temp_temp_index = text.find("src", temp_index)
    if temp_temp_index == -1:
        break
    indices_2.append(temp_temp_index)
    temp_index = temp_temp_index + 1

print(indices_2) 
html.close() 
