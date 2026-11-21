import java.nio.file.*;
import com.lx862.mtrscripting.lib.org.mozilla.javascript.*;
public class LcdPreview {
 public static void main(String[] args)throws Exception{
  Context cx=Context.enter();try{cx.setLanguageVersion(Context.VERSION_ES6);Scriptable scope=cx.initStandardObjects();
   cx.evaluateString(scope,Files.readString(Path.of("assets/mtr/jinan_line4/scripts/lcd.js")),"lcd.js",1,null);
   cx.evaluateString(scope,Files.readString(Path.of("source/lcd_test.js")),"lcd_test.js",1,null);
  }finally{Context.exit();}
 }
}
