# Native Visual Paradigm project

Open Assignment06.vpp with Visual Paradigm 18.1 or newer. Three diagrams are saved inside the project:

1. 01 Use Case Model — native Actor, UseCase, Association and Generalization.
2. 02 Three Layer Architecture — native Package, Component and Dependency.
3. 03 Voice Search Sequence — VP's native InteractionDiagram (sequence) with lifelines and messages.

The PNG files were exported by Visual Paradigm from the saved project. The evaluation-edition watermark is retained. Source for the builder plugin is included for transparency; no plugin is required to open or edit the project. The application code and diagram names match the architecture.

Builder lifecycle: VP Open API creates models/shapes/connectors, resets captions, and saves through ProjectManager.saveProjectAs. Verification reopens the saved .vpp through VP and inventories diagram/model types; see ../results/vpp_verification.txt. The .vpp is a VP-generated binary project, not renamed XML or an image container.
