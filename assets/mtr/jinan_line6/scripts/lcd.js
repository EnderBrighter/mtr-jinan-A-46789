/* JCM 2.3.0 / MTR 4.0.5. Coordinates in metres above car floor. */
var LCD={width:2048,height:336,singleRowMax:18,maxPerRow:18,refreshMillis:200,arrivalPageSeconds:6,animationSeconds:1.4,doorCycleSeconds:1.0,arrivalTolerance:6,stoppedSpeed:0.6,screenOffset:0.020,defaultColor:0x55b7d5,debug:false};
if(typeof SCRIPT_INPUT!=='undefined')Object.keys(LCD).forEach(function(k){if(SCRIPT_INPUT[k]!==undefined)LCD[k]=SCRIPT_INPUT[k];});
LCD.singleRowMax=Math.max(2,Math.min(24,Number(LCD.singleRowMax)));
LCD.maxPerRow=Math.max(2,Math.min(24,Number(LCD.maxPerRow)));
LCD.refreshMillis=Math.max(100,Number(LCD.refreshMillis));
LCD.arrivalPageSeconds=Math.max(2,Number(LCD.arrivalPageSeconds));
LCD.animationSeconds=Math.max(.4,Number(LCD.animationSeconds));
LCD.doorCycleSeconds=Math.max(.4,Number(LCD.doorCycleSeconds));
var AwtColor=java.awt.Color,AwtFont=java.awt.Font,INK=0x24313b,GREY=0xb7bbc2,RED=0xd8304c;
function list(a){var b=[];if(!a)return b;for(var i=0;i<a.size();i++)b.push(a.get(i));return b;}
function names(s){var a=String(s||'').split('|');return[a[0],a.slice(1).join(' / ')];}
function col(g,c){g.setColor(new AwtColor(Number(c)&0xffffff));}
function rect(g,x,y,w,h,c){col(g,c);g.fillRect(Math.round(x),Math.round(y),Math.round(w),Math.round(h));}
function text(g,s,x,y,size,c,max,bold){
 s=String(s||'');if(!s)return;g.setFont(new AwtFont('Microsoft YaHei',bold?1:0,size));col(g,c);
 var tr=g.getTransform(),w=g.getFontMetrics().stringWidth(s);g.translate(x,y);if(max&&w>max)g.scale(max/w,1);g.drawString(s,0,0);g.setTransform(tr);
}
function pair(g,s,x,y,size,c,max){var a=names(s);text(g,a[0],x,y,size,c,max,true);text(g,a[1],x,y+size*.65,Math.max(11,Math.round(size*.43)),c,max,false);}
function line(g,x1,y1,x2,y2,c,w){col(g,c);g.setStroke(new java.awt.BasicStroke(w,1,1));g.draw(new java.awt.geom.Line2D.Double(x1,y1,x2,y2));}
function circle(g,x,y,r,c){col(g,c);g.fill(new java.awt.geom.Ellipse2D.Double(x-r,y-r,r*2,r*2));}
function badge(g,s,x,y,c,w){rect(g,x,y,w,22,c);text(g,names(s)[0],x+5,y+17,15,0xffffff,w-10,true);}
function polygon(g,points,c){col(g,c);var p=new java.awt.geom.Path2D.Double();p.moveTo(points[0][0],points[0][1]);for(var i=1;i<points.length;i++)p.lineTo(points[i][0],points[i][1]);p.closePath();g.fill(p);}
function rounded(g,x,y,w,h,c,r){col(g,c);g.fill(new java.awt.geom.RoundRectangle2D.Double(x,y,w,h,r,r));}
function snapshot(v){
 var onRoute=v.isOnRoute(),raw=v.getThisRouteStops(),stops=list(raw),progress=v.getRailProgress(),next=Number(v.getNextStopIndex(raw,0.5)),nearest=-1,delta=Infinity;
 for(var i=0;i<stops.length;i++){var dist=Number(stops[i].distance);if(dist>=0&&Math.abs(dist-progress)<delta){delta=Math.abs(dist-progress);nearest=i;}}
 var arrived=Math.abs(v.getSpeedMs())<LCD.stoppedSpeed&&nearest>=0&&delta<=LCD.arrivalTolerance&&(v.getDoorValue()>0||v.getTotalDwellTime()>=0);
 var index=arrived?nearest:Math.max(0,Math.min(next,Math.max(0,stops.length-1))),current=stops[index],route=onRoute&&current?current.route:null;
 var data=stops.map(function(s,i){return{name:s.station?String(s.station.getName()):String(s.name||'站名加载中|Loading station'),color:s.route?Number(s.route.getColor()):Number(LCD.defaultColor),transfers:list(s.routeInterchanges).map(function(r){return{name:String(r.name),color:Number(r.color)};})};});
 return{stops:data,index:index,arrived:arrived,onRoute:onRoute,ready:v.isStopsDataFetched(),line:route?String(route.getName()):'',color:route?Number(route.getColor()):Number(LCD.defaultColor),origin:data.length?data[0].name:'',destination:current?String(current.destinationName||''):'',doorValue:Number(v.getDoorValue()),anim:Date.now()/1000,phase:Math.floor(Date.now()/1000/LCD.arrivalPageSeconds)%2,blink:Math.floor(Date.now()/1000)%2,reversed:v.isReversed()};
}
function doorKey(v,car,side,z){
 // Platform-query X is opposite the LCD render X in this vehicle coordinate convention.
 // Convert once here; JCM still applies each car rotation/reversal itself.
 var own=v.isDoorOpenable(car,new Vector3f(-side*1.45,0,z-.70),new Vector3f(-side*1.45,.1,z+.70));
 var other=v.isDoorOpenable(car,new Vector3f(side*1.45,0,z-.70),new Vector3f(side*1.45,.1,z+.70));
 return own?(other?'both':'this'):(other?'other':'unknown');
}
function mapWindow(n,index){var cap=n<=LCD.singleRowMax?LCD.singleRowMax:2*LCD.maxPerRow;var start=n<=cap?0:Math.max(0,Math.min(n-cap,index-Math.floor(cap/3)));return{start:start,end:Math.min(n,start+cap),rows:n<=LCD.singleRowMax?1:2};}
function header(g,d){
 rect(g,0,0,2048,70,d.color); // logo area intentionally blank
 pair(g,d.line||'线路信息|Route information',285,32,29,0xffffff,290);rect(g,610,0,810,70,0xf7f8fa);
 text(g,d.arrived?'到达站':'下一站',630,31,25,INK,140,true);text(g,d.arrived?'Arrived':'Next station',630,54,13,INK,140,false);
 pair(g,d.stops.length?d.stops[d.index].name:'等待线路数据|Waiting for route data',815,33,32,INK,575);pair(g,d.origin||'',1440,30,20,0xffffff,155);text(g,'›››',1605+5*((d.anim||0)%1),43,25,0xffffff,50,true);pair(g,d.destination,1665,30,20,0xffffff,160);
}
function routeMap(g,d,x,y,w,h,start,end,rows){
 rows=Number(rows);var n=end-start;if(n<1)return;var rc=rows===1?n:Math.ceil(n/2),margin=55,rightMargin=165,ys=rows===1?[y+47]:[y+31,y+h/2+22],pts=[];
 for(var j=0;j<n;j++){var row=Math.floor(j/rc),k=j%rc,count=Math.min(rc,n-row*rc);var xx=x+margin+(w-margin-rightMargin)*(rows===2&&row===1?1-k/Math.max(1,count-1):k/Math.max(1,count-1));pts.push([xx,ys[row],row]);}
 for(var j=1;j<n;j++){var a=pts[j-1],b=pts[j],i=start+j,c=i<=d.index?GREY:d.stops[i].color;
  if(a[2]===b[2]){line(g,a[0],a[1],b[0],b[1],c,9);var flow=i<=d.index?.5:(.15+.7*((d.anim||0)/LCD.animationSeconds%1));text(g,b[0]>a[0]?'»':'«',a[0]+(b[0]-a[0])*flow-7,b[1]+6,18,0xffffff,24,true);}
  else{var edge=x+w-25;line(g,a[0],a[1],edge,a[1],c,9);line(g,edge,a[1],edge,b[1],c,9);line(g,edge,b[1],b[0],b[1],c,9);}
 }
 for(var j=0;j<n;j++){var i=start+j,p=pts[j],s=d.stops[i],passed=i<d.index,c=passed?GREY:s.color;
  circle(g,p[0],p[1],10,c);circle(g,p[0],p[1],7,0xffffff);if(i===d.index){circle(g,p[0],p[1],12,RED);circle(g,p[0],p[1],8,d.blink?RED:0xffffff);}
  var tr=g.getTransform();g.translate(p[0]-5,p[1]+25);g.rotate(Math.PI/5);pair(g,s.name,0,0,rows===1?24:19,passed?GREY:(i===d.index?RED:INK),rows===1?160:123);g.setTransform(tr);
  var ts=s.transfers||[];if(ts.length){var r=ts[Math.floor(Date.now()/4000)%ts.length];badge(g,r.name,p[0]-32,p[1]-30,r.color,64);}
 }
 if(start>0)text(g,'‹ 前 '+start+' 站',x+5,y+h-5,15,INK,160,false);if(end<d.stops.length)text(g,'后 '+(d.stops.length-end)+' 站 ›',x+w-150,y+h-5,15,INK,145,false);return pts;
}
function doorAnimation(d,own){
 if(!own||!(d.doorValue>0))return 0;
 // Repeat a quick opening illustration while the real doors are opening/open.
 var t=((d.anim||0)/LCD.doorCycleSeconds)%1;return Math.min(1,t/.60);
}
function doorIcon(g,key,color,d){
 var own=key==='this'||key==='both',c=key==='unknown'?0x9ba3a7:(own?color:0x8d989f),opening=doorAnimation(d,own);
 // Flat reference-style door leaves, large windows and a restrained passenger pictogram.
 var gap=36*opening;

 for(var i=0;i<2;i++){var x=i===0?162-gap-79:162+gap;
  rounded(g,x,105,79,119,c,7);rect(g,i===0?x+74:x,105,5,119,c);rounded(g,x+7,113,65,43,0xf7f8fa,3);
  if(own&&d.doorValue>0){var shift=3*((d.anim||0)%1);var ax=x+39+(i===0?-shift:shift),sgn=i===0?-1:1;rect(g,ax-12,184,24,10,0xffffff);polygon(g,[[ax+sgn*20,189],[ax+sgn*6,179],[ax+sgn*6,199]],0xffffff);}
 }
 // Only the non-opening side carries a red prohibition pictogram.
 if(key==='other'){
  circle(g,162,166,32,0xf7f8fa);col(g,RED);g.setStroke(new java.awt.BasicStroke(8));g.draw(new java.awt.geom.Ellipse2D.Double(130,134,64,64));line(g,140,144,184,188,RED,8);
 }

 var labels={this:['本侧开门','Doors will open on this side'],other:['对侧开门','Doors will open on the other side'],both:['两侧开门','Doors will open on both sides'],unknown:['请留意开门方向','Check the platform side']};text(g,labels[key][0],36,267,32,INK,280,true);text(g,labels[key][1],36,292,15,INK,280,false);
}
function stationDiagram(g,d,carCount){
 // Flat planes and a single continuous train silhouette follow the supplied LCD reference.

 polygon(g,[[468,154],[516,135],[946,135],[897,154]],0xe1e4e6);
 polygon(g,[[468,154],[897,154],[897,162],[468,162]],0xcdd1d3);

 polygon(g,[[420,231],[488,193],[1000,193],[930,231]],d.color);
 // Minimal stair indications; no invented exit labels or station-specific geometry.
 for(var stair=0;stair<2;stair++){var sx=550+stair*270;polygon(g,[[sx,162],[sx+14,162],[sx+41,199],[sx+27,199]],0xf7f8fa);for(var j=0;j<7;j++)line(g,sx+j*4,164+j*5,sx+13+j*4,164+j*5,0x9ea7a9,1);}
 polygon(g,[[690,163],[706,163],[706,211],[690,211]],0xf7f8fa);
 var count=Math.max(1,carCount),left=464,right=943,y=239,h=39,cw=(right-left)/count;
 // Rounded/sloped cab ends, white car divisions and numbers, like the reference schematic.
 rounded(g,left-12,y,right-left+24,h,d.color,20);
 for(var i=1;i<count;i++)line(g,left+i*cw,y+3,left+i*cw,y+h-3,0xf7f8fa,1);
 for(var i=0;i<count;i++)text(g,String(i+1),left+(i+.5)*cw-7,y+28,23,0xffffff,Math.max(10,cw-10),false);
 for(var end=0;end<2;end++){var x=end===0?left-3:right-12;rect(g,x,y+9,6,10,0xffffff);rect(g,x+8,y+9,6,10,0xffffff);}
}
function paint(g,d,key,carCount){
 g.setRenderingHint(java.awt.RenderingHints.KEY_ANTIALIASING,java.awt.RenderingHints.VALUE_ANTIALIAS_ON);rect(g,0,0,2048,336,0xf7f8fa);header(g,d);
 if(!d.onRoute||!d.stops.length){text(g,d.onRoute?'正在获取线路与站点数据':'列车暂不载客',650,205,49,INK,1160,true);text(g,d.onRoute?'Loading route and station data':'Not in service',650,252,23,0x8c959c,1160,false);return;}
 if(d.arrived){doorIcon(g,key,d.color,d);stationDiagram(g,d,carCount);if(d.phase===0){pair(g,d.stops[d.index].name,1110,192,68,INK,880);var ts=d.stops[d.index].transfers;for(var i=0;i<Math.min(6,ts.length);i++)badge(g,ts[i].name,1110+i*145,276,ts[i].color,133);}else{var start=Math.max(0,Math.min(d.index-1,d.stops.length-6));routeMap(g,d,1060,104,965,206,start,Math.min(start+6,d.stops.length),1);}}
 else{var win=mapWindow(d.stops.length,d.index);routeMap(g,d,8,77,2032,251,win.start,win.end,win.rows);}
}
function create(ctx,state,v){state.textures={};state.carLabels={};state.labelColor=null;state.calls=[];state.lastUpdate=0;}
function screenCall(tex,side,z){
 function p(u,v){return new Vector3f(side*(1.245-.48*v-LCD.screenOffset),2.325+v,z+u);}
 var left=side>0?-.87:.87,right=-left;
 return QuadDrawCall.create('Jinan LCD').quad(p(left,.1425),p(left,-.1425),p(right,-.1425),p(right,.1425)).texture(tex.identifier).renderType('LIGHT');
}
function carLabelCall(tex,side,z){
 var left=side>0?-.87:.87,right=-left,u=left+(right-left)*1840/2048,bottom=.1425-.285*70/336;
 function p(u,v){return new Vector3f(side*(1.245-.48*v-LCD.screenOffset-.0005),2.325+v,z+u);}
 return QuadDrawCall.create('LCD car position').quad(p(u,.1425),p(u,bottom),p(right,bottom),p(right,.1425)).texture(tex.identifier).renderType('LIGHT');
}
function paintCarLabel(g,car,color){
 g.setRenderingHint(java.awt.RenderingHints.KEY_ANTIALIASING,java.awt.RenderingHints.VALUE_ANTIALIAS_ON);
 rect(g,0,0,208,70,color);rounded(g,26,12,166,46,0xf7f8fa,7);text(g,String(car+1)+'车',60,46,28,INK,122,true);}
function makeCarLabel(car,color){var tex=new GraphicsTexture(208,70);paintCarLabel(tex.graphics,car,color);tex.upload();return tex;}
function render(ctx,state,v){
 var now=Date.now();if(now-state.lastUpdate>=LCD.refreshMillis){state.lastUpdate=now;var d=snapshot(v),cars=ctx.getMyCars(),calls=[],used={};
  if(state.labelColor!==d.color){Object.keys(state.carLabels).forEach(function(k){state.carLabels[k].close();});state.carLabels={};state.labelColor=d.color;}
  for(var c=0;c<cars.length;c++){var car=Number(cars[c]);if(!state.carLabels[car])state.carLabels[car]=makeCarLabel(car,d.color);for(var side=-1;side<=1;side+=2)for(var z=-10;z<=10;z+=5){var key=d.arrived?doorKey(v,car,side,z):'unknown';used[key]=true;if(!state.textures[key])state.textures[key]=new GraphicsTexture(2048,336);calls.push({car:car,call:screenCall(state.textures[key],side,z)});calls.push({car:car,call:carLabelCall(state.carLabels[car],side,z)});}}
  Object.keys(used).forEach(function(key){var tex=state.textures[key];paint(tex.graphics,d,key,v.getCarCount());tex.upload();});state.calls=calls;if(LCD.debug){ctx.setDebugInfo('LCD',d);ctx.setDebugInfo('LCD texture',state.textures[Object.keys(used)[0]]);}
 }for(var i=0;i<state.calls.length;i++){var item=state.calls[i],rm=ctx.getCarRenderManager(item.car);if(rm)rm.draw(item.call);}
}
function dispose(ctx,state,v){Object.keys(state.textures||{}).forEach(function(k){state.textures[k].close();});Object.keys(state.carLabels||{}).forEach(function(k){state.carLabels[k].close();});state.calls=[];}
