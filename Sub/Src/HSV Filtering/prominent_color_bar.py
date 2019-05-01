import cv2
import numpy as np
import matplotlib.pyplot as plt
import colorsys
from sklearn.cluster import KMeans


def find_histogram(clt):
    """
        create a histogram with k clusters
        :param: clt
        :return: hist
        """
    numLabels = np.arange(0, len(np.unique(clt.labels_)) + 1)
    (hist, _) = np.histogram(clt.labels_, bins=numLabels)
    
    hist = hist.astype("float")
    hist /= hist.sum()
    return hist

def plot_colors2(hist, centroids):
    """
        Find most prominent color and plots bar chart of color clusters
        params- hist: pass histogram
                centroids: cluster centers
        return- bar chart and prints hsv value of most prominent color given rgb
        """
    bar = np.zeros((50, 300, 3), dtype="uint8")
    startX = 0
    lengthBar = {}
    for (percent, color) in zip(hist, centroids):
        # plot the relative percentage of each cluster
        endX = startX + (percent * 300)
        lengthBar[int(endX - startX)] =  color #Color score : color rgb
        cv2.rectangle(bar, (int(startX), 0), (int(endX), 50),
                      color.astype("uint8").tolist(), -1)
        startX = endX
    
    print(lengthBar)
    maxColor = max(lengthBar, key = int)
    r,g,b = lengthBar[maxColor]
    
    print("Max COLOR")
    print (maxColor)
    print(g)
    print(b)
    
    r = r/255
    g = g/255
    b = b/255
    h,s,_ = colorsys.rgb_to_hsv(r, g, b)
    v = max(r,g,b) #manually calculate Value b/c colorsys function gives weird V values
   
    print("HSV:")
    print(h)
    print(s)
    print(v)

    return bar     # return the bar chart


img = cv2.imread("bottle.jpg")
img = cv2.resize(img, (0,0), fx=0.5, fy=0.5)


cv2.rectangle(img, (225,220),(325,320),(0,0,255),1) #(x1,y1),(x2,y2)
cv2.imshow("image",img)
img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)


#y0:y1 , x0:x1
img = img[220:320,225:325] #Selext Range of Interest
img = img.reshape((img.shape[0] * img.shape[1],3)) #represent as row*column,channel number
clt = KMeans(n_clusters=3) #cluster number
clt.fit(img)

hist = find_histogram(clt)
bar = plot_colors2(hist, clt.cluster_centers_)

plt.axis("off")
plt.imshow(bar)
plt.show()
