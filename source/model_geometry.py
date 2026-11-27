"""Photo-led Jinan Line 4 geometry. All dimensions metres, Z along carriage.
The 1.5 m end allocations include the cab and half connections; car pitch stays 25 m.
"""
import math

DOORS=(-10,-5,0,5,10)
DOOR_OPENING=1.5  # Visible aperture; the platform / interaction allocation remains 2 m.
PANEL_CENTRES=(-7.5,-2.5,2.5,7.5)
END=12.24
COVE_PROFILE=[(1.37,3.0),(1.26,3.22),(1.10,3.34),(.98,3.36),(.94,3.36),(.94,3.46),(1.18,3.46),(1.39,3.18),(1.39,3.0)]
LCD_HALF=1.025
LCD_JOIN_HALF=1.20

def build(Mesh,cab=False,panto=False):
 m=Mesh();b=m.box
 def poly(g,vs,c):m.poly(g,vs,c)
 def strip(g,points,w,c):
  # Ribbon lying in side plane; points are 3D, offset within YZ.
  for a,d in zip(points,points[1:]):
   dy,dz=d[1]-a[1],d[2]-a[2];length=math.hypot(dy,dz);oy,oz=-dz/length*w/2,dy/length*w/2
   poly(g,[(a[0],a[1]+oy,a[2]+oz),(d[0],d[1]+oy,d[2]+oz),(d[0],d[1]-oy,d[2]-oz),(a[0],a[1]-oy,a[2]-oz)],c)
 def section(g,points,z0,z1,c):
  # Mirrored profiles must still wind counter-clockwise before extrusion.
  if sum(a[0]*d[1]-d[0]*a[1] for a,d in zip(points,points[1:]+points[:1]))<0:points=list(reversed(points))
  for i in range(len(points)):
   a,d=points[i],points[(i+1)%len(points)];poly(g,[(a[0],a[1],z0),(d[0],d[1],z0),(d[0],d[1],z1),(a[0],a[1],z1)],c)
  poly(g,[(x,y,z0) for x,y in reversed(points)],c);poly(g,[(x,y,z1) for x,y in points],c)
 def rounded_patch(g,mapper,w,h,r,c,normal,depth=.009):
  import numpy as np
  pts=[]
  for u,v,start in [(w/2-r,h/2-r,0),(-w/2+r,h/2-r,90),(-w/2+r,-h/2+r,180),(w/2-r,-h/2+r,270)]:
   for k in range(6):
    a=math.radians(start+k*18);pts.append(mapper(u+r*math.cos(a),v+r*math.sin(a)))
  n=np.array(normal,dtype=float);n/=np.linalg.norm(n)
  pn=sum((np.cross(np.array(pts[i]),np.array(pts[(i+1)%len(pts)])) for i in range(len(pts))),np.zeros(3))
  if np.dot(pn,n)<0:pts.reverse()
  back=[tuple(np.array(v)-n*depth) for v in pts]
  poly(g,pts,c);poly(g,list(reversed(back)),c)
  for i in range(len(pts)):
   j=(i+1)%len(pts);poly(g,[pts[i],back[i],back[j],pts[j]],c)
 def round_side(g,side,z,y,l,h,r,c,x=1.483):
  pts=[]
  for zz,yy,start in [(z+l/2-r,y+h/2-r,0),(z-l/2+r,y+h/2-r,90),(z-l/2+r,y-h/2+r,180),(z+l/2-r,y-h/2+r,270)]:
   for k in range(5):
    t=math.radians(start+k*22.5);pts.append((side*x,yy+r*math.sin(t),zz+r*math.cos(t)))
  poly(g,pts,c)
 def outer_panel(side,z,ll):
  # Inner liner and outer sheet leave x=1.405..1.4675 free as an actual door pocket.
  for ya,yb,col in [(1.0,1.1875,'silver'),(1.1875,1.3125,'green'),(1.3125,1.80,'silver')]:
   b('shell',side*1.49,(ya+yb)/2,z,.02,yb-ya,ll,col)
 def side_window(side,z,l=2.54):
  # Four non-overlapping frame bars, rather than nested coplanar black boxes.
  for ya,yb in [(1.88,1.91),(2.89,3.0)]:b('shell',side*1.49,(ya+yb)/2,z,.02,yb-ya,3,'black')
  for dz in [-1.385,1.385]:b('shell',side*1.49,2.40,z+dz,.02,.98,.23,'black')
  round_side('window',side,z,2.40,l,.98,.10,'clear_glass',x=1.395)
  for zz in [z-l/2,z+l/2]:b('interior',side*1.353,2.40,zz,.035,1.05,.035,'steel')
  b('interior',side*1.353,1.88,z,.04,.035,l,'steel');b('interior',side*1.353,2.92,z,.04,.035,l,'steel')
 # Completely closed floor and roof envelopes at the car ends.
 floor_start=-11.0 if cab else -END
 b('interior',0,.945,(floor_start+END)/2,2.78,.11,END-floor_start,'floor')
 if cab:b('interior',0,.945,-11.70,2.40,.11,1.40,'floor')
 chassis_start=-11.0 if cab else -END
 b('shell',0,.79,(chassis_start+END)/2,2.81,.20,END-chassis_start,'silver')
 roof=[]
 for k in range(13):
  t=math.pi*k/24;roof.append((.95+.55*math.cos(t),3.075+.595*math.sin(t)))
 roof.extend([(.475,3.67),(0,3.67),(-.475,3.67)])
 for k in range(13):
  t=math.pi/2+math.pi*k/24;roof.append((-.95+.55*math.cos(t),3.075+.595*math.sin(t)))
 yy=3.1305;xx=.95+.55*math.sqrt(1-((yy-3.075)/.595)**2)
 roof.insert(1,(xx,yy));roof.insert(len(roof)-1,(-xx,yy))
 z0=-11.0 if cab else -END
 for a,d in zip(roof,roof[1:]):poly('shell',[(a[0],a[1],z0),(d[0],d[1],z0),(d[0],d[1],END),(a[0],a[1],END)],'green' if max(a[1],d[1])<=3.130501 else 'roof')
 ceiling_start=-11.0 if cab else -END
 b('interior',0,3.405,(ceiling_start+END)/2,2.02,.09,END-ceiling_start,'white')
 if cab:b('interior',0,3.14,-11.23,2.32,.08,.46,'white')
 for side in [-1,1]:
  # Raise the centre ceiling and leave a real opening in the cove at every LCD.
  spans=[];cursor=ceiling_start
  for dz in DOORS:
   left=max(ceiling_start,dz-LCD_JOIN_HALF);right=min(END,dz+LCD_JOIN_HALF)
   if left>cursor:spans.append((cursor,left))
   cursor=max(cursor,right)
  if cursor<END:spans.append((cursor,END))
  for za,zb in spans:
   section('interior',[(side*x,y) for x,y in COVE_PROFILE],za,zb,'white')
   b('interior',side*1.24,3.24,(za+zb)/2,.07,.012,zb-za,'steel')
   for lane in [-.018,.018]:b('interior',side*1.24+lane,3.23,(za+zb)/2,.008,.008,zb-za,'black')
  b('lights',side*.80,3.347,(ceiling_start+END)/2,.22,.016,END-ceiling_start-.04,'light')
  # Overhead rail and its short ceiling hangers.
  m.rod('interior',(side*.82,3.28,-10.95 if cab else -11.8),(side*.82,3.28,11.8),.018,'steel',10)
  for z in [-10,-5,0,5,10]:m.rod('interior',(side*.82,3.28,z),(side*.82,3.36,z),.017,'steel')
  # Side header stops exactly at cab start or car end. No old 0.4 m ceiling/side-wall gap.
  centre=(z0+END)/2;length=END-z0
  # Recess this strip 4 mm: lamp/base/strip must never share their outward plane.
  b('shell',side*1.489,3.02275,centre,.014,.0455,length,'silver')
  b('shell',side*1.493,3.06025,centre,.014,.0295,length,'green')
  b('interior',side*1.365,2.995,centre,.035,.13,length,'white')
  for z in PANEL_CENTRES:
   outer_panel(side,z,3)
   b('interior',side*1.353,1.42,z,.035,.84,3,'white')
   # Low sill extrusion and flush black belt around a single broad window.
   b('shell',side*1.49,1.84,z,.02,.08,3,'silver')
   side_window(side,z)
   # Continuous white moulding with six distinct inset coloured pads.
   shell=[(.69,1.44),(.69,1.49),(.72,1.505),(1.19,1.505),(1.25,1.56),(1.24,1.68),(1.32,1.99),(1.32,2.01),(1.35,1.99),(1.35,1.69),(1.31,1.52),(1.21,1.45),(.72,1.44)]
   section('seats',[(side*x,y) for x,y in shell],z-1.30,z+1.30,'white')
   for k in range(6):
    zz=z-1.075+k*.43;colour='yellow' if k==(5 if side<0 else 0) else 'seat'
    rounded_patch('seats',lambda u,v:(side*(.965+u),1.519+.01*u,zz+v),.43,.365,.05,colour,(-side*.01,1,0))
    rounded_patch('seats',lambda u,v:(side*(1.250+.206*v),1.79+v,zz+u),.365,.34,.045,colour,(-side,.206,0))
   b('seats',side*1.28,1.25,z,.13,.36,2.48,'rubber')
   for zz in [z-.9,z+.9]:b('seats',side*1.27,1.38,zz,.11,.14,.09,'steel')
   # Rounded rail at seat end, glazing windbreak and no pole in the doorway centre.
   for dz in [-1.34,1.34]:
    zz=z+dz
    path=[(side*.72,1.40,zz),(side*.69,1.65,zz),(side*.72,1.93,zz),(side*.85,2.12,zz),(side*1.15,2.20,zz),(side*1.34,2.20,zz)]
    for a,d in zip(path,path[1:]):m.rod('interior',a,d,.021,'steel',10)
    poly('window',[(side*.75,1.46,zz),(side*1.34,1.46,zz),(side*1.34,2.15,zz),(side*.88,2.08,zz),(side*.75,1.88,zz)],'clear_glass')
   # Reduced-scale triangular straps, softened corners represented by ten-sided tubes.
   for dz in [-.9,-.45,0,.45,.9]:
    zz=z+dz;m.rod('interior',(side*.82,3.28,zz),(side*.82,2.83,zz),.009,'rubber',6)
    pts=[(side*.82,2.83,zz),(side*.82-.075,2.68,zz),(side*.82-.065,2.655,zz),(side*.82+.065,2.655,zz),(side*.82+.075,2.68,zz),(side*.82,2.83,zz)]
    for a,d in zip(pts,pts[1:]):m.rod('interior',a,d,.012,'seat',8)
  for i,z in enumerate(DOORS):
   # Native moving leaf: geometry kept as cuboids for MTR's stable door path.
   for leaf in [-1,1]:
    g=f'door_{"l" if side<0 else "r"}_{i}_{"a" if leaf<0 else "b"}';zz=z+leaf*.50
    b(g,side*1.43625,1.10875,zz,.075,.2175,.984,'silver');b(g,side*1.43625,1.55125,zz,.075,.4575,.984,'silver')
    b(g,side*1.43625,1.27,zz,.075,.105,.984,'green')
    b(g,side*1.43625,2.89,zz,.075,.0666667,.984,'black')
    b(g,side*1.43625,2.9566667,zz,.075,.0666667,.984,'green')
    b(g,side*1.43625,1.83,zz,.075,.10,.984,'black')
    for dz in [-.441,.441]:b(g,side*1.43625,2.37,zz+dz,.075,1.0,.102,'black')
    b(g+'_glass',side*1.43625,2.37,zz,0,.98,.78,'glass')
    # Interior door skins are white; exterior silver/green/black stays on the outer face.
    b(g,side*1.402,1.39,zz,0,.78,.984,'white')
    b(g,side*1.402,2.925,zz,0,.15,.984,'white')
    for dz in [-.458,.458]:b(g,side*1.402,2.37,zz+dz,0,1.0,.068,'white')
    # Fine closing seals on both faces; native inflate retains sub-pixel widths.
    # The inward seal clears the fixed inner pocket lip even through full travel.
    for x in [1.473,1.4025]:b(g,side*x,2.01,z,0,1.98,0,'seal')
    b(g,side*1.474,1.75,z+leaf*.10,.005,.12,.026,'black')
    b(g,side*1.471,1.04,zz,.005,.04,.984,'steel')
   # Fill the unused quarter-metre on each side of the 2 m platform allocation.
   for dz in [-.875,.875]:
    outer_panel(side,z+dz,.25)
    b('shell',side*1.49,1.84,z+dz,.02,.08,.25,'silver')
    b('shell',side*1.49,2.44,z+dz,.02,1.12,.25,'black')
    b('interior',side*1.353,2.,z+dz,.035,2.,.25,'white')
   for dz in [-.768,.768]:b('interior',side*1.348,2.0,z+dz,.045,1.98,.032,'steel')
   # Inner and outer seals overlap the closed edge in projection, while leaving the pocket open.
   for dz in [-.749,.749]:
    b('interior',side*1.393,2.00,z+dz,.012,2.0,.075,'rubber')
    b('shell',side*1.491,2.00,z+dz,.012,2.0,.050,'rubber')
   # Fixed lower apron closes the space below the raised door; inner floor remains continuous.
   b('shell',side*1.49,1.09375,z,.02,.1875,1.5,'silver')
   b('interior',side*1.353,1.09375,z,.035,.1875,1.5,'white')
   b('interior',side*1.445,1.1825,z,.11,.01,1.49,'steel')
   # Inner cap terminates behind the external strip instead of at the same X=1.5 face.
   b('interior',side*1.425,3.11,z,.11,.03,2.07,'white')
   b('shell',side*1.49,3.0965,z,.02,.0675,1.5,'green')
   b('interior',side*1.365,3.0965,z,.035,.0675,1.5,'white')
   b('interior',side*1.34,1.1905,z,.10,.006,1.49,'yellow')
   # v12: no exterior door indicator or bezel.
   # A 1.84 x 0.34 m, downward-tilted LCD mounting opening, with a blank insert.
   # It is a separate mesh group so later LCD work can replace only this assembly.
   def lcd_point(u,v,offset=0):return (side*(1.245-.48*v-offset),3.325+v,z+u)
   def lcd_panel(w,h,c,offset):
    vs=[lcd_point(-w/2,-h/2,offset),lcd_point(w/2,-h/2,offset),lcd_point(w/2,h/2,offset),lcd_point(-w/2,h/2,offset)]
    if side<0:vs.reverse()
    # Face the passenger aisle; the back wall closes the cove opening.
    import numpy as np
    n=np.cross(np.array(vs[1])-vs[0],np.array(vs[2])-vs[0])
    if n[0]*side>0:vs.reverse()
    poly('lcd_mounts',vs,c)
   # One closed housing joins the screen face, ceiling, rear liner and BOTH end
   # caps. Its 2.05 m span exactly fills the matching cove opening above.
   housing=[(1.3626,3.08),(1.1274,3.57),(.98,3.57),(.98,3.36),(.94,3.36),(.94,3.60),(1.18,3.60),(1.39,3.39),(1.39,3.08)]
   # The raised housing and the lower cove must share their end profile.
   # One closed loft includes the housing and BOTH 175 mm transition cheeks.
   profiles=[(z-LCD_JOIN_HALF,COVE_PROFILE),(z-LCD_HALF,housing),(z+LCD_HALF,housing),(z+LCD_JOIN_HALF,COVE_PROFILE)]
   rings=[[(side*x,y,zz) for x,y in profile] for zz,profile in profiles]
   if sum(a[0]*d[1]-d[0]*a[1] for a,d in zip(rings[0],rings[0][1:]+rings[0][:1]))<0:rings=[list(reversed(ring)) for ring in rings]
   poly('lcd_mounts',list(reversed(rings[0])),'white')
   poly('lcd_mounts',rings[-1],'white')
   for first,last in zip(rings,rings[1:]):
    for i in range(len(first)):
     j=(i+1)%len(first)
     # Explicit triangles also handle the non-planar faces of a tapered loft.
     poly('lcd_mounts',[first[i],first[j],last[j]],'white')
     poly('lcd_mounts',[first[i],last[j],last[i]],'white')
   lcd_panel(1.87,.35,'black',.008)
   lcd_panel(1.74,.285,'screen',.016)
   for zz in [z-1.17,z+1.17]:
    m.rod('interior',(side*.73,1.02,zz),(side*.73,2.62,zz),.019,'steel',10)
    m.rod('interior',(side*.73,2.62,zz),(side*.82,3.28,zz),.019,'steel',10)
  # Closed full-height end side panels, with cabinet seams and interior colour.
  for end in [-1,1]:
   if cab and end<0:continue
   zz=end*(11+END)/2;ll=END-11
   outer_panel(side,zz,ll)
   b('shell',side*1.49,2.40,zz,.02,1.20,ll,'black')
   b('interior',side*1.353,2.0,zz,.035,2.0,ll,'white')
   b('interior',side*1.329,2.0,end*11.22,.004,1.90,.012,'steel')
 # Ring bulkhead + continuous floor, ceiling and corrugated inner bellows.
 for end in [-1,1]:
  if cab and end<0:continue
  ze=end*END
  for side in [-1,1]:
   b('shell',side*1.15,2.05,ze,.65,2.10,.10,'silver')
   b('interior',side*1.15,2.05,ze-end*.07,.62,2.10,.03,'white')
   b('interior',side*.815,2.07,ze-end*.085,.035,2.14,.025,'steel')
  b('shell',0,3.25,ze,2.88,.30,.10,'silver')
  m.poly('shell',[(x,y,ze) for x,y in roof],'roof')
  b('interior',0,3.10,ze-end*.065,1.66,.04,.03,'steel')
  b('interior',0,3.255,ze-end*.06,2.70,.23,.03,'white')
  # The whole last 0.26 m belongs to the prescribed 1.5 m end zone.
  b('interior',0,.982,end*12.37,1.64,.036,.26,'floor')
  b('interior',0,3.115,end*12.37,1.64,.06,.26,'white')
  for k in range(7):
   zz=end*(12.255+k*.037);w=.045 if k%2==0 else .03
   for side in [-1,1]:b('shell',side*.856,2.08,zz,w,2.15,.018,'rubber')
   b('shell',0,3.14,zz,1.75,.055,.018,'rubber')
  b('shell',0,.64,end*12.28,.30,.22,.44,'black')
  # visible end bellows flange and anti-climber, below passenger floor
  b('shell',0,.86,end*12.34,1.72,.08,.18,'steel')
 # Underframe: distinct converter, battery and brake housings with fasteners.
 for z,l in [(-5.7,2.3),(-2.2,2.6),(1.5,2.6),(5.4,2.4)]:
  b('shell',0,.49,z,2.16,.42,l,'black')
  for side in [-1,1]:
   b('shell',side*1.087,.50,z,.025,.32,l-.08,'roof')
   for dz in [-l/2+.12,l/2-.12]:
    b('shell',side*1.108,.50,z+dz,.012,.28,.025,'steel')
    for yy in [.40,.60]:m.rod('shell',(side*1.11,yy,z+dz),(side*1.12,yy,z+dz),.018,'steel',6)
   for dz in [-.65,-.43,-.21,.01,.23,.45,.67]:b('shell',side*1.105,.51,z+dz,.008,.16,.023,'black')
 m.rod('shell',(-.78,.73,-6.8),(-.78,.73,6.8),.026,'rubber',8)
 # HVAC units: bevelled casing, fan grilles and side louvers.
 for z in [-5.2,5.2]:
  casing=[(-1.02,3.63),(-1.02,3.76),(-.88,3.89),(.88,3.89),(1.02,3.76),(1.02,3.63)]
  section('shell',casing,z-1.65,z+1.65,'roof')
  for dz in [-.82,.82]:
   m.rod('shell',(0,3.895,z+dz),(0,3.903,z+dz),.54,'black',32)
   for k in range(13):
    xx=-.48+k*.08;half=math.sqrt(max(0,.48**2-xx**2));b('shell',xx,3.912,z+dz,.014,.012,2*half,'steel')
  for side in [-1,1]:
   for k in range(19):b('shell',side*1.021,3.745,z-1.40+k*.155,.008,.07,.035,'black')
 if panto:
  b('shell',0,3.73,8.3,1.1,.10,1.55,'steel')
  for x in [-.43,.43]:
   for z in [7.75,8.85]:m.rod('shell',(x,3.71,z),(x,3.93,z),.065,'white',10)
   m.rod('shell',(x,3.94,7.8),(x,4.45,8.65),.028,'black',10)
   m.rod('shell',(x,4.45,8.65),(x,4.98,7.85),.022,'steel',10)
  b('shell',0,4.99,7.85,1.66,.035,.16,'black')
  m.rod('shell',(-.48,3.93,8.2),(.48,3.93,8.2),.025,'steel',8)
 if cab:build_cab(m,roof,section,strip)
 return m

def _curve(y,points):
 slopes=[(points[i+1][1]-points[i][1])/(points[i+1][0]-points[i][0]) for i in range(len(points)-1)]
 tangents=[slopes[0]]+[0 if slopes[i-1]*slopes[i]<=0 else 2/(1/slopes[i-1]+1/slopes[i]) for i in range(1,len(points)-1)]+[slopes[-1]]
 if y<=points[0][0]:return points[0][1]
 for i,((a,x),(d,z)) in enumerate(zip(points,points[1:])):
  if y<=d:
   t=(y-a)/(d-a);h=d-a
   return (2*t**3-3*t**2+1)*x+(t**3-2*t**2+t)*h*tangents[i]+(-2*t**3+3*t**2)*z+(t**3-t**2)*h*tangents[i+1]
 return points[-1][1]

def cab_width(y):return _curve(y,[(1.,1.29),(1.3,1.40),(1.8,1.47),(2.5,1.47),(3.05,1.43),(3.30,1.37),(3.48,1.23),(3.60,1.00),(3.67,.65)])
def cab_rake(y):return _curve(y,[(1.,-12.37),(1.5,-12.40),(2.,-12.22),(2.5,-11.98),(3.18,-11.60),(3.48,-11.36),(3.60,-11.22),(3.67,-11.10)])
def cab_front(x,y):return (x,y,cab_rake(y)-.06*max(0,1-(x/cab_width(y))**2)*max(0,min(1,(3.67-y)/.27)))
def headsign_layout():return [('destination',-.84,3.115,.44,.125),('route',.84,3.115,.44,.125)]

def build_cab(m,roof,section,strip):
 """Photo-proportioned emergency door, curved mask, white cheeks and inner lining."""
 b=m.box;front=cab_front;wf=cab_width
 rr=sorted([(y,x) for x,y in roof if x>=.94])
 def bw(y):
  if y<=3.075:return 1.5
  for (a,x),(d,z) in zip(rr,rr[1:]):
   if a<=y<=d:return x+(z-x)*(y-a)/(d-a)
  return .95
 def fy(u,y):
  # Smile-shaped mask sill and a genuinely domed front crown, not a flat top plate.
  sill=.15*abs(u)**2*max(0,1-abs(y-1.80)/.36)
  dome=.065*abs(u)**6*max(0,1-abs(y-3.33)/.14)
  return y+sill-dome
 def fp(u,y,inner=False):
  yy=fy(u,y);x=u*wf(yy);v=front(x,yy)
  return (x-u*.10,yy-.025*max(0,(y-3.1)/.57),v[2]+.035) if inner else v
 def skin(vs,c,iv,inner='white'):
  if c=='glass':return  # Each glazing aperture receives one planar sheet below.
  m.poly('shell',vs,c)
  m.poly('interior',list(reversed(iv)),inner)
 ys=sorted(set(round(y,10) for y in [1.,1.1,1.2175,1.3225,1.5,1.65,1.8,1.88,1.93,2.02,2.10,2.12,2.16,2.5,2.7,2.95,2.97,3.,3.0455,3.075,3.1305,3.20,3.33,3.48,3.55,3.6,3.67]+[y for x,y in roof]))
 us=sorted(set([round(-1+i*.08,10) for i in range(26)]+[-1,-.94,-.91,-.47,-.38,-.25,0,.25,.38,.47,.91,.94,1]))
 for ya,yb in zip(ys,ys[1:]):
  ym=(ya+yb)/2
  for ua,ub in zip(us,us[1:]):
   um=(ua+ub)/2
   glass=(2.10<ym<2.97 and .47<abs(um)<.91) or (2.12<ym<2.97 and abs(um)<.25)
   c='glass' if glass else 'black' if (ym>1.80 and abs(um)<.94) or ym>3.55 else 'roof' if ym<1.80 and abs(um)<.38 else 'silver'
   order=[(ua,ya),(ua,yb),(ub,yb),(ub,ya)]
   skin([fp(u,y) for u,y in order],c,[fp(u,y,True) for u,y in order], 'black' if c=='black' and ym<3.20 else 'white')
 qs=[0,.12,.24,.36,.48,.60,.70,.76,.82,.90,1.,1.12,1.26,1.40]
 def wrap(side,y,q,inner=False):
  # A 0.75 m leaf retracts to -11.5, freeing 1 m for the real windscreen rake.
  corner=-11.525 if y<=3.01 else -11.525+.465*min(1,(y-3.01)/.64)
  yy=fy(1,y)+(y-fy(1,y))*min(1,q/1.4)
  if q<=1:
   a=q*math.pi/2
   x=side*(wf(fy(1,y))+(bw(y)-wf(fy(1,y)))*math.sin(a));z=cab_rake(fy(1,y))+(corner-cab_rake(fy(1,y)))*(1-math.cos(a))
  else:x=side*bw(y);z=corner+(q-1)/.4*(-11-corner)
  if inner:x-=side*(.10+.03*q/1.4);z+=.035*(1-q/1.4);yy-=.025*max(0,(y-3.1)/.57)
  return (x,yy,z)
 def side_q(y,q):
  # Move the cab side aperture and its green surround aft as one contour.
  # The lower leading edge stays ahead of the upper one, matching the sloped
  # side window in the supplied depot photo and leaving a solid silver A-pillar.
  f=max(0,min(1,(y-2.16)/.79))
  window_front=.98+.14*f
  frame_front=window_front-.14
  # Lean the green leading border with the raked nose rather than almost upright.
  # Keep the side glass where it was; only the painted surround changes.
  rake=cab_rake(fy(1,y))
  corner=-11.525 if y<=3.01 else -11.525+.465*min(1,(y-3.01)/.64)
  target=rake+.22
  if target<=corner:
   parallel_q=math.acos(max(-1,min(1,1-(target-rake)/(corner-rake))))/(math.pi/2)
  else:parallel_q=1+.4*(target-corner)/(-11-corner)
  frame_front=min(window_front-.10,.30*frame_front+.70*parallel_q)
  blend=min(max(0,(y-1.0)/.3225),max(0,min(1,(3.48-y)/.3495)))
  frame_front=.70+(frame_front-.70)*blend
  window_front=.82+(window_front-.82)*blend
  if q<=.70:return q/.70*frame_front
  if q<=.76:return frame_front+(q-.70)
  if q<=.82:return frame_front+.06+(q-.76)/.06*(window_front-frame_front-.06)
  return window_front+(q-.82)/.58*(1.40-window_front)
 def side_sample(side,y,q,inner=False):return wrap(side,y,side_q(y,q),inner)
 for side in [-1,1]:
  for ya,yb in zip(ys,ys[1:]):
   ym=(ya+yb)/2
   for qa,qb in zip(qs,qs[1:]):
    qm=(qa+qb)/2
    glass=2.16<ym<2.95 and .82<qm<1.40
    green=(qm>=.76 and (1.2175<ym<1.3225 or 3.0455<ym<3.1305)) or (.70<qm<.76 and 1.2175<ym<3.1305)
    c='green' if green else 'glass' if glass else 'black' if ym>3.45 and qm<.70 else 'roof' if ym>3.1305 else 'black' if qm>=.76 and 1.88<ym<3.0455 else 'silver'
    order=[(ya,qa),(yb,qa),(yb,qb),(ya,qb)]
    if side<0:order.reverse()
    skin([side_sample(side,y,q) for y,q in order],c,[side_sample(side,y,q,True) for y,q in order])
 # MTR uses EntityTranslucentCull: opposite windings on ONE plane show one surface
 # per viewing side. Avoid separate, finely tessellated inner/outer glazing skins.
 def pane(vs,axis):
  import numpy as np
  a=np.array(vs,dtype=float);keep=[k for k in range(3) if k!=axis]
  fit=np.linalg.lstsq(np.c_[a[:,keep],np.ones(len(a))],a[:,axis],rcond=None)[0]
  a[:,axis]=np.c_[a[:,keep],np.ones(len(a))]@fit
  points=[tuple(v) for v in a]
  m.poly('cab_glazing',points,'clear_glass');m.poly('cab_glazing',list(reversed(points)),'clear_glass')
 for ua,ub,ya,yb in [(-.91,-.47,2.10,2.97),(-.25,.25,2.12,2.97),(.47,.91,2.10,2.97)]:
  vs=[fp(ua,ya),fp(ua,yb),fp(ub,yb),fp(ub,ya)]
  pane([(x,y,z+.025) for x,y,z in vs],2)
 for side in [-1,1]:
  vs=[side_sample(side,y,q) for y,q in [(2.16,.82),(2.95,.82),(2.95,1.4),(2.16,1.4)]]
  if side<0:vs.reverse()
  pane([(x-side*.008,y,z) for x,y,z in vs],0)
 # Shared crown grid joins the curved front edge to the unchanged body cross-section.
 def crown(u,q,inner=False):
  a=fp(u,3.67,inner);edge=wrap(1 if u>=0 else -1,3.67,q,inner);f=q/1.4
  frontedge=fp(1,3.67,inner)
  yy=a[1]+(edge[1]-frontedge[1])*abs(u)**2+(3.67-(.025 if inner else 0)-a[1])*(1-abs(u)**2)*f
  zz=edge[2]+(a[2]-frontedge[2])*(1-f)
  xx=a[0]*(1-f)+u*(abs(edge[0])-abs(frontedge[0])*(1-f))
  return (xx,yy,zz)
 for qa,qb in zip(qs,qs[1:]):
  for ua,ub in zip(us,us[1:]):
   order=[(ua,qa),(ua,qb),(ub,qb),(ub,qa)]
   skin([crown(u,q) for u,q in order],'black' if qa<1.12 else 'roof',[crown(u,q,True) for u,q in order])
 # The centre escape door is a full-height tapered panel, with its actual window proportions.
 for u in [-.38,.38]:
  path=[fp(u,y) for y in [1.12,1.5,1.8,2.12,2.5,2.97,3.33]]
  for a,d in zip(path,path[1:]):m.rod('shell',(a[0],a[1],a[2]-.004),(d[0],d[1],d[2]-.004),.005,'rubber',6)
 for side in [-1,1]:
  for a,d in [((side*.96,2.31),(side*.72,2.72)),((side*.72,2.72),(side*.56,3.10))]:
   a=front(*a);d=front(*d);m.rod('shell',(a[0],a[1],a[2]-.014),(d[0],d[1],d[2]-.014),.008,'black',8)
  for x,w,c in [(side*1.20,.15,'light')]:
   v=front(x,3.115);b('shell',x,3.115,v[2]-.010,w+.025,.065,.012,'black')
   b('headlights',x,3.115,v[2]-.020,w,.038,.006,'light');b('tail_lights',x,3.115,v[2]-.020,w,.038,.006,'red');b('depot_lights',x,3.115,v[2]-.020,w,.038,.006,'red')
 # Recessed two-sided headsign housings; the actual text is supplied by native DISPLAY parts.
 for name,x,y,w,h in headsign_layout():
  vs=[front(x-w/2,y-h/2),front(x-w/2,y+h/2),front(x+w/2,y+h/2),front(x+w/2,y-h/2)]
  m.poly('shell',[(a,b,c-.009) for a,b,c in vs],'black')
 # Curved blade lamps, sampled along the same nose surface so housings do not cut into it.
 shape=[(.54,1.13),(.95,1.28),(1.23,1.50),(1.32,1.91),(1.09,1.86),(.97,1.56),(.80,1.36)]
 for side in [-1,1]:
  pts=[(side*x,y) for x,y in shape];cx=sum(x for x,y in pts)/len(pts);cy=sum(y for x,y in pts)/len(pts)
  for scale,offset,col in [(1.10,.008,'black'),(1.,.013,'steel'),(.82,.018,'roof')]:
   # Triangulate each contour in its XY plane, then subdivide onto the curved face.
   from mesh_topology import triangles
   xy=[(cx+(x-cx)*scale,cy+(y-cy)*scale,0) for x,y in pts]
   for tri in triangles(xy):
    a,d,e=[xy[k] for k in tri]
    def pt(i,j):
     xx=a[0]+(d[0]-a[0])*i/4+(e[0]-a[0])*j/4;yy=a[1]+(d[1]-a[1])*i/4+(e[1]-a[1])*j/4;v=front(xx,yy);return (xx,yy,v[2]-offset)
    for i in range(4):
     for j in range(4-i):
      vs=[pt(i,j),pt(i+1,j),pt(i,j+1)]
      if side>0:vs.reverse()
      m.poly('shell',vs,col)
      if i+j<3:
       vs=[pt(i+1,j),pt(i+1,j+1),pt(i,j+1)]
       if side>0:vs.reverse()
       m.poly('shell',vs,col)
  for trace in [[(.59,1.18),(.97,1.34),(1.19,1.54),(1.27,1.85)]]:
   for a,d in zip(trace,trace[1:]):
    pp=[front(side*(a[0]+(d[0]-a[0])*k/5),a[1]+(d[1]-a[1])*k/5) for k in range(6)]
    for v,t in zip(pp,pp[1:]):m.rod('headlights',(v[0],v[1],v[2]-.026),(t[0],t[1],t[2]-.026),.010,'light',8)
  for g in ['tail_lights','depot_lights']:
   pp=[front(side*x,y) for x,y in [(.56,1.16),(1.01,1.33),(1.25,1.54),(1.30,1.88)]]
   for a,d in zip(pp,pp[1:]):m.rod(g,(a[0],a[1],a[2]-.028),(d[0],d[1],d[2]-.028),.019,'red',10)
  # Three visible projector reflectors in each housing, seated on the nose tangent.
  import numpy as np
  for x,y in [(1.17,1.75),(1.10,1.60),(.99,1.43)]:
   x*=side;p=np.array(front(x,y));dx=(front(x+.001,y)[2]-front(x-.001,y)[2])/.002;dy=(front(x,y+.001)[2]-front(x,y-.001)[2])/.002
   n=np.array([dx,dy,-1.]);n/=np.linalg.norm(n)
   for offset,r,col in [(.023,.062,'black'),(.027,.052,'silver'),(.031,.027,'white')]:m.rod('shell',tuple(p+n*offset),tuple(p+n*(offset+.003)),r,col,16)
 # Rounded shoulder skirts and conspicuous dark coupler recesses below the silver bumper.
 for side in [-1,1]:
  skirt=[(side*.54,.57),(side*.95,.61),(side*1.24,.73),(side*1.42,.93),(side*1.45,.99),(side*.54,.99)]
  section('shell',skirt,-12.28,-11.02,'silver')
  rp=[]
  for xx,yy,start in [(side*.91+.36-.055,.90+.15-.055,0),(side*.91-.36+.055,.90+.15-.055,90),(side*.91-.36+.055,.90-.15+.055,180),(side*.91+.36-.055,.90-.15+.055,270)]:
   for k in range(6):
    a=math.radians(start+k*18);rp.append((xx+.055*math.cos(a),yy+.055*math.sin(a)))
  section('shell',rp,-12.445,-12.225,'black')
  for yy in [.82,.87,.92,.97]:b('shell',side*.96,yy,-12.452,.43,.013,.012,'steel')
 b('shell',0,1.095,-12.42,2.78,.10,.12,'silver')
 b('shell',0,.77,-12.20,.44,.28,.46,'black')
 b('shell',0,.78,-12.455,.43,.30,.065,'steel')
 for side in [-1,1]:
  m.rod('shell',(side*.105,.79,-12.489),(side*.105,.79,-12.491),.083,'black',16)
  m.rod('shell',(side*.105,.79,-12.492),(side*.105,.79,-12.494),.048,'steel',16)
  m.rod('shell',(side*.18,.64,-12.27),(side*.24,.54,-12.36),.022,'rubber',8)
 m.rod('shell',(-.11,.62,-12.30),(.12,.62,-12.30),.019,'yellow',8)
 # Cab compartment: closed floor, lined face, roof, desk and real glazing apertures.
 b('interior',0,1.25,-11.03,2.67,.50,.045,'white')
 for x in [-1.31,-.42,.42,1.31]:b('interior',x,2.30,-11.04,.025,1.62,.025,'steel')
 for x,w in [(-.87,.82),(0,.79),(.87,.82)]:b('window',x,2.30,-11.04,w,1.58,.012,'clear_glass')
 b('interior',0,3.10,-11.04,2.67,.05,.045,'white')
 b('interior',0,3.245,-11.03,2.67,.24,.045,'white')
 desk=[(-1.05,1.55),(-1.05,1.78),(-.75,1.89),(.75,1.89),(1.05,1.78),(1.05,1.55)]
 section('interior',desk,-11.97,-11.60,'steel')
 for x in [-.48,0,.48]:b('interior',x,1.90,-11.78,.31,.018,.18,'black');b('interior',x,1.912,-11.78,.24,.004,.11,'glass')
 # Transit emblem and small vehicle number; no fixed line-name or destination inscription.
 for x0,x1,y0,y1,uv in [(-.15,.15,1.72,1.99,[(272/1024,264/512),(272/1024,212/512),(220/1024,212/512),(220/1024,264/512)]),(-.28,.28,1.46,1.65,[(.125,268/512),(.125,210/512),(0,210/512),(0,268/512)])]:
  vs=[front(x0,y0),front(x0,y1),front(x1,y1),front(x1,y0)];m.poly('shell',[(x,y,z-.008) for x,y,z in vs],'white',uv)


def bogie(Mesh):
 m=Mesh();b=m.box
 b('bogie',0,.49,0,1.77,.20,2.65,'black')
 for side in [-1,1]:
  # longitudinal cast frame and axle boxes
  b('bogie',side*1.10,.49,0,.14,.22,2.73,'black')
  for z in [-.94,.94]:
   m.rod('bogie',(-1.16,.42,z),(1.16,.42,z),.072,'steel',12)
   m.rod('bogie',(side*.93,.42,z),(side*1.08,.42,z),.405,'rubber',24)
   m.rod('bogie',(side*.925,.42,z),(side*1.085,.42,z),.34,'steel',24)
   m.rod('bogie',(side*.92,.42,z),(side*1.09,.42,z),.22,'black',20)
   m.rod('bogie',(side*.915,.42,z),(side*1.095,.42,z),.09,'steel',12)
   b('bogie',side*1.14,.46,z,.16,.20,.24,'roof')
   b('bogie',side*.81,.43,z+.28,.16,.26,.12,'black')
  # secondary air spring and damper
  m.rod('bogie',(side*.64,.55,0),(side*.64,.74,0),.22,'rubber',16)
  m.rod('bogie',(side*.92,.48,-.40),(side*.99,.70,.12),.025,'steel',10)
  for z in [-.94,.94]:
   # small primary suspension coils, visually distinct from the wheel flanges
   for j in range(36):
    a=j*math.tau/12;d=(j+1)*math.tau/12
    m.rod('bogie',(side*1.13+.065*math.cos(a),.53+j*.004,z+.065*math.sin(a)),(side*1.13+.065*math.cos(d),.53+(j+1)*.004,z+.065*math.sin(d)),.008,'steel',5)
 return m
