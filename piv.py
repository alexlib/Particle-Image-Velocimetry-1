from PIL import Image
import math
#file or debugging data output 
out2 = open('out2.txt', 'w')


#Variable parameters for optimizing to best output
user_differenceOperationFactor	= 2
user_seedLengthFactor			= 3
user_maxIterationsFactor		= 3
user_boxSize					= 50

#Load 2 individual frames
im1, im2 = Image.open("a.bmp"), Image.open("b.bmp")


#Find 'difference' between two given images of same dimensions
#	adjustment 3 -> the difference is amplified using a squaring factor (in line 28)
#	a higher factor can be used for better amplification 

def difference(image1, image2):
	#*********************adjustment1************************

	factor = user_differenceOperationFactor
	if (image1.size[0]==image2.size[0]) and (image1.size[1]==image2.size[1]):
		cols, rows = image1.size[0], image1.size[1]
		difference = 0 
		for i in range(0,rows):
			for j in range(0,cols):	
				difference += abs( image1.getpixel((j,i)) - image2.getpixel((j,i)) ) ** factor
		return difference
	else:
		print('size mismatch for difference operation')

#Returns if a coordinate is Qualified for a square section search of length 'size' in 'image'
def isQual(image, coord, size):
	c,r = image.size[0], image.size[1]
	x,y = coord[0], coord[1]
	if c-x < size or r-y < size:
		return False
	else:
		return True

#Search for the Image 'seed' in the bigger image 'ground' 
#Search begins from the coordinate 'init_c' in 'ground'
def searchMatrix(seed, ground, init_c):
	# Adjust variable search_area in 
	# units of seed_length( box side length of image to find )
	# For example , here search area is 4 times the seed area
	# search_length is twice seed_length
	# The required threshold for difference in two given images.
 	
 	#print(seed.size)
	seed_length = seed.size[0]
	#*********************adjustment1************************
	search_length = 2 * user_seedLengthFactor
	#*********************adjustment2************************
	#	This adjustment is a function of the extend to which 
	#   particles are dispersed in the image
	itr_max = seed_length / user_maxIterationsFactor

	if isQual(ground, init_c, seed_length):
		subimage = ground.crop((init_c[0],init_c[1], init_c[0]+seed_length, init_c[1]+ seed_length))
		diff = difference(subimage, seed)
		itr = 2
		doneC = set([init_c])
		
		cdDB = {
			diff
			 : init_c
		}

		least_diff = diff

		while diff>0 :
		
			init_c = (init_c[0]-1, init_c[1]-1)
			for i in range(0,2*itr-2):
				for j in range(0,2*itr-2):
					newCoord = (init_c[0]+i ,init_c[1]+j)
					if isQual(ground, newCoord, seed_length) and not doneC.issuperset([newCoord]) and newCoord[0]>-1 and newCoord[1]>-1 :
						doneC.add(newCoord)
						subimage = ground.crop((newCoord[0], newCoord[1], newCoord[0]+ seed_length, newCoord[1] +seed_length))
						# O(n^2) operation
						diff = difference(subimage, seed)
						#Save each operation as a file for visual comparison
						#fdiff = open('op/'+ str(diff) +'_'+ str(newCoord[0])+'_' + str(newCoord[1])+'.bmp', 'w' )
						#subimage.save(fdiff)
						#Write data into textfile
						#out.write('newCoord '+ str(newCoord) + ' diff '+ str(diff) +'\n')
						#Check if this is the least diff and if so add this to DB 
						if diff  < least_diff : 
							least_diff = diff
							cdDB[least_diff] = newCoord
						#print(diff)
						if diff == 0:
							return newCoord
			
			itr+=1
			if itr==itr_max:
				return cdDB[least_diff]
	else:
		return 'dot' #'frames are same'


#im1, im2 = Image.open("source_images/a.bmp"), Image.open("source_images/b.bmp")
# Convert images into Luminance from RGB
frameA, frameB = im1.convert("L"), im2.convert("L")

cols = frameA.size[0]
rows = frameA.size[1]

#*********************adjustment4************************
boxSize	= user_boxSize

# verThreshold : vertical space in top and bottom to be ignored 
#				 as specified by the user (in pixels) 
# horThreshold : horizontal space in left and right to be ignored 
#				 as specified by the user
# Minimum value should be the box size 

verT = 50
horT = 50

#    The code auto-selects a region-of-interest which fits to the 
#size of box considering verticalThreshold and horizontalThreshold

# ++++++++++++++
# ++A++++++++B++
# ++++++++++++++
# ++C++++++++D++
# ++++++++++++++

A = (horT, verT)
B = ((cols - horT) - (cols - horT)%boxSize - 1 , verT)
C = (horT, (rows - verT) - (rows - verT)%boxSize -1 )
D = ((cols - horT) - (cols - horT)%boxSize - 1 , (rows - verT) - (rows - verT)%boxSize -1 )


# new image with size of parent image for arrow pattern display 
field = open('field.bmp', 'w')
arrow_img = Image.new( 'RGB', frameA.size)
# load arrow 
arrow = Image.open('arrow.png')
# resize arrow to boxSize
arrow = arrow.resize((boxSize,boxSize))

for i in range(1 , (B[0] - A[0] +1)/boxSize):
	for j in range(1, (D[1] - B[1] +1)/boxSize):
		center = (A[0] + (i*boxSize) - int(boxSize/2) , A[1] + (j*boxSize) - int(boxSize/2))
		
		ref_box = (center[0], center[1] ,  center[0]+boxSize-1, center[1]+boxSize-1)
		region  = frameA.crop(ref_box)
		aim = searchMatrix(region, frameB, center)
		if(str(aim) =='dot'):
			continue

		vector = (aim[0]-center[0], aim[1] - center[1])

		if vector[0]!=0 : 
			turn = math.atan(float(vector[1])/ float(vector[0]))
   		else:
   			turn = 1.5708
		alpha, beta = A[0] + i*boxSize, A[1]+ j*boxSize
	
		arrow_new = arrow.rotate(math.degrees(turn))
		out2.write( str(center) + '\t' + str(aim) + '\t'+ str(math.degrees(turn)) + '\t' + str(vector) +'\n' )
		print( str(center) + '\t' + str(aim) + '\t'+ str(math.degrees(turn)) + '\t' + str(vector) +'\n' )
		arrow_img.paste(arrow_new.convert('RGB') , (alpha, beta))

arrow_img.show()
arrow_img.save(field, 'BMP')