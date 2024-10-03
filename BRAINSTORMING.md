# atg-tools
 Internal web app built custom for ATG. This was initially inspired project to assist the QA department with building Checklists dynamically, making them easier to follow and properly complete, based on a specific platform. But after showing the possiblilties, I was asked to build some tools for other departments. The goal of this project is to integrate all the different departments needs in one application in order to create a useful workflow with less opportunity of human error between hand-offs as well as simplify the employees tasks.

 ## Phase 1: Inital development
 The initial development will start with QA department needs. This is because QA is the one that needs this tool the most. It will also likely be the most complex and difficult to get right. 
 
 Initial development will also require all of the foundational components to be developed, including but not limited to, user authentication with the Business' Slack account, any models that will be needed throughout the different applications, SMTP email notifications, and standard views and templates that will be required to login, logout, handle profile settings, create "QA checklists", "tasks", "components", and "products", as well as view and use the "QA checklists" to mark checklist tasks as "complete" and ready to ship. 

  ### Questions that need clarification
  1. At what point is a customer's product assigned a IRIS Number?
    - Answer:
  2. 

  ### Packages used
  This is a list of third-party packages that will be utilized during initial development
  - **Django** (the framework this app will be developed with)
  - **python-decouple** (used for better securing sensitive data as environment variables)
  - **psycopg[binary]** (used for the PostrgeSQL database I will be using)
  - **dj-database-url** (used to store the database credentials as a string)
  - **django-allauth[socialaccount]** (used to authenticate users with Slack)
  - **django-weasyprint** (used to download completed checklist forms as a PDF file)

 ## Phase 2: Wiki
 After QA app, there will be a push to develop a CMS for Support (*as well as other employees granted access*) to use in order to document how-to's and anything else to help employees accomplish their goals and responsibilites. This will be accomplished by using Wagtail (*which is a framework built on Django specifidcally for content management*).
  
  ### Packages used
  This is a list of all third-party packages added in "Phase 2"
  - **wagtail** (used to develop a CMS for the wiki much easier than doing it from scratch)

 ## Phase 3: Build department
 Once a working QA app and Wiki are developed, a tool will be made for the build team. This is still need more communication with management, however, one current process being discussed is the Checklist for receiving vehicles. 
 *TBD*

 ## Phase 4: Customer Training
 Need a tool for customers to fill a form out and sign. Need to discuss this further with management also.

 *Note*: Look into *signature_pad* JavaScript library for implementing a signature in a form

---

# Model Planning
*Note*: I'll be moving this to a Lucidchart diagram once things are finialized and I no longer need to brainstorm things.

After some brainstorming of other possible checklist needs, I'm in a state uncertain of the best route forward. Mainly with checklist model development. 

## Base models
These models will be stored in the base app for better usability throughout other parts of the project.

---

### **Customer Model**
- **Purpose**: Represents a customer or organization that purchases a product platform.

#### Fields:
1. **name** (*CharField*): The name of the customer or organization.
   - **Purpose**: Identifies the customer.

2. **address** (*CharField*): The shipping address that will be used to ship the platfom(s) once complete.
   - **Purpose**: Stores the shipping address for the specific customer (*this will not be used initially*)

3. **timezone** (*CharField* or *ChoiceField*): The customer's desired timezone
   - **Purpose**: Stores the timezone that will be used to set the time on cameras, software, etc.

4. **platforms** (*ForeignKey to Platform*): Links to the platforms owned by this customer.
   - **Purpose**: Tracks which platforms the customer owns.

---

### **Product Model**
- **Purpose**: Represents the overarching product line (e.g., Vehicle Surveillance System) and its general specifications, including generation.
  
#### Fields:
1. **name** (*CharField*): The name of the product line (e.g., Vehicle, Toolbox, etc.).
   - **Purpose**: Identifies the product line as a whole.
   
2. **generation** (*CharField* or *DecimalField*): Specifies the generation or version of the product (e.g., 1st Gen, 2nd Gen).
   - **Purpose**: Allows for tracking product updates or major changes across different iterations.

3. **description** (*CharField*): Links to a list of general component types that apply to this product.
   - **Purpose**: Stores which high-level component types (e.g., Cameras, GPS) are part of this product line.

---

### **Platform Model**
- **Purpose**: Represents specific instances of a product, such as a unit with its own unique IRIS number and customer-specific configurations.

#### Fields:
1. **iris_number** (*CharField*): A unique serial number or identifier for the specific platform (e.g., IRIS200).
   - **Purpose**: Used to track individual product units for internal and customer purposes.

2. **product** (*ForeignKey to Product*): Links the platform to a specific product line and generation.
   - **Purpose**: Establishes which product this platform belongs to, helping track general features and configurations.

3. **customer** (*ForeignKey to Customer*): Links the platform to the customer who owns it.
   - **Purpose**: Tracks customer ownership of the specific platform.

4. **components** (*ManyToManyField to Component*): Lists the specific components that are part of this platform.
   - **Purpose**: Allows for customization of components specific to this platform, depending on customer requirements or unit-specific features.

---

## QA Department models
These models will be used to store all the necessary parts of the QA departments application functionalities.

### **ComponentType Model**
- **Purpose**: Represents the high-level grouping of components, like "Cameras" or "GPS."

#### Fields:
1. **name** (*CharField*): The name of the component type (e.g., Cameras, GPS).
   - **Purpose**: Helps organize and group components by type for clarity and filtering purposes.

---

### **Component Model**
- **Purpose**: Represents individual components that make up a product platform, such as "Camera Model A" or "GPS Module B."

#### Fields:
1. **name** (*CharField*): The name of the specific component (e.g., Camera Model A).
   - **Purpose**: Identifies the specific component being used in the product.

2. **component_type** (*ForeignKey to ComponentType*): Links the component to its component type.
   - **Purpose**: Organizes components into higher-level categories like Cameras, GPS, etc.

3. **tasks** (*ManyToManyField to Task*): Lists tasks that are specific to this component.
   - **Purpose**: Allows you to define tasks or procedures for QA checks based on the component.

---

### **Task Model**
- **Purpose**: Represents the individual tasks and subtasks needed for the QA checklist. Tasks can be either parent or child (subtask).

#### Fields:
1. **name** (*CharField*): The description of the task (e.g., "Check VBMS settings").
   - **Purpose**: Describes what needs to be checked or done in QA.

2. **parent_task** (*ForeignKey to self*): Allows a task to have a parent task (creating the parent/child or task/subtask relationship).
   - **Purpose**: Establishes a hierarchy for tasks and subtasks, so subtasks can be nested under a parent task.

3. **component** (*ForeignKey to Component*): Links the task to a specific component.
   - **Purpose**: Ties the task to a particular component, ensuring that tasks are only applied to relevant platforms/components.

4. **product** (*ForeignKey to Product*): Links a task to all of their related products.
   - **Purpose**: Ties the task to all products that are assigned to the specific task.

5. **order** (*IntegerField*): Determines the order in which tasks should be displayed.
   - **Purpose**: Ensures that tasks and subtasks appear in a logical order on the checklist.

6. **is_subtask** (*BooleanField* or calculated*): Identifies if the task is a subtask.
   - **Purpose**: Helps differentiate between parent tasks and subtasks in the display logic.

---

### **Checklist Model**
- **Purpose**: Represents an instance of a QA checklist generated for a specific platform and customer, tracking task completion and notes.

#### Fields:
1. **platform** (*ForeignKey to Platform*): Links the checklist to a specific platform.
   - **Purpose**: Tracks which platform the checklist belongs to.

2. **customer** (*ForeignKey to Customer*): Links the checklist to a specific customer.
   - **Purpose**: Helps track checklists per customer for reference and historical data.

3. **tasks** (*ManyToManyField to ChecklistTask*): Contains all tasks that make up the checklist.
   - **Purpose**: Tracks the tasks needed to complete the checklist.

4. **created_on** (*DateField*): The date when the checklist was created.
   - **Purpose**: Allows tracking of when the QA process was started.

---

### **ChecklistTask Model**
- **Purpose**: Tracks the progress of individual tasks within a checklist, including completion status and notes.

#### Fields:
1. **checklist** (*ForeignKey to Checklist*): Links this task to a specific checklist.
   - **Purpose**: Establishes which checklist this task belongs to.

2. **task** (*ForeignKey to Task*): Links this instance of the task to the general task.
   - **Purpose**: Ties the task to the task definitions while allowing task instances to have separate statuses.

3. **status** (*CharField/ChoiceField*): Indicates whether the task is complete, incomplete, or failed.
   - **Purpose**: Tracks the progress of the task.

4. **notes** (*TextField*): Optional notes about the task, filled out by QA personnel.
   - **Purpose**: Stores observations, findings, or issues encountered while completing the task.

---

### **IssueResolution Model**
- **Purpose**: Tracks any issues found during the QA process and the resolution steps taken.

#### Fields:
1. **checklist** (*ForeignKey to Checklist*): Links the issue resolution to a specific checklist.
   - **Purpose**: Ensures that the issue is tied to the relevant checklist and platform.

2. **issue_description** (*TextField*): A description of the issue found.
   - **Purpose**: Stores details of the problem discovered during QA.

3. **resolution** (*TextField*): Details of the steps taken to resolve the issue.
   - **Purpose**: Records how the issue was resolved during the QA process.
