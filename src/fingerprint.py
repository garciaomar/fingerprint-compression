from PIL import Image
import glob
import os
import math

def compress(image):
    string = ""
    size = image.size
    breaks = 30
    vector = list()
    for x in range(breaks):
        vector.append(x * size[1] / breaks)

    for y in xrange(size[1]):
        count = 0
        if y not in vector:
            continue
        for x in xrange(size[0]):
            pixel = image.getpixel((x, y))[0]
            if x == 0:
                lastpixel = pixel
            if lastpixel != pixel and x > 0:
                if lastpixel == 255:
                    string += str(count) + "a,"
                else:
                    string += str(count) + "b,"
                count = 1
            if pixel == 255:
                count += 1
                lastpixel = 255
            else:
                count += 1
                lastpixel = 0
        string += str(count) + "a" if lastpixel == 255 else str(count) + "b"
        string += "\n"
    return string


def decompress(filepath):
    f = open(filepath, 'r')
    width = int(f.readline())
    height = int(f.readline())
    string = f.readline()
    image = Image.new('RGB', (width, height), 'white')

    add = 0
    for y in xrange(height):
        for x in xrange(width):
            if string[x + add] == 'a':
                pixel = 255
            else:
                pixel = 0
            image.putpixel((x, y), (pixel, pixel, pixel))
        add += width
    return image


def compare(image, directory):
    image = binary_threshold(image)
    string = compress(image)
    msg = ""
    results = dict()
    promedios = list()

    os.chdir(directory)
    for f in glob.glob("*.txt"):
        file_comparable = open(f, 'r')
        image_file, promedio = compare_files(image.size, string, file_comparable)
        promedios.append(promedio)
        results[str(promedio)] = image_file
        msg += f + " : " + str(min(150, promedio)) + "% \n"
    maximum = max(promedios)
    filename = results[str(maximum)]
    higher_match = find_absolute_path(filename)
    return higher_match, msg


def compare_files(image_size, string, f):
    image_file = f.readline() #skip first line
    image_file = image_file.split("\n")[0]
    width = int(f.readline())
    int(f.readline())  # skip line
    string1 = f.readlines()
    string2 = string.split("\n")
    promedio = 0
    for i in xrange(len(string1)):
        promedio += compare_lines(image_size[0], width, string2[i], string1[i])
    promedio /= 30.0
    return image_file, int(promedio * 100)


def compare_lines(width1, width2, line1, line2):
    vector1 = []
    suma1 = 0
    parse1 = line1.split(",")
    for p in parse1:
        if len(p) > 1:
            vector1.append((suma1 * 1.0 / width1, (suma1*1.0 + int(p[:-1]))/width1, p[-1]))
            suma1 += int(p[:-1])

    vector2 = []
    suma2 = 0
    parse2 = line2.split(",")
    for p in parse2:
        p = p.replace('\n', '')
        if len(p) > 1:
            vector2.append((suma2 * 1.0 / width2, (suma2*1.0 + int(p[:-1]))/width2, p[-1]))
            suma2 += int(p[:-1])

    vector_shared = []
    for v1 in vector1:
        for v2 in vector2:
            if shared(v1, v2):
                vector_shared.append(shared_cell(v1, v2))

    return porcentaje(vector_shared, vector1, vector2)


def porcentaje(c, v1, v2):
    suma = 0
    for t in c:
        suma += t[1] - t[0]
    x1 = max(len(v1[:len(v1)/2]), len(v2[:len(v2)/2]))
    t = (min(len(v1[:len(v1)/2]), len(v2[:len(v2)/2])) * 1.0 /  x1 if x1 > 0 else 1 * 1.0) / 2.0
    x2 = max(len(v1[len(v1)/2:len(v1)]), len(v2[len(v2)/2:len(v2)]))
    t += (min(len(v1[len(v1)/2:len(v1)]), len(v2[len(v2)/2:len(v2)])) * 1.0 /  x2 if x2 > 0 else 1 * 1.0) / 2.0
    suma *= (t ** 3)
    return suma if suma <= 1 else 1


def shared_cell(v1, v2):
    c = [max(v1[0], v2[0]), min(v1[1], v2[1])]
    return c


def shared(v1, v2):
    return not (v2[0] > v1[1] or v1[0] > v2[1] or v1[2] != v2[2])


def binary_threshold(image, thresh=128):
    if thresh > 1:
        thresh /= 255.0
    size = image.size
    x0 = image.size[0]
    x1 = 0
    y0 = image.size[1]
    y1 = 0
    for x in xrange(size[0]):
        for y in xrange(size[1]):
            pixel = image.getpixel((x, y))
            g = (pixel[0] + pixel[1] + pixel[2]) / 3
            if g < (255 * thresh):
                if x0 > x:
                    x0 = x
                if x1 < x:
                    x1 = x
                if y0 > y:
                    y0 = y
                if y1 < y:
                    y1 = y
                pixel = (0, 0, 0)
            else:
                pixel = (255, 255, 255)
            image.putpixel((x, y), pixel)

    image = image.crop((x0, y0, x1, y1))
    return image

def find_absolute_path(name):
    path_ = "/"
    for root, dirs, files in os.walk(path_):
        if name in files:
            return os.path.join(root, name)
