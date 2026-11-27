// Uses the fixtures and AWT context from lcd_test.js.
var ringMode='CLOCKWISE',ringStep=0,ringProgress=100,ringDoor=0,ringSpeed=3;
function ringStops(labels){return jlist(labels.map(function(name,i){return {
 distance:100+i*100,station:{getName:function(){return name;}},
 route:{getName:function(){return '测试环线|Test loop';},getColor:function(){return 0xa5d431;},getCircularState:function(){return ringMode;}},
 routeInterchanges:jlist([]),destinationName:'测试终点|Test terminal'
};}));}
var ringRaw=ringStops(['甲|A','乙|B','丙|C','丁|D','甲|A']);
var ringVehicle={getThisRouteStops:function(){return ringRaw;},getNextStopIndex:function(){return ringStep;},
 getRailProgress:function(){return ringProgress;},getSpeedMs:function(){return ringSpeed;},
 getDoorValue:function(){return ringDoor;},getTotalDwellTime:function(){return ringDoor?30000:-1;},
 isOnRoute:function(){return true;},isStopsDataFetched:function(){return true;},isReversed:function(){return false;}};
var rd=snapshot(ringVehicle);
assert(rd.circular&&rd.stops.length===4&&rd.direction==='顺时针|Clockwise','explicit clockwise route and duplicate endpoint');
ringStep=4;rd=snapshot(ringVehicle);assert(rd.index===0,'duplicate endpoint wraps to station zero');
ringProgress=500;ringDoor=1;ringSpeed=0;rd=snapshot(ringVehicle);
assert(rd.arrived&&rd.index===0&&rd.stops[rd.index].name==='甲|A','arrival at repeated final stop');
ringMode='ANTICLOCKWISE';assert(snapshot(ringVehicle).direction==='逆时针|Anticlockwise','anticlockwise API state');
ringMode='NONE';rd=snapshot(ringVehicle);assert(!rd.circular&&rd.stops.length===5&&rd.index===4,'linear repeated stops are not loops');
ringMode='unknown';assert(!snapshot(ringVehicle).circular,'unknown state remains linear');
ringMode='CLOCKWISE';
var oldLine=line,oldPair=pair,oldText=text,segments=[],labels=[],headerLabels=[];
line=function(g,x1,y1,x2,y2,c,w){segments.push([x1,y1,x2,y2]);return oldLine.apply(null,arguments);};
pair=function(g,s){labels.push(String(s));return oldPair.apply(null,arguments);};
text=function(g,s){headerLabels.push(String(s));return oldText.apply(null,arguments);};
var rg=new java.awt.image.BufferedImage(2048,336,2).createGraphics();
rd=snapshot(ringVehicle);rd.arrived=false;
var clockwise=routeMap(rg,rd,8,77,2032,251,0,4,2);
assert(segments.length===8,'four-node loop has two horizontal links and two three-part end joins');
assert(labels.join(',')==='甲|A,乙|B,丙|C,丁|D','each loop station shown exactly once');
rd.mode='ANTICLOCKWISE';segments=[];var anticlockwise=routeMap(rg,rd,8,77,2032,251,0,4,2);
assert(clockwise[0][0]<clockwise[1][0]&&anticlockwise[0][0]>anticlockwise[1][0],'map follows circular direction');
labels=[];var nearby=routeMap(rg,rd,1060,104,965,206,-1,3,1,true);
assert(labels.join(',')==='丁|D,甲|A,乙|B,丙|C','nearby map wraps across loop start');
assert(nearby.every(function(p){return p[1]===nearby[0][1];}),'nearby map retains one-row style');
headerLabels=[];header(rg,rd);assert(headerLabels.indexOf('测试终点')<0&&headerLabels.indexOf('顺时针')>=0,'header shows direction instead of false endpoint');
line=oldLine;pair=oldPair;text=oldText;rg.dispose();
new java.io.File('preview/ring_validation').mkdirs();
function ringOutput(d,name){var im=new java.awt.image.BufferedImage(2048,336,2),g=im.createGraphics();paint(g,d,'this',6);g.translate(1840,0);paintCarLabel(g,2,d.color);g.dispose();javax.imageio.ImageIO.write(im,'png',new java.io.File('preview/ring_validation/'+name+'.png'));}
var visual=fixture(16);visual.circular=true;visual.mode='CLOCKWISE';visual.direction='顺时针|Clockwise';visual.index=0;visual.anim=.4;visual.doorValue=1;
ringOutput(visual,'clockwise');visual.mode='ANTICLOCKWISE';visual.direction='逆时针|Anticlockwise';ringOutput(visual,'anticlockwise');
visual.arrived=true;visual.phase=1;ringOutput(visual,'arrived_wrap');
for(var count=1;count<=60;count++){
 var d=fixture(count);d.circular=true;d.mode='CLOCKWISE';d.direction='顺时针|Clockwise';d.index=count-1;
 var g=new java.awt.image.BufferedImage(2048,336,2).createGraphics();paint(g,d,'unknown',6);d.arrived=true;d.phase=1;paint(g,d,'this',6);g.dispose();
}
java.lang.System.out.println('PASS: circular API states, repeated endpoint arrival, linear repeats, closed geometry, mirrored direction, nearby wrap, 1–60 stations');
