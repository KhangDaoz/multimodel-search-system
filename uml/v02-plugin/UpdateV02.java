package assignment;
import com.vp.plugin.*;
import com.vp.plugin.model.*;
import com.vp.plugin.diagram.*;
import java.io.*;
import java.util.*;
import com.vp.plugin.model.factory.*;
public class UpdateV02 implements VPPlugin, VPPluginCommandLineSupport {
 public void loaded(VPPluginInfo info) {} public void unloaded() {}
 public void invoke(String[] args) {
  try {
   ProjectManager pm=ApplicationManager.instance().getProjectManager();
   String[][] changes={{"submit(voice, transcript)","record / upload audio"},{"transcribe(audio_input)","transcribe_audio(bytes)"},{"text (simulated STT)","text (Vosk offline)"}};
   for(IModelElement m:pm.getProject().toAllLevelModelElementArray()) {
    if("record microphone / upload audio".equals(m.getName())) m.setName("record / upload audio");
    if("submit_audio(bytes) / transcribe_audio(bytes)".equals(m.getName())) m.setName("transcribe_audio(bytes)");
    if("recognized English text (Vosk offline)".equals(m.getName())) m.setName("text (Vosk offline)");
    if("SpeechService".equals(m.getName())) m.setDescription("V02: real encoded audio, FFmpeg mono PCM conversion, offline Vosk English recognition; transcript adapter is CLI-only.");
    if("QueryService".equals(m.getName())) m.setDescription("V02: common text/voice/image/multimodal dictionary, aliases, validated category/price/stock filters and text weight.");
    if("SearchService".equals(m.getName())) m.setDescription("V02: distinct candidate retrieval and ranking, normalized keyword score, cosine score, weighted text-image fusion, shared filters, customer-scoped order lookup.");

    for(String[] pair:changes) if(pair[0].equals(m.getName())) m.setName(pair[1]);
   }
   DiagramManager dm=ApplicationManager.instance().getDiagramManager();
   for(IDiagramUIModel diagram:pm.getProject().toDiagramArray()) {
    if(!"02 Three Layer Architecture".equals(diagram.getName())) continue;
    Map<String,IDiagramElement> components=new HashMap<>();
    for(IDiagramElement e:diagram.toDiagramElementArray()) {
     IModelElement m=e.getModelElement();
     if(m!=null && "Component".equals(m.getModelType())) components.put(m.getName(),e);
    }
    for(IDiagramElement e:diagram.toDiagramElementArray()) {
     IModelElement m=e.getModelElement();
     if(m!=null && "Dependency".equals(m.getModelType())) {diagram.removeDiagramElement(e);m.delete();}
    }
    String[][] edges={{"SearchUI","VoiceInput"},{"SearchUI","ImageUpload"},{"SearchUI","SearchResultView"},
     {"SearchUI","QueryService"},{"SearchUI","SpeechService"},{"SearchUI","ImageService"},{"SearchUI","SearchService"},
     {"SearchService","RankingService"},{"SearchService","ProductRepository"},{"SearchService","OrderRepository"},
     {"SearchService","VectorIndex"},{"ProductRepository","ProductDatabase"},{"OrderRepository","OrderDatabase"},{"ImageService","ImageStorage"}};
    for(String[] edge:edges) {
     IDiagramElement a=components.get(edge[0]),b=components.get(edge[1]);
     IDependency relationship=IModelElementFactory.instance().createDependency();
     relationship.setFrom(a.getModelElement());relationship.setTo(b.getModelElement());
     IDiagramElement connector=dm.createConnector(diagram,relationship,a,b,null);
     connector.setRequestResetCaption(true);connector.resetCaption();
    }
   }
   pm.getProject().setName("Assignment 06 V02 - Real Voice and Multimodal E-Commerce");
   for(IDiagramUIModel d:pm.getProject().toDiagramArray()) {
    for(IDiagramElement e:d.toDiagramElementArray()) {e.setRequestResetCaption(true);e.resetCaption();}
   }
   if(!pm.saveProjectAs(new File(args[0]))) throw new RuntimeException("Save failed");
   try(PrintWriter out=new PrintWriter(args[1])) {
    for(IDiagramUIModel d:pm.getProject().toDiagramArray()) {
     out.println(d.getName()+" | "+d.getType());
     for(IDiagramElement e:d.toDiagramElementArray()) if(e.getModelElement()!=null) out.println("  "+e.getModelElement().getModelType()+" | "+e.getModelElement().getName());
    }
   }
   System.out.println("V02_UPDATED");
  }catch(Exception e){throw new RuntimeException(e);}
 }
}
