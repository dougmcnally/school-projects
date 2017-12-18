# Stadium Billiards Problem
from __future__ import division
import math 

# initialize variables
r = 1
v0 = 1
alpha = 0.02
x0 = .1
y0 = - .1
theta0 = math.radians(56.5)
vx0 = v0*math.cos(theta0)
vy0 = v0*math.sin(theta0)
nstep = 30
xpos = list()
ypos = list()
vxs = list()
vys = list()
n = 1000
dt = 0.01
offset = int(1/dt)


def calculate(r,alpha,x0,y0,vx0,vy0,nstep):
   xlist = list()
   ylist = list()
   vxlist = list()
   vylist = list()
   xlist.append(x0)
   ylist.append(y0)
   vxlist.append(vx0)
   vylist.append(vy0)
   vx1 = vx0
   vy1 = vy0
   x1 = x0
   y1 = y0
   for i in range(1, nstep):
      if vy1>0:
         x = (r-y1)*vx1/vy1+x1
         if -alpha*r <= x and x <= alpha*r:
            y = r
            vx = vx1
            vy = -vy1
         elif x>alpha*r:
            a = 1+(vx1/vy1)**2
            b = 2*vx1/vy1*(x1-alpha*r-vx1/vy1*y1)
            c = (x1-alpha*r-vx1/vy1*y1)**2-r**2
            y = (-b+math.sqrt(b**2-4*a*c))/(2*a)
            x = math.sqrt(r**2-y**2)+alpha*r
            nx = (x-alpha*r)/math.sqrt((x-alpha*r)**2+y**2)
            ny = y/math.sqrt((x-alpha*r)**2+y**2)
            vperpx = (vx1*nx+vy1*ny)*nx
            vperpy = (vx1*nx+vy1*ny)*ny
            vparx = vx1-vperpx
            vpary = vy1-vperpy
            vx = vparx-vperpx
            vy = vpary-vperpy
         else:
            a = 1+(vx1/vy1)**2
            b = 2*vx1/vy1*(x1+alpha*r-vx1/vy1*y1)
            c = (x1+alpha*r-vx1/vy1*y1)**2-r**2
            y = (-b+math.sqrt(b**2-4*a*c))/(2*a)
            x = -math.sqrt(r**2-y**2)-alpha*r
            nx = (x+alpha*r)/math.sqrt((x+alpha*r)**2+y**2)
            ny = y/math.sqrt((x+alpha*r)**2+y**2)
            vperpx = (vx1*nx+vy1*ny)*nx
            vperpy = (vx1*nx+vy1*ny)*ny
            vparx = vx1-vperpx
            vpary = vy1-vperpy
            vx = vparx-vperpx
            vy = vpary-vperpy
      elif vy1<0:
         x = -(r+y1)*vx1/vy1+x1
         if -alpha*r <= x and x <= alpha*r:
            y = -r
            vx = vx1
            vy = -vy1
         elif x>alpha*r:
            a = 1+(vx1/vy1)**2
            b = 2*vx1/vy1*(x1-alpha*r-vx1/vy1*y1)
            c = (x1-alpha*r-vx1/vy1*y1)**2-r**2
            y = (-b-math.sqrt(b**2-4*a*c))/(2*a)
            x = math.sqrt(r**2-y**2)+alpha*r
            nx = (x-alpha*r)/math.sqrt((x-alpha*r)**2+y**2)
            ny = y/math.sqrt((x-alpha*r)**2+y**2)
            vperpx = (vx1*nx+vy1*ny)*nx
            vperpy = (vx1*nx+vy1*ny)*ny
            vparx = vx1-vperpx
            vpary = vy1-vperpy
            vx = vparx-vperpx
            vy = vpary-vperpy
         else:
            a = 1+(vx1/vy1)**2
            b = 2*vx1/vy1*(x1+alpha*r-vx1/vy1*y1)
            c = (x1+alpha*r-vx1/vy1*y1)**2-r**2
            y = (-b-math.sqrt(b**2-4*a*c))/(2*a)
            x = -math.sqrt(r**2-y**2)-alpha*r
            nx = (x+alpha*r)/math.sqrt((x+alpha*r)**2+y**2)
            ny = y/math.sqrt((x+alpha*r)**2+y**2)
            vperpx = (vx1*nx+vy1*ny)*nx
            vperpy = (vx1*nx+vy1*ny)*ny
            vparx = vx1-vperpx
            vpary = vy1-vperpy
            vx = vparx-vperpx
            vy = vpary-vperpy
      else:
         if vx1>0:
            y = y1
            x = alpha*r+math.sqrt(r**2-y1**2)
            nx = (x-alpha*r)/math.sqrt((x-alpha*r)**2+y**2)
            ny = y/math.sqrt((x-alpha*r)**2+y**2)
            vperpx = (vx1*nx+vy1*ny)*nx
            vperpy = (vx1*nx+vy1*ny)*ny
            vparx = vx1-vperpx
            vpary = vy1-vperpy
            vx = vparx-vperpx
            vy = vpary-vperpy   
         elif vx1<0:
            y = y1
            x = -alpha*r-math.sqrt(r**2-y1**2)
            nx = (x+alpha*r)/math.sqrt((x+alpha*r)**2+y**2)
            ny = y/math.sqrt((x+alpha*r)**2+y**2)
            vperpx = (vx1*nx+vy1*ny)*nx
            vperpy = (vx1*nx+vy1*ny)*ny
            vparx = vx1-vperpx
            vpary = vy1-vperpy
            vx = vparx-vperpx
            vy = vpary-vperpy
         else:
            print "billiard is stopped!"
      xlist.append(x)
      ylist.append(y)
      vxlist.append(vx)
      vylist.append(vy)
      x1 = x
      y1 = y
      vx1 = vx
      vy1 = vy
   return xlist, ylist, vxlist, vylist

for i in range(n):
    x,y,vx,vy = calculate(r, alpha, x0+1e-5*i, y0, vx0, vy0, nstep)
    xlist = list()
    ylist = list()
    for j in range(len(x)*offset):
        if j % offset == 0:
            q = int(j/offset)
            xlist.append(x[q])
            ylist.append(y[q])
            vxcur = vx[q]
            vycur = vy[q]
        else:
            xlist.append(xlist[j-1]+vxcur*dt)
            ylist.append(ylist[j-1]+vycur*dt)    
    xpos.append(xlist)
    ypos.append(ylist)
    vxs.append(vx)
    vys.append(vy)

separations = list()

for i in range(n-1):
    separations.append(list())
    for j in range(len(xpos[i])):
        separations[i].append(((xpos[i][j]-xpos[i+1][j])**2+(ypos[i][j]-ypos[i+1][j])**2)**0.5)
times = list()
for i in range(len(xpos[0])):
    times.append(i*dt)
separations_avg = separations[0]
for i in range(1, n-1):
    for j in range(len(separations_avg)):
        separations_avg[j] += separations[i][j]
for i in range(len(separations_avg)):
    separations_avg[i] /= n-1

import pylab

pylab.plot(times, separations_avg)
pylab.yscale('log')
pylab.xlabel("time")
pylab.ylabel("separation")
pylab.title("Stadium with alpha = 0.02 - Average separation of 1000 trajectories")
pylab.show()

pylab.plot(times, separations[1])
pylab.yscale('log')
pylab.xlabel("time")
pylab.ylabel("separation")
pylab.title("Stadium with alpha = 0.02 - Separation of 1 trajectory")
pylab.show()

#pylab.plot(times, separations[10])
#pylab.yscale('log')
#pylab.show()


##x1, y1, vx1, vy1 = calculate(r, alpha, x0, y0, vx0, vy0, nstep)
##x2, y2, vx2, vy2 = calculate(r, alpha, x0-1e-5, y0, vx0, vy0, nstep)
##
##xpos1 = list()
##xpos2 = list()
##ypos1 = list()
##ypos2 = list()
##dt = 0.01
##offset = int(1/dt)
##for i in range(len(x1)*offset):
##    if i % offset == 0:
##        j = int(i/offset)
##        xpos1.append(x1[j])
##        ypos1.append(y1[j])
##        xpos2.append(x2[j])
##        ypos2.append(y2[j])
##        vx_1 = vx1[j]
##        vy_1 = vy1[j]
##        vx_2 = vx2[j]
##        vy_2 = vy2[j]
##    else:
##        xpos1.append(xpos1[i-1]+vx_1*dt)
##        ypos1.append(ypos1[i-1]+vy_1*dt)
##        xpos2.append(xpos2[i-1]+vx_2*dt)
##        ypos2.append(ypos2[i-1]+vy_2*dt)
##
##import pylab
##pylab.scatter(xpos1, ypos1)
##pylab.show()
##
##
##separation = list()
##times = list()
##
##for i in range(len(xpos1)):
##    separation.append(((xpos1[i]-xpos2[i])**2+(ypos1[i]-ypos2[i])**2)**.5)
##    times.append(dt*i)
##
##pylab.plot(times, separation)
##pylab.yscale('log')
##pylab.show()
##
##xtot = xpos1+xpos2
##ytot = ypos1+ypos2
##
##for i in range(len(xpos1)):
##    separation[i] = ((xtot[i]/2)**2+(ytot[i]/2)**2)**.5
##pylab.plot(times, separation)
##pylab.yscale('log')
##pylab.show()
