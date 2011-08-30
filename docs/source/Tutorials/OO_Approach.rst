=============================================================
Tutorial: An Object Oriented Approach to Using SimPy
=============================================================

:Authors: K G Muller
:Date:  2010 April

.. highlight:: python
   :linenothreshold: 5 
   
Introduction
------------

Many simulation languages support a procedural modelling style. Using them,
problems are decomposed into procedures (functions, subroutines) and either
represented by general components, such as queues, or represented in code
with data structures.

There are fundamental problems with using the procedural style of
modelling and simulation. Procedures do not correspond to real world
components. Instead, they correspond to methods and algorithms. 
Mapping from the real (problem) world to the model and back is difficult
and not obvious, particularly for users expert in the problem domain, but
not in computer science. Perhaps the greatest limitation of the procedural 
style is the lack of model extensibility. The only way in this style
to change simulation models is through functional extension. One can
add structural functionality but not alter any of its basic processes.

SimPy, on the other hand, supports an **object oriented approach**
to simulation modelling.
In SimPy, models can be implemented as collections of autonomous,
cooperating objects.
These objects are self-sufficient and independent. The actions on these
objects are tied to the objects and their attributes. The object-oriented
capabilities of Python strongly support this encapsulation.

Why does this matter for simulation models? It helps with the mapping from
real-world objects and their activities to modelled objects and activities, 
and back. This not only reduces the complexity of the models, it also
makes for easier validation of models and interpretation of simulation
results in real world terms.

Object-oriented model implementation allows the development of libraries
of model components for specific real world domains. It also supports
the re-use and extension of models when model specifications change.

The most effective use of the object-oriented approach is an iteration
over Object Oriented Analysis, Object Oriented Design, and Object Oriented
Programming.

Simulation studies are typically performed to study systems to understand
the relationships between its components or to predict how the system
will perform in a changed environment. They are accomplished by building
a *model* of a system and experimenting with it.

In modelling, it is only necessary to consider aspects of the system
that affect the problems being investigated.

Identifying those aspects is rarely trivial and often requires trials with
a model and subsequent model refinement.

This short tutorial will attempt to show how this can be done for simulation 
modelling with SimPy. It is no comprehensive course on the object oriented 
approach, though. There are many publications on the web and also books 
teaching OO in general. 

Object Oriented Analysis
========================

The goal of OO analysis is to identify the scenary in which the system
to be modelled operates and the system components in terms of objects,
their attributes, actions and interactions.

A good start is to write a concise scenario description in natural
language and to look for terms which identify objects, attributes, etc.

Unfortunately, there is no algorithm for this, only heuristics. For english
language analysis, the article `Natural Language Analysis for Domain and Usage Models`_
gives a good introduction.

.. _Natural Language Analysis for Domain and Usage Models: http://www.educery.com/papers/rhetoric/analysis/ 

Here is a useful set of heuristics for mapping parts of speech to model
components:

========================  ========================  ========================

Part of speech            Model component           Examples

========================  ========================  ========================
Proper noun               Object                    Cashier
Common noun               Class                     Bank customer; clerk
Doing verb                Operation                 visit; withdraw money
Being verb                Inheritance               Is a clerk
Having verb               Aggregation               Has an account
Modal verb                Constraints               Clerk must be at counter
Adjective                 Attribute                 Number of clerks

========================  ========================  ========================

It is essential that the scenario description be done in the terms of the
user and/or the system domain.

Here are further useful heuristics for identifying objects:

*  recurring nouns (e.g. *transaction*)
*  real-world entities the model should include (e.g. *a customer*, *cashier*,
   *bank account*)
   
Model developers name and briefly describe the objects, their attributes, and their 
responsibilities as they are identified. Describing objetcs, even briefly, 
allows simulation modellers to clarify the concepts they use and avoid misunderstandings.
Initially, modellers need not, however, spend a lot of time detailing objects or 
attributes. They will be refined during the unavoidable iterations and 
revisions. At the end of the analysis process, this should result in a stable
and sufficiently detailed statement on objects and attributes. Such a statement
is esential for gathering simulation inputs from users and mapping simulation
results into real world terms.

Here is a very simple scenario description:

    A **bank** has a number of **counters** **staffed** by **clerks**. It also has 
    a number of **Automatic Teller Machines** (ATMs). During the bank's 
    **opening hours**, **customers** **visit** the bank at different **times**
    to **perform** one or more **transactions** requiring **service** by a bank clerk 
    at a counter or **use** of an **ATM**. All service by clerks is provided at counters.
    Counters can be **closed** and **unstaffed**. If the clerk or ATM they need is **busy**, they 
    **wait** for him/her/it 
    to become **available**. **After having performed all their transactions**, they **leave**
    the bank. The **waiting times** of the customers and the **load** on
    clerks and the ATMs should be estimated by using a simulation model.
    
The highlighted words and the scenario text suggest objects, attributes, 
operations and constraints:

**Objects**: bank, counters, clerks, customers, ATM, transactions, service

**Attributes**:

Of *bank*:
   counters, clerks, ATMs, opening hours
   
Of *customers*: 
   arrival times, transactions, waiting times, departure times
   
Of *counters*: 
   status(staffed, closed)
   
Of *clerks*: availability, load

Of *ATMs*: 
   availability, load
   
**Operations**:

By *customers*: 
   arrive, perform transaction, wait, leave

By *clerks*: 
   staff counter, provide service
By *ATM*: 
   provide service
   
**Constraints**: 
   
Counter service:
   if clerk available
ATM service: 
   if ATM available
Customer departure: 
   after having performed all transactions
Customer arrival: 
   if bank open
                 
It is highly unlikely that these initially identified objects, attributes etc. 
are either sufficient or all necessary for the intended simulation model. They
do provide a starting point, though, for seeking further details (e.g.
by interviews of staff with domain knowledge) and building a first rough 
object design.
                 
Object Oriented Design
========================

The next step is to develop an initial high-level object design from
the results from the OO analysis. This means that for each object identified, 
a class must be defined to which the object belongs, i.e. a generalization
of the object. The class encloses all the properties of an object, i.e.
attributes and operations. The attributes define all the data members
of an object. The behaviors define how the object interacts with
other objects and changes its own attributes.

This class modelling should be done even if there is only one object of this 
class in the scenario being modelled. It should be noted that the term *class*
here is not to be confused with the ``class`` construct in Python (and 
therefore SimPy). The class here is just the description of one or more
similar objects. It will 
become obvious in the following sections that the 
availability of ``class`` in Python, the implementation language being used
for SimPy models, is a great benefit. It allows clear, relatively simple 
mapping from the OO design to a SimPy program.

Class **Bank**:

Attributes:
   counters, clerks, ATMs, opening hours
Operations: 
   open, close
    
Class **Customer**:

Attributes: 
   arrival time, transactions, waiting time, departure time
Operations: 
   arrive, get service for a transaction, leave
    
Class **Counter**:

Attributes: 
   staffing(staffed, closed)
Operations: 
   open
    
Class **Clerk**:

Attributes: 
   availability (available, busy, absent)
Operations: 
   provide service, staff counter
    
Class **ATM**

Attributes: 
    availability(available, busy)
Operations: 
    provide service
    
Control object needed to set up simulation experiment:

Class **Model**:

Attributes: 
   model components, experiment data
Operations: 
   get experiment data, generate component objects, 
                run model, report results



Object Oriented Programming
===========================

Object Oriented Building of SimPy Simulation Models
----------------------------------------------------

Basic Recipe
============

* Describe the situation to be modelled in natural language.
* Identify the nouns and verbs as candidates for classes, objects
  and actions, respectively.


Model Components Provided By SimPy
==================================

User-Developed Components
===========================

SimPy Model Structure 
======================

Re-use of Components and Models
================================



Examples: The Bank World
=========================

Objects and Activities
**********************

Bank Model Components
*********************

Model 1: ....
**************

Model 2: ......
***************



