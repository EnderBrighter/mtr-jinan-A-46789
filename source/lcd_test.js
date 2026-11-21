function assert(a,msg){if(!a)throw new Error(msg);}
function jlist(a){var l=new java.util.ArrayList();a.forEach(function(x){l.add(x);});return l;}
var Vector3f=function(x,y,z){this.x=x;this.y=y;this.z=z;};
var fixtureNames=['第一医科大学|Shandong First Medical University','省会文化艺术中心|Culture and Arts Center','济南西站|Jinan West Railway Station','大杨|Dayang','腊山河公园|Lashanhe Park','腊山|Lashan','段店|Duandian','营市街|Yingshi Jie','南辛庄|Nanxinzhuang','五里牌坊|Wulipaifang','八一立交桥|Bayi Lijiaoqiao','山东体育中心|Shandong Sports Center','泉城公园|Quancheng Park','千佛山|Qianfoshan','山师东路|Shanshi East Road','山大路南口|Shanda South'];
function fixture(n){var a=[];for(var i=0;i<n;i++)a.push({name:fixtureNames[i%fixtureNames.length]+(i>=fixtureNames.length?' '+(i+1):''),color:i<22?0x67b943:0x7858ae,transfers:i%7===3?[{name:'2号线|Line 2',color:0xd6a947}]:[]});return{stops:a,index:7,arrived:false,onRoute:true,line:'4号线|Line 4',color:0x67b943,origin:fixtureNames[15],destination:fixtureNames[0],phase:0,blink:1};}
function output(d,key,file){var im=new java.awt.image.BufferedImage(2048,336,2),g=im.createGraphics();paint(g,d,key,6);g.translate(1840,0);paintCarLabel(g,2,d.color);g.dispose();javax.imageio.ImageIO.write(im,'png',new java.io.File('preview/'+file+'.png'));}
output(fixture(16),'unknown','lcd_running_16');output(fixture(36),'unknown','lcd_running_36');output(fixture(60),'unknown','lcd_running_60');
var d=fixture(36);d.arrived=true;d.doorValue=1;d.anim=.7;output(d,'this','lcd_arrived_this');d.doorValue=0;output(d,'this','lcd_arrived_this_closed');d.doorValue=1;output(d,'other','lcd_arrived_other');d.phase=1;output(d,'this','lcd_arrived_local');output(d,'both','lcd_arrived_both');output(d,'unknown','lcd_arrived_unknown');
var empty=fixture(0);output(empty,'unknown','lcd_loading');empty.onRoute=false;output(empty,'unknown','lcd_depot');
assert(mapWindow(18,2).rows===1,'18 stations');assert(mapWindow(19,2).rows===2,'19 stations');assert(mapWindow(36,20).end===36,'36 stations');var w=mapWindow(60,55);assert(w.start===24&&w.end===60,'60-station window');
var v={isDoorOpenable:function(car,a,b){return a.x>0;}};assert(doorKey(v,0,1,0)==='other','positive query X is opposite positive screen X');assert(doorKey(v,0,-1,0)==='this','positive query X is the negative screen side');v.isDoorOpenable=function(){return true;};assert(doorKey(v,0,1,0)==='both','both sides');v.isDoorOpenable=function(){return false;};assert(doorKey(v,0,1,0)==='unknown','no platform');
var stops=jlist([0,1,2].map(function(i){return{distance:100+i*100,station:{getName:function(){return '站 '+i;}},route:{getName:function(){return '4号线';},getColor:function(){return 0x67b943;}},routeInterchanges:jlist([]),destinationName:'终点'};}));
var progress=200,speed=0,door=1,dwell=30000;
v={getThisRouteStops:function(){return stops;},getRailProgress:function(){return progress;},getNextStopIndex:function(){return progress>200.5?2:1;},getSpeedMs:function(){return speed;},getDoorValue:function(){return door;},getTotalDwellTime:function(){return dwell;},isOnRoute:function(){return true;},isStopsDataFetched:function(){return true;},isReversed:function(){return false;}};
assert(snapshot(v).arrived&&snapshot(v).index===1,'arrived current station');door=0;assert(snapshot(v).arrived,'door-close dwell holds current');speed=3;progress=210;assert(!snapshot(v).arrived&&snapshot(v).index===2,'departure advances');speed=0;dwell=-1;assert(!snapshot(v).arrived,'signal stop is not arrival');
// Rendering lifecycle, 6 cars x 10 screens, cached draw calls remain submitted between texture updates.
var drawn=0,uploaded=0,closed=0;var GraphicsTexture=function(){this.graphics=new java.awt.image.BufferedImage(2048,336,2).createGraphics();this.identifier='mock';this.upload=function(){uploaded++;};this.close=function(){closed++;this.graphics.dispose();};};
var QuadDrawCall={create:function(){return{quad:function(a,b,c,d){assert((b.y-a.y)*(c.z-a.z)-(b.z-a.z)*(c.y-a.y)<0===a.x>0,'inward screen normal');return this;},texture:function(){return this;},renderType:function(){return this;}};}};
var ctx={getMyCars:function(){return[0,1,2,3,4,5];},getCarRenderManager:function(){return{draw:function(){drawn++;}};}};v.getCarCount=function(){return 6;};v.isDoorOpenable=function(car,a,b){return a.x>0;};var state={};create(ctx,state,v);render(ctx,state,v);assert(drawn===120&&uploaded===7,'shared running texture, all 60 screens');state.lastUpdate=Date.now();render(ctx,state,v);assert(drawn===240&&uploaded===7,'draw outside refresh limiter');dispose(ctx,state,v);assert(closed===7,'texture disposal');
java.lang.System.out.println('PASS: Rhino/AWT previews, thresholds, windowing, arrival/departure, door states, inward winding, lifecycle (60 LCDs)');

var testG=new java.awt.image.BufferedImage(2048,336,2).createGraphics();var positions=routeMap(testG,fixture(36),1060,104,965,206,6,12,1);assert(positions.length===6&&positions.every(function(p){return p[1]===positions[0][1];}),'arrival local map MUST remain one row on a 36-stop route');testG.dispose();

// Animated fixture preview: doorValue simulates the game-driven opening/closing timeline.
var frameDir=new java.io.File('preview/lcd_frames');frameDir.mkdirs();
for(var frame=0;frame<24;frame++){
 var run=fixture(36);run.anim=frame/5;var arrive=fixture(36);arrive.arrived=true;arrive.phase=1;arrive.anim=frame/5;arrive.doorValue=Math.max(0,Math.min(1,frame<12?frame/5:(23-frame)/5));
 var img=new java.awt.image.BufferedImage(2048,672,2),fg=img.createGraphics();paint(fg,run,'unknown',6);fg.translate(1840,0);paintCarLabel(fg,2,run.color);fg.translate(-1840,336);paint(fg,arrive,'this',6);fg.translate(1840,0);paintCarLabel(fg,2,arrive.color);fg.dispose();javax.imageio.ImageIO.write(img,'png',new java.io.File(frameDir,'frame_'+('00'+frame).slice(-2)+'.png'));
}

var savedText=text,numbers=[];text=function(g,s){if(/^\d+$/.test(String(s)))numbers.push(String(s));return savedText.apply(null,arguments);};
var countGraphics=new java.awt.image.BufferedImage(2048,336,2).createGraphics();stationDiagram(countGraphics,fixture(16),4);assert(numbers.join(',')==='1,2,3,4','four-car diagram follows live consist count');numbers=[];stationDiagram(countGraphics,fixture(16),8);assert(numbers.join(',')==='1,2,3,4,5,6,7,8','eight-car diagram follows live consist count');text=savedText;countGraphics.dispose();
java.lang.System.out.println('PASS: nearby map remains one row; 4/8-car schematic; animation frames generated');

// Both platform sides and the car-local mapping, including reversed consists.
for(var reversed=0;reversed<2;reversed++)for(var platformSide=-1;platformSide<=1;platformSide+=2){
 var queriedCars=[],mockDoor={isReversed:function(){return !!reversed;},isDoorOpenable:function(car,a,b){queriedCars.push(car);assert(a.z===4.3&&b.z===5.7,'doorway Z bounds retained');return a.x*platformSide>0;}};
 assert(doorKey(mockDoor,3,-platformSide,5)==='this','platform-facing LCD uses the converted X side');
 assert(doorKey(mockDoor,3,platformSide,5)==='other','opposite LCD stays closed');assert(queriedCars.every(function(c){return c===3;}),'per-car query retained');
}
function redDoorPixels(key){var img=new java.awt.image.BufferedImage(330,310,2),g=img.createGraphics();rect(g,0,0,330,310,0xf7f8fa);doorIcon(g,key,0x67b943,{doorValue:1,anim:0});g.dispose();var n=0;for(var y=110;y<220;y++)for(var x=125;x<200;x++){var c=img.getRGB(x,y)&0xffffff;if(((c>>16)&255)>150&&((c>>8)&255)<110&&(c&255)<130)n++;}return n;}
assert(redDoorPixels('this')===0,'no passenger/prohibition on opening side');assert(redDoorPixels('both')===0,'no passenger/prohibition when both sides open');assert(redDoorPixels('other')>300,'closed side has red prohibition icon');assert(redDoorPixels('unknown')===0,'unknown side makes no closed-side claim');
java.lang.System.out.println('PASS: corrected LCD/query X mapping on both sides; opening side clean; closed side red prohibition');

assert(doorAnimation({doorValue:0,anim:.4},true)===0,'real closed doors keep icon closed');assert(doorAnimation({doorValue:1,anim:.2},true)>0,'opening icon animates');assert(doorAnimation({doorValue:1,anim:1.2},true)<.5,'opening icon repeats after one second');assert(doorAnimation({doorValue:1,anim:.2},false)===0,'opposite-side doors remain closed');
var closedImage=new java.awt.image.BufferedImage(330,310,2),closedG=closedImage.createGraphics();rect(closedG,0,0,330,310,0xf7f8fa);doorIcon(closedG,'this',0x67b943,{doorValue:0,anim:.5});closedG.dispose();for(var yy=106;yy<223;yy++)assert((closedImage.getRGB(162,yy)&0xffffff)===0x67b943,'closed icon centre seam has no white gap');
var oldText=text,labelText=[];text=function(g,s){labelText.push(String(s));return oldText.apply(null,arguments);};var testLabel=makeCarLabel(3,0x67b943);assert(labelText.indexOf('4车')>=0,'actual carriage index is displayed');testLabel.close();labelText=[];var diagramG=new java.awt.image.BufferedImage(2048,336,2).createGraphics();stationDiagram(diagramG,fixture(16),6);diagramG.dispose();assert(!labelText.some(function(s){return s==='站台'||s==='站厅';}),'no hall/platform labels');text=oldText;
java.lang.System.out.println('PASS: fully closed icon, repeating one-second opening cycle, no platform labels and actual car badge');

// v13: missing route uses each vehicle family's configured identifier colour.
var savedDefaultColor=LCD.defaultColor;
[0xa5d431,0x55b7d5,0xc65054,0x8965ae,0xb69452].forEach(function(color){
 LCD.defaultColor=color;
 var defaultVehicle=Object.create(v);
 defaultVehicle.getThisRouteStops=function(){return jlist([]);};
 defaultVehicle.isOnRoute=function(){return false;};
 assert(snapshot(defaultVehicle).color===color,'no route: vehicle default colour');
 defaultVehicle.getThisRouteStops=function(){return stops;};
 assert(snapshot(defaultVehicle).color===color,'inactive stale route: vehicle default colour');
 defaultVehicle.isOnRoute=function(){return true;};
 assert(snapshot(defaultVehicle).color===0x67b943,'assigned route retains live route colour');
 defaultVehicle.getThisRouteStops=function(){return jlist([]);};
 assert(snapshot(defaultVehicle).color===color,'route loading: vehicle default colour');
 var d=snapshot(defaultVehicle),im=new java.awt.image.BufferedImage(2048,336,2),g=im.createGraphics();
 paint(g,d,'unknown',6);g.dispose();assert((im.getRGB(20,20)&0xffffff)===color,'LCD header paints default colour');
 var label=new java.awt.image.BufferedImage(208,70,2),lg=label.createGraphics();paintCarLabel(lg,0,color);lg.dispose();assert((label.getRGB(2,2)&0xffffff)===color,'car badge paints default colour');
});
LCD.defaultColor=savedDefaultColor;
java.lang.System.out.println('PASS: all 5 default colours; no route, stale route, loading, live route priority, painted header and car badge');
