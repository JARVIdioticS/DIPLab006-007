import math
from os import name
import random
from PIL import Image
import numpy as np

import FrequencyDomainManager

class ImageManager:
    width = None
    height = None
    bitDepth = None

    img = None
    data = None
    original = None

    def read(self, fileName):
        global img 
        global data 
        global original 
        global width 
        global height 
        global bitDepth 
        img = Image.open(fileName)
        data = np.array(img)
        original = np.copy(data)
        width = data.shape[0]
        height = data.shape[1]

        mode_to_bpp = {"1":1,"L":8,"P":8,"RGB":24,"RGBA":32,"CMYK":32,"YCbCr":24,"LAB":24,"HSV":24,"I":32,"F":32}
        bitDepth = mode_to_bpp[img.mode]

        print("Image %s with %s x %s pixels (%s bits per pixels) has been read!" % (img.filename, width, height, bitDepth))

    def write(self, fileName):
        global img 
        img = Image.fromarray(data)
        try:
            img.save(fileName)
        except:
            print("Write file error")
        else:
            print("Image %s has been written!" %(fileName))

    def getFrequencyDomain(self):
        self.convertToGray()
        fft = FrequencyDomainManager(self)
        self.restoreToOriginal()
        return fft

    def convertToRed(self):
        global data
        for y in range(height):
            for x in range(width):
                data[x, y, 1] = 0
                data[x, y, 2] = 0

    def convertToGreen(self):
        global data
        for y in range(height):
            for x in range(width):
                data[x, y, 0] = 0
                data[x, y, 2] = 0

    def convertToBlue(self):
        global data
        for y in range(height):
            for x in range(width):
                data[x, y, 0] = 0
                data[x, y, 1] = 0

    def convertToGray(self):
        global data
        for y in range(height):
            for x in range(width):
                # matlab's (NTSC/PAL) implementation:
                R, G, B = data[x, y, 0], data[x, y, 1], data[x, y, 2]
                gray = 0.2989 * R + 0.5870 * G + 0.1140 * B # and somehow the magic happened
                data[x, y, 0], data[x, y, 1], data[x, y, 2] = gray, gray, gray

    def restoreToOriginal(self):
        global data
        data = np.copy(original)

    def adjustBrightness(self, brightness):
        global data
        for y in range(height):
            for x in range(width):
                r = data[x, y, 0]
                g = data[x, y, 1]
                b = data[x, y, 2]

                r = r + brightness
                r = 255 if r > 255 else r
                r = 0 if r < 0 else r

                g = g + brightness
                g = 255 if g > 255 else g
                g = 0 if g < 0 else g

                b = b + brightness
                b = 255 if b > 255 else b
                b = 0 if b < 0 else b

                data[x, y, 0] = r
                data[x, y, 1] = g
                data[x, y, 2] = b

    def invert(self):
        global data
        for y in range(height):
            for x in range(width):
                r = data[x, y, 0]
                g = data[x, y, 1]
                b = data[x, y, 2]

                r = 255 - r
                g = 255 - g
                b = 255 - b

                data[x, y, 0] = r
                data[x, y, 1] = g
                data[x, y, 2] = b

    def powerLaw(self, constant, gamma):
        global data
        for y in range(height):
            for x in range(width):
                r = data[x, y, 0] / 255.0
                g = data[x, y, 1] / 255.0
                b = data[x, y, 2] / 255.0

                r = (int)(255 * (constant * (math.pow(r, gamma))))
                r = 255 if r > 255 else r
                r = 0 if r < 0 else r

                g = (int)(255 * (constant * (math.pow(g, gamma))))
                g = 255 if g > 255 else g
                g = 0 if g < 0 else g

                b = (int)(255 * (constant * (math.pow(b, gamma))))
                b = 255 if b > 255 else b
                b = 0 if b < 0 else b

                data[x, y, 0] = r
                data[x, y, 1] = g
                data[x, y, 2] = b
        return

    def getGrayscaleHistogram(self):
        self.convertToGray()

        histogram = np.array([0] * 256)

        for y in range(height):
            for x in range(width):
                histogram[data[x, y, 0]] += 1

        self.restoreToOriginal()
        return histogram
            
    def writeHistogramToCSV(self, histogram, fileName):
        histogram.tofile(fileName,sep=',',format='%s')

    def getContrast(self):
        contrast = 0.0
        histogram = self.getGrayscaleHistogram()
        avgIntensity = 0.0
        pixelNum = width * height

        for i in range(len(histogram)):
            avgIntensity += histogram[i] * i

        avgIntensity /= pixelNum

        for y in range(height):
            for x in range(width):
                contrast += (data[x, y, 0] - avgIntensity) ** 2

        contrast = (contrast / pixelNum) ** 0.5

        return contrast
                
    def adjustContrast(self, contrast):
        global data
        currentContrast = self.getContrast()
        histogram = self.getGrayscaleHistogram()
        avgIntensity = 0.0
        pixelNum = width * height
        for i in range(len(histogram)):
            avgIntensity += histogram[i] * i

        avgIntensity /= pixelNum

        min = avgIntensity - currentContrast
        max = avgIntensity + currentContrast

        newMin = avgIntensity - currentContrast - contrast / 2
        newMax = avgIntensity + currentContrast + contrast / 2

        newMin = 0 if newMin < 0 else newMin
        newMax = 0 if newMax < 0 else newMax
        newMin = 255 if newMin > 255 else newMin
        newMax = 255 if newMax > 255 else newMax

        if (newMin > newMax):
            temp = newMax
            newMax = newMin
            newMin = temp

        contrastFactor = (newMax - newMin) / (max - min)

        for y in range(height):
            for x in range(width):
                r = data[x, y, 0]
                g = data[x, y, 1]
                b = data[x, y, 2]
                contrast += (data[x, y, 0] - avgIntensity) ** 2

                r = (int)((r - min) * contrastFactor + newMin)
                r = 255 if r > 255 else r
                r = 0 if r < 0 else r

                g = (int)((g - min) * contrastFactor + newMin)
                g = 255 if g > 255 else g
                g = 0 if g < 0 else g

                b = (int)((b - min) * contrastFactor + newMin)
                b = 255 if b > 255 else b
                b = 0 if b < 0 else b

                data[x, y, 0] = r
                data[x, y, 1] = g
                data[x, y, 2] = b

    def averagingFilter(self, size):
        global data
        if (size % 2 == 0):
            print("Size Invalid: must be odd number!")
            return
        
        data_zeropaded = np.zeros([width + int(size/2) * 2, height + int(size/2) * 2, 3])
        data_zeropaded[int(size/2):width + int(size/2), int(size/2):height + int(size/2), :] = data

        for y in range(int(size/2), int(size/2) + height):
            for x in range(int(size/2), int(size/2) + width):

                subData = data_zeropaded[x - int(size/2):x + int(size/2) + 1, y - int(size/2):y + int(size/2) + 1, :]

                avgRed = np.mean(subData[:,:,0:1])
                avgGreen = np.mean(subData[:,:,1:2])
                avgBlue = np.mean(subData[:,:,2:3])

                avgRed = 255 if avgRed > 255 else avgRed
                avgRed = 0 if avgRed < 0 else avgRed

                avgGreen = 255 if avgGreen > 255 else avgGreen
                avgGreen = 0 if avgGreen < 0 else avgGreen

                avgBlue = 255 if avgBlue > 255 else avgBlue
                avgBlue = 0 if avgBlue < 0 else avgBlue

                data[x - int(size/2), y - int(size/2), 0] = avgRed
                data[x - int(size/2), y - int(size/2), 1] = avgGreen
                data[x - int(size/2), y - int(size/2), 2] = avgBlue

    def gaussianBlurFilter(self, size, sigma):
        global data

        if size % 2 == 0:
            print("Size Invalid: must be odd number!")
            return

        k = int(size // 2)
        x, y = np.mgrid[-k:k+1, -k:k+1]
        gaussian_kernel = np.exp(-(x**2 + y**2) / (2 * sigma**2))
        gaussian_kernel /= gaussian_kernel.sum()

        data_zeropaded = np.zeros([width + k * 2, height + k * 2, 3])
        data_zeropaded[k:width + k, k:height + k, :] = data

        for y in range(k, k + height):
            for x in range(k, k + width):
                subData = data_zeropaded[x - k:x + k + 1, y - k:y + k + 1, :]
                
                red = np.sum(subData[:, :, 0] * gaussian_kernel)
                green = np.sum(subData[:, :, 1] * gaussian_kernel)
                blue = np.sum(subData[:, :, 2] * gaussian_kernel)

                data[x - k, y - k, 0] = min(max(red, 0), 255)
                data[x - k, y - k, 1] = min(max(green, 0), 255)
                data[x - k, y - k, 2] = min(max(blue, 0), 255)

    def medianFilter(self, size):
        global data

        if size % 2 == 0:
            print("Size Invalid: must be odd number!")
            return

        k = int(size // 2)
        data_zeropaded = np.zeros([width + k * 2, height + k * 2, 3])
        data_zeropaded[k:width + k, k:height + k, :] = data

        for y in range(k, k + height):
            for x in range(k, k + width):
                subData = data_zeropaded[x - k:x + k + 1, y - k:y + k + 1, :]

                medianRed = np.median(subData[:, :, 0])
                medianGreen = np.median(subData[:, :, 1])
                medianBlue = np.median(subData[:, :, 2])

                data[x - k, y - k, 0] = medianRed
                data[x - k, y - k, 1] = medianGreen
                data[x - k, y - k, 2] = medianBlue

    def laplacianFilter(self):
        global data
        laplacian_kernel = np.array([[0, -1, 0],
                                    [-1, 4, -1],
                                    [0, -1, 0]])

        data_zeropaded = np.zeros([width + 2, height + 2, 3])
        data_zeropaded[1:width + 1, 1:height + 1, :] = data

        for y in range(1, height + 1):
            for x in range(1, width + 1):
                subData = data_zeropaded[x - 1:x + 2, y - 1:y + 2, :]

                laplacianRed = np.sum(subData[:, :, 0] * laplacian_kernel)
                laplacianGreen = np.sum(subData[:, :, 1] * laplacian_kernel)
                laplacianBlue = np.sum(subData[:, :, 2] * laplacian_kernel)

                red = data[x - 1, y - 1, 0] - laplacianRed
                green = data[x - 1, y - 1, 1] - laplacianGreen
                blue = data[x - 1, y - 1, 2] - laplacianBlue

                data[x - 1, y - 1, 0] = min(max(red, 0), 255)
                data[x - 1, y - 1, 1] = min(max(green, 0), 255)
                data[x - 1, y - 1, 2] = min(max(blue, 0), 255)

    def addSaltNoise(self, percent):
        global data
        noOfPX = height * width
        noiseAdded = (int)(percent * noOfPX)
        whiteColor = 255
        for i in range(noiseAdded):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)

            data[x, y, 0] = whiteColor
            data[x, y, 1] = whiteColor
            data[x, y, 2] = whiteColor

    def addPepperNoise(self, percent):
        global data
        noOfPX = height * width
        noiseAdded = (int)(percent * noOfPX)
        blackColor = 0
        for i in range(noiseAdded):
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)

            data[x, y, 0] = blackColor
            data[x, y, 1] = blackColor
            data[x, y, 2] = blackColor

    def contraharmonicFilter(self, size, Q):
        global data
        if (size % 2 == 0):
            print("Size Invalid: must be odd number!")
            return
        
        data_temp = np.zeros([width, height, 3])
        data_temp = data.copy()

        for y in range(height):
            for x in range(width):

                sumRedAbove = 0
                sumGreenAbove = 0
                sumBlueAbove = 0
                sumRedBelow = 0
                sumGreenBelow = 0
                sumBlueBelow = 0

                subData = data_temp[x - int(size/2):x + int(size/2) + 1, y - int(size/2):y + int(size/2) + 1, :].copy()
                subData = subData ** (Q + 1)
                sumRedAbove = np.sum(subData[:,:,0:1], axis=None)
                sumGreenAbove = np.sum(subData[:,:,1:2], axis=None)
                sumBlueAbove = np.sum(subData[:,:,2:3], axis=None)

                subData = data_temp[x - int(size/2):x + int(size/2) + 1, y - int(size/2):y + int(size/2) + 1, :].copy()
                subData = subData ** Q
                sumRedBelow = np.sum(subData[:,:,0:1], axis=None)
                sumGreenBelow = np.sum(subData[:,:,1:2], axis=None)
                sumBlueBelow = np.sum(subData[:,:,2:3], axis=None)

                if (sumRedBelow != 0): sumRedAbove /= sumRedBelow
                sumRedAbove = 255 if sumRedAbove > 255 else sumRedAbove
                sumRedAbove = 0 if sumRedAbove < 0 else sumRedAbove
                if (math.isnan(sumRedAbove)): sumRedAbove = 0

                if (sumGreenBelow != 0): sumGreenAbove /= sumGreenBelow
                sumGreenAbove = 255 if sumGreenAbove > 255 else sumGreenAbove
                sumGreenAbove = 0 if sumGreenAbove < 0 else sumGreenAbove
                if (math.isnan(sumGreenAbove)): sumGreenAbove = 0

                if (sumBlueBelow != 0): sumBlueAbove /= sumBlueBelow
                sumBlueAbove = 255 if sumBlueAbove > 255 else sumBlueAbove
                sumBlueAbove = 0 if sumBlueAbove < 0 else sumBlueAbove
                if (math.isnan(sumBlueAbove)): sumBlueAbove = 0

                data[x, y, 0] = sumRedAbove
                data[x, y, 1] = sumGreenAbove
                data[x, y, 2] = sumBlueAbove

    # def alphaTrimmedFilter(self, size, d):
    #     global data
    #     if (size % 2 == 0):
    #         print("Size Invalid: must be odd number!")
    #         return

    #     data_zeropaded = np.zeros([width + int(size/2) * 2, height + int(size/2) * 2, 3])

    #     data_zeropaded[int(size/2):width + int(size/2), int(size/2):height + int(size/2), :] = data
    #     for y in range(height):
    #         for x in range(width):
    #             subData = data_zeropaded[x:x + size + 1, y:y + size + 1, :]
    #             sortedRed = np.sort(subData[:,:,0:1], axis=None)
    #             sortedGreen = np.sort(subData[:,:,1:2], axis=None)
    #             sortedBlue = np.sort(subData[:,:,2:3], axis=None)

    #             r = np.mean(sortedRed[int(d/2) : size * size - int(d/2)])
    #             r = min(max(0, r), 255)  

    #             g = np.mean(sortedGreen[int(d/2) : size * size - int(d/2)])
    #             g = min(max(0, g), 255)  

    #             b = np.mean(sortedBlue[int(d/2) : size * size - int(d/2)])
    #             b = min(max(0, b), 255)  
                
    #             data[x, y, 0] = r
    #             data[x, y, 1] = g
    #             data[x, y, 2] = b

    def alphaTrimmedFilter(self, size, d):
        global data

        # ตรวจสอบขนาดฟิลเตอร์
        if size % 2 == 0:
            print("Size Invalid: must be odd number!")
            return

        if d >= size * size:
            print("Invalid d: too large for given size!")
            return

        pad_size = size // 2
        data_zeropaded = np.zeros([width + 2 * pad_size, height + 2 * pad_size, 3])
        data_zeropaded[pad_size:width + pad_size, pad_size:height + pad_size, :] = data

        for y in range(height):
            for x in range(width):
                # ดึงค่าข้อมูลที่ต้องการ
                subData = data_zeropaded[x:x + size, y:y + size, :]

                # เรียงค่าพิกเซลในแต่ละช่องสี
                sortedRed = np.sort(subData[:, :, 0].flatten())
                sortedGreen = np.sort(subData[:, :, 1].flatten())
                sortedBlue = np.sort(subData[:, :, 2].flatten())

                # ตัดค่าที่ไม่ต้องการออกและคำนวณค่าเฉลี่ย
                r = np.mean(sortedRed[d//2 : -d//2])
                g = np.mean(sortedGreen[d//2 : -d//2])
                b = np.mean(sortedBlue[d//2 : -d//2])

                # ป้องกันไม่ให้ค่าเกินขอบเขต
                data[x, y, 0] = min(max(0, r), 255)
                data[x, y, 1] = min(max(0, g), 255)
                data[x, y, 2] = min(max(0, b), 255)


    def convertToRedBlue(self, cr, cg, cb):
        global data
        for y in range(height):
            for x in range(width):
                r = data[x, y, 0]
                g = data[x, y, 1]
                b = data[x, y, 2]

                if (r <= 10 and g <= 10 and b <= 10) or (r >= 245 and g >= 245 and b >= 245): continue

                r = min(255, r + cr)
                g = max(0, g + cg)
                b = min(255, b + cb)

                data[x, y, 0] = r
                data[x, y, 1] = g
                data[x, y, 2] = b
