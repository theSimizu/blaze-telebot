from time import sleep

def simple_generator(n):
    i = 0
    while True:
        yield i
        i += 1



my_simple_gen = simple_generator(3) #// Create a generator

for i in my_simple_gen:
    print(type(i))
    sleep(1)


# print(my_simple_gen)
# first_return = my_simple_gen. #// 0
# second_return = my_simple_gen.next() #// 1