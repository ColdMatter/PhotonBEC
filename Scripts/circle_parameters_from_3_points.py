#ipython --pylab
#execfile("circle_parameters_from_3_points.py")

#Takes three 2-tuples and returns radius
#Formula hoicked from Wikepedia http://en.wikipedia.org/wiki/Radius#Radius_from_three_points
def radius_from_three_points((x1,y1),(x2,y2),(x3,y3)):
	numer_squared_fac21 = (x2-x1)**2 + (y2-y1)**2
	numer_squared_fac32 = (x2-x3)**2 + (y2-y3)**2
	numer_squared_fac13 = (x3-x1)**2 + (y3-y1)**2
	numer_squared = numer_squared_fac13*numer_squared_fac32*numer_squared_fac21
	denom = 2.0*abs(  x1*y2 + x2*y3 + x3*y1 - x1*y3 - x2*y1 - x3*y2 )
	return (numer_squared**0.5) / denom
	
#Takes three 2-tuples and returns centre co-ords
#Formula hoicked from Wikepedia http://en.wikipedia.org/wiki/Circumscribed_circle#Cartesian_coordinates
def centre_from_three_points((Ax,Ay),(Bx,By),(Cx,Cy)):
	D = 2.0*( Ax*(By - Cy) + Bx*(Cy - Ay) + Cx*(Ay - By))
	Ux = ( (Ax**2 + Ay**2)*(By - Cy) + (Bx**2 + By**2)*(Cy - Ay) + (Cx**2 + Cy**2)*(Ay - By)  )/D
	Uy = ( (Ax**2 + Ay**2)*(Cx - Bx) + (Bx**2 + By**2)*(Ax - Cx) + (Cx**2 + Cy**2)*(Bx - Ax)) / D
	return Ux,Uy