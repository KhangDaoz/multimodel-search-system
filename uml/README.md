# Native Visual Paradigm models — V02

Open `Assignment06.vpp` with Visual Paradigm 18.1+. The editable native project
contains the required use case, three-layer component and voice sequence diagrams.
`Assignment06_V01.vpp` preserves the original project.

The V02 sequence uses actual recorded/uploaded audio and offline Vosk recognized
text. Component descriptions document fusion, validated filters and real speech.
Combined text/image search uses the existing Search Product use case/services.
There are no required additional external actors for the local STT model.

`v02-plugin/UpdateV02.java` and `plugin.xml` are the actual VP Open API update
source used to edit and save the existing project without replacing its layout.
No plugin is required to open/edit the saved project. VP's own project save and
image-export tools produced the V02 artifacts; this is not renamed XML or an
image container. The native model inventory is in `../results/vpp_verification.txt`.
The report's use-case/architecture/voice-sequence PNGs are exported from V02.
