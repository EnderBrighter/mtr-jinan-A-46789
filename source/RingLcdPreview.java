import java.nio.file.*;
import java.util.zip.*;
import com.lx862.mtrscripting.lib.org.mozilla.javascript.*;

/** Runs the existing LCD regression suite in isolation, then tests circular routes. */
public class RingLcdPreview {
 public static void main(String[] args)throws Exception {
  Path root=Path.of("").toAbsolutePath(),temp=Files.createTempDirectory("jinan-ring-lcd-");
  String before;
  try(ZipFile z=new ZipFile("source/archive/before_ring_pantograph.zip")) {
   before=new String(z.getInputStream(z.getEntry("assets/mtr/jinan_line4/scripts/lcd.js")).readAllBytes(),java.nio.charset.StandardCharsets.UTF_8);
  }
  String after=Files.readString(root.resolve("assets/mtr/jinan_line4/scripts/lcd.js"));
  for(String version:new String[]{"before","after"}) {
   Path out=temp.resolve(version);Files.createDirectories(out);
   String prefix=out.toString().replace('\\','/')+"/";
   Context cx=Context.enter();
   try {
    cx.setLanguageVersion(Context.VERSION_ES6);Scriptable scope=cx.initStandardObjects();
    cx.evaluateString(scope,version.equals("before")?before:after,"lcd.js",1,null);
    cx.evaluateString(scope,"Date.now=function(){return 1700000000000;};","clock",1,null);
    String tests=Files.readString(root.resolve("source/lcd_test.js")).replace("preview/",prefix);
    cx.evaluateString(scope,tests,"lcd_test.js",1,null);
    if(version.equals("after"))cx.evaluateString(scope,Files.readString(root.resolve("source/ring_lcd_test.js")),"ring_lcd_test.js",1,null);
   } finally {Context.exit();}
  }
  int compared=0;
  try(var files=Files.walk(temp.resolve("before"))) {
   for(Path p:files.filter(Files::isRegularFile).toList()) {
    Path q=temp.resolve("after").resolve(temp.resolve("before").relativize(p));
    if(Files.mismatch(p,q)!=-1)throw new AssertionError("Linear display changed: "+p);
    compared++;
   }
  }
  System.out.println("PASS: "+compared+" existing linear preview files byte-identical; isolated outputs: "+temp);
 }
}
