import java.nio.file.*;
import java.io.*;
import org.mtr.libraries.de.javagl.obj.*;
public class CheckObj {
 public static void main(String[] args) throws Exception {
  for (String s:args) {
   Obj o=ObjReader.read(Files.newInputStream(Path.of(s)));
   Obj converted=ObjUtils.convertToRenderable(o);
   if(o.getNumFaces()==0||o.getNumGroups()==0)throw new IllegalStateException(s);
   for(int i=0;i<converted.getNumFaces();i++)if(converted.getFace(i).getNumVertices()!=3)throw new IllegalStateException("Non-triangle");
   System.out.println(s+": "+o.getNumGroups()+" groups; "+o.getNumFaces()+" triangles; parsed by MTR bundled javagl OBJ library");
  }
 }
}
